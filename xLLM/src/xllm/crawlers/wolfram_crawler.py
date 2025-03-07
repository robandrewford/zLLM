"""Wolfram Alpha crawler implementation."""

import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import requests

from xllm.crawlers.base import BaseCrawler

logger = logging.getLogger(__name__)


class WolframCrawler(BaseCrawler):
    """Crawler for Wolfram Alpha website.

    This crawler is specifically designed to crawl the Wolfram Alpha website,
    particularly the MathWorld section.
    """

    def __init__(
        self,
        base_url: str = "https://mathworld.wolfram.com/",
        delay: float = 2.5,
        output_dir: Optional[Path] = None,
        batch_size: int = 500,
    ):
        """Initialize the Wolfram crawler.

        Args:
            base_url: The base URL for Wolfram Alpha
            delay: Delay between requests in seconds
            output_dir: Directory to save crawled data
            batch_size: Number of pages per batch file
        """
        self.base_url = base_url
        self.delay = delay
        self.output_dir = output_dir or Path("data/raw")
        self.batch_size = batch_size

        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize data structures
        self.url_list: List[str] = []
        self.url_parent_category: Dict[str, str] = {}
        self.category_level: Dict[str, int] = {}
        self.history: Dict[str, int] = {}
        self.final_urls: Dict[str, Tuple[str, str, int]] = {}

    def crawl(self, url: str, max_pages: int = 1000) -> List[Dict[str, Any]]:
        """Crawl the Wolfram Alpha website starting from the given URL.

        Args:
            url: The starting URL to crawl from
            max_pages: Maximum number of pages to crawl

        Returns:
            A list of dictionaries containing the crawled data
        """
        # Extract category from URL
        if "topics/" in url:
            category = url.split("/")[-1].split(".")[0]
        else:
            category = "Root"

        # Initialize crawling state
        self.url_list = [url]
        self.url_parent_category[url] = category
        self.category_level[category] = 0 if category == "Root" else 1

        parsed = 0
        n_urls = 1
        results = []

        # Create log files
        crawl_log = self.output_dir / "crawl_log.txt"
        category_log = self.output_dir / "crawl_categories.txt"

        with open(crawl_log, "w", encoding="utf-8") as file1, \
             open(category_log, "w", encoding="utf-8") as file2:

            # Main crawling loop
            while parsed < min(max_pages, n_urls):
                current_url = self.url_list[parsed]
                parent_category = self.url_parent_category[current_url]
                level = self.category_level[parent_category]

                # Respect crawling delay
                time.sleep(self.delay)
                parsed += 1

                # Skip if already crawled
                if current_url in self.history:
                    logger.info(f"Duplicate: {current_url}")
                    file1.write(f"{current_url}\tDuplicate\t{parent_category}\t{level}\n")
                    continue

                logger.info(f"Parsing: {parsed} out of {n_urls}: {current_url}")

                try:
                    # Fetch the page
                    response = requests.get(current_url, timeout=5)
                    self.history[current_url] = response.status_code

                    if response.status_code != 200:
                        logger.warning(f"Failed: {current_url} with status {response.status_code}")
                        file1.write(f"{current_url}\tError:{response.status_code}\t{parent_category}\t{level}\n")
                        continue

                    # Process the page
                    file1.write(f"{current_url}\tParsed\t{parent_category}\t{level}\n")
                    page = response.text

                    # Process directory page
                    if "topics/" in current_url:
                        # Extract links to other directory pages
                        new_urls = self._extract_directory_links(page, current_url, parent_category, level, file1, file2)
                        self.url_list.extend(new_urls)
                        n_urls += len(new_urls)

                    # Process content page
                    else:
                        page_data = self.process_page(current_url, page, parent_category)
                        if page_data:
                            results.append(page_data)
                            self.final_urls[current_url] = (page_data["category"], parent_category, level + 1)

                except Exception as e:
                    logger.error(f"Error processing {current_url}: {e}")
                    file1.write(f"{current_url}\tError:{str(e)}\t{parent_category}\t{level}\n")

            # Save final URLs
            self._save_final_urls()

            # Save crawled content in batches
            self._save_content_batches(results)

        return results

    def process_page(self, url: str, content: Optional[str] = None, parent_category: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Process a single page.

        Args:
            url: The URL of the page to process
            content: The page content if already fetched, otherwise it will be fetched
            parent_category: The parent category of the page

        Returns:
            A dictionary containing the processed page data or None if the page
            couldn't be processed
        """
        if content is None:
            try:
                response = requests.get(url, timeout=5)
                if response.status_code != 200:
                    logger.warning(f"Failed to fetch {url}: {response.status_code}")
                    return None
                content = response.text
            except Exception as e:
                logger.error(f"Error fetching {url}: {e}")
                return None

        # Extract page components
        try:
            header, main_content, related, see_also = self._split_page(content)

            # Extract category
            if parent_category:
                category = parent_category
            else:
                category = self._get_category(content)

            return {
                "url": url,
                "category": category,
                "content": main_content,
                "related": related,
                "see_also": see_also,
                "top_category": self._get_top_category(content)
            }
        except Exception as e:
            logger.error(f"Error processing content from {url}: {e}")
            return None

    def _extract_directory_links(
        self, page: str, current_url: str, parent_category: str, level: int, log_file, category_file
    ) -> List[str]:
        """Extract links from a directory page.

        Args:
            page: The page content
            current_url: The current URL
            parent_category: The parent category
            level: The category level
            log_file: The log file to write to
            category_file: The category file to write to

        Returns:
            A list of new URLs to crawl
        """
        new_urls = []

        # Extract links to other directory pages
        page1 = page.replace('\n', ' ').split("<a href=\"/topics/")
        for line in page1[1:]:  # Skip the first element which is before the first link
            line = line.split("<span>")[0]
            if line.count(">") == 1:
                line = line.split("\">")
                if len(line) > 1:
                    new_url = f"{self.base_url}topics/{line[0]}"
                    new_category = line[1]

                    # Update data structures
                    self.url_parent_category[new_url] = new_category
                    self.category_level[new_category] = level + 1

                    # Log the new URL
                    category_file.write(f"{level+1}\t{new_category}\t{parent_category}\n")
                    log_file.write(f"{new_url}\tQueued\t{new_category}\t{level+1}\n")

                    new_urls.append(new_url)

        return new_urls

    def _split_page(self, page: str) -> Tuple[str, str, List[str], List[str]]:
        """Split a page into its components.

        Args:
            page: The page content

        Returns:
            A tuple containing the header, content, related topics, and see also links
        """
        # Extract header and content
        parts = page.split("<!-- Begin Content -->")
        header = parts[0].split("\t~")[0]

        content_parts = parts[1].split("<!-- End Content -->")
        content = content_parts[0]

        # Extract related topics
        related = []
        related_parts = content_parts[1].split("<h2>See also</h2>")
        if len(related_parts) > 1:
            related_html = related_parts[1].split("<!-- End See Also -->")[0]
            for item in related_html.split("\">"):
                item = item.split("<")[0]
                if item and "mathworld" not in item.lower():
                    related.append(item)

        # Extract see also links
        see_also = []
        see_parts = page.split("<p class=\"CrossRefs\">")
        if len(see_parts) > 1:
            see_html = see_parts[1].split("<!-- Begin See Also -->")[0]
            for item in see_html.split("\">"):
                item = item.split("<")[0]
                if item and item.strip():
                    see_also.append(item)

        return header, content, related, see_also

    def _get_top_category(self, page: str) -> str:
        """Extract the top category from a page.

        Args:
            page: The page content

        Returns:
            The top category
        """
        try:
            breadcrumb = page.split("<ul class=\"breadcrumb\">")[1]
            category_html = breadcrumb.split("\">")[1]
            top_category = category_html.split("</a>")[0]
            return top_category
        except (IndexError, KeyError):
            return "Unknown"

    def _get_category(self, page: str) -> str:
        """Extract the category from a page.

        Args:
            page: The page content

        Returns:
            The category
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you would parse the page more carefully
            if "<title>" in page and "</title>" in page:
                title = page.split("<title>")[1].split("</title>")[0]
                if " -- " in title:
                    return title.split(" -- ")[0]
            return "Uncategorized"
        except (IndexError, KeyError):
            return "Uncategorized"

    def _save_final_urls(self) -> None:
        """Save the final URLs to a file."""
        final_urls_file = self.output_dir / "list_final_URLs.txt"
        with open(final_urls_file, "w", encoding="utf-8") as file:
            for i, (url, (category, parent, level)) in enumerate(self.final_urls.items(), 1):
                file.write(f"{i}\t{url}\t{category}\t{parent}\t{level}\n")

    def _save_content_batches(self, results: List[Dict[str, Any]]) -> None:
        """Save the crawled content in batches.

        Args:
            results: The crawled results
        """
        for i in range(0, len(results), self.batch_size):
            batch = results[i:i+self.batch_size]
            begin = i + 1
            end = min(i + self.batch_size, len(results))

            batch_file = self.output_dir / f"crawl_final_{begin}_{end}.txt"
            with open(batch_file, "w", encoding="utf-8") as file:
                for result in batch:
                    # Format: URL, category, separator, content
                    file.write(f"{result['url']}\t{result['category']}\t~{result['content']}\n")
