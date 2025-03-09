import argparse
import json
import logging
import random
import time
from urllib import request as urlrequest
from urllib.error import HTTPError, URLError
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("brightdata_crawler")


class BrightdataCrawler:
    """Crawler using Brightdata proxy to avoid 403 errors."""

    def __init__(
        self,
        username="brd-customer-hl_YOUR_CUSTOMER_ID",  # Replace with your Brightdata username
        password="YOUR_PASSWORD",  # Replace with your Brightdata password
        port=22225,
        country="us",
        delay=2.5,
        output_dir="data/scraped",
        max_retries=3,
    ):
        """Initialize the Brightdata crawler.

        Args:
            username: Brightdata username
            password: Brightdata password
            port: Brightdata proxy port
            country: Country code for the proxy
            delay: Delay between requests in seconds
            output_dir: Directory to save crawled data
            max_retries: Maximum number of retries for failed requests
        """
        self.username = username
        self.password = password
        self.port = port
        self.country = country
        self.delay = delay
        self.output_dir = Path(output_dir)
        self.max_retries = max_retries

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Initialize session ID
        self.session_id = random.random()

        # Build proxy URL
        self.super_proxy_url = (
            f"http://{self.username}-country-{self.country}-session-{self.session_id}:"
            f"{self.password}@brd.superproxy.io:{self.port}"
        )

        # Create proxy handler
        self.proxy_handler = urlrequest.ProxyHandler(
            {
                "http": self.super_proxy_url,
                "https": self.super_proxy_url,
            }
        )

        # Build opener with proxy handler
        self.opener = urlrequest.build_opener(self.proxy_handler)

        logger.info(
            f"Brightdata crawler initialized with session ID: {self.session_id}"
        )

    def crawl(self, url, max_pages=10):
        """Crawl a website starting from the given URL.

        Args:
            url: Starting URL for crawling
            max_pages: Maximum number of pages to crawl

        Returns:
            List of crawled pages
        """
        logger.info(f"Starting crawl from {url} with max {max_pages} pages")

        # Initialize variables
        crawled_pages = []
        urls_to_crawl = [url]
        crawled_urls = set()

        # Crawl until we reach max_pages or run out of URLs
        while urls_to_crawl and len(crawled_pages) < max_pages:
            # Get the next URL to crawl
            current_url = urls_to_crawl.pop(0)

            # Skip if we've already crawled this URL
            if current_url in crawled_urls:
                continue

            logger.info(
                f"Crawling: {len(crawled_pages) + 1} out of {max_pages}: {current_url}"
            )

            # Crawl the page
            page_data = self._crawl_page(current_url)

            # If crawling was successful
            if page_data:
                # Add to crawled pages
                crawled_pages.append(page_data)
                crawled_urls.add(current_url)

                # Extract links from the page and add to urls_to_crawl
                new_urls = self._extract_links(page_data)
                for new_url in new_urls:
                    if new_url not in crawled_urls and new_url not in urls_to_crawl:
                        urls_to_crawl.append(new_url)

                # Save the page data
                self._save_page(page_data)

            # Delay between requests
            time.sleep(self.delay)

        logger.info(f"Crawling complete. Crawled {len(crawled_pages)} pages")
        return crawled_pages

    def _crawl_page(self, url):
        """Crawl a single page.

        Args:
            url: URL to crawl

        Returns:
            Dictionary with page data or None if crawling failed
        """
        for retry in range(self.max_retries):
            try:
                # Open the URL
                response = self.opener.open(url)

                # Get the status code
                status_code = response.getcode()

                # If successful
                if status_code == 200:
                    # Read the content
                    content = response.read().decode("utf-8")

                    # Get the headers
                    headers = dict(response.info())

                    # Create page data
                    page_data = {
                        "url": url,
                        "status_code": status_code,
                        "content": content,
                        "headers": headers,
                        "timestamp": time.time(),
                    }

                    logger.info(f"Successfully crawled: {url}")
                    return page_data
                else:
                    logger.warning(f"Failed: {url} with status {status_code}")
            except HTTPError as e:
                logger.warning(f"HTTP Error: {url} - {e.code} {e.reason}")
            except URLError as e:
                logger.warning(f"URL Error: {url} - {e.reason}")
            except Exception as e:
                logger.warning(f"Error: {url} - {e}")

            # If we're going to retry
            if retry < self.max_retries - 1:
                # Exponential backoff
                wait_time = self.delay * (2**retry)
                logger.info(f"Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)

                # Create a new session ID for the retry
                self.session_id = random.random()

                # Rebuild the proxy URL
                self.super_proxy_url = (
                    f"http://{self.username}-country-{self.country}-session-{self.session_id}:"
                    f"{self.password}@brd.superproxy.io:{self.port}"
                )

                # Create new proxy handler
                self.proxy_handler = urlrequest.ProxyHandler(
                    {
                        "http": self.super_proxy_url,
                        "https": self.super_proxy_url,
                    }
                )

                # Build new opener with proxy handler
                self.opener = urlrequest.build_opener(self.proxy_handler)

                logger.info(f"Created new session ID: {self.session_id}")

        # If we've exhausted all retries
        logger.error(f"Failed to crawl {url} after {self.max_retries} retries")
        return None

    def _extract_links(self, page_data):
        """Extract links from page data.

        Args:
            page_data: Dictionary with page data

        Returns:
            List of URLs
        """
        # This is a simple implementation that would need to be enhanced
        # with proper HTML parsing for a production crawler
        content = page_data["content"]
        urls = []

        # Look for href attributes
        start_index = 0
        while True:
            # Find the next href attribute
            href_index = content.find('href="', start_index)
            if href_index == -1:
                break

            # Find the end of the URL
            start_url = href_index + 6
            end_url = content.find('"', start_url)
            if end_url == -1:
                break

            # Extract the URL
            url = content[start_url:end_url]

            # Only add if it's a valid URL
            if url.startswith("http") and "wolfram.com" in url:
                urls.append(url)

            # Move to the next position
            start_index = end_url

        return urls

    def _save_page(self, page_data):
        """Save page data to a file.

        Args:
            page_data: Dictionary with page data
        """
        # Create a filename from the URL
        url = page_data["url"]
        filename = (
            url.replace("://", "_")
            .replace("/", "_")
            .replace("?", "_")
            .replace("&", "_")
        )
        filename = f"{filename}.json"

        # Save to file
        file_path = self.output_dir / filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(page_data, f, indent=2)

        logger.info(f"Saved page data to {file_path}")


def main():
    """Main function to run the Brightdata crawler."""
    parser = argparse.ArgumentParser(description="Brightdata Crawler")
    parser.add_argument(
        "--url", type=str, required=True, help="Starting URL for crawling"
    )
    parser.add_argument(
        "--username",
        type=str,
        default="brd-customer-hl_YOUR_CUSTOMER_ID",
        help="Brightdata username",
    )
    parser.add_argument(
        "--password", type=str, default="YOUR_PASSWORD", help="Brightdata password"
    )
    parser.add_argument("--port", type=int, default=22225, help="Brightdata proxy port")
    parser.add_argument(
        "--country", type=str, default="us", help="Country code for the proxy"
    )
    parser.add_argument(
        "--delay", type=float, default=2.5, help="Delay between requests in seconds"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="data/scraped",
        help="Directory to save crawled data",
    )
    parser.add_argument(
        "--max-pages", type=int, default=10, help="Maximum number of pages to crawl"
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum number of retries for failed requests",
    )
    args = parser.parse_args()

    # Create the crawler
    crawler = BrightdataCrawler(
        username=args.username,
        password=args.password,
        port=args.port,
        country=args.country,
        delay=args.delay,
        output_dir=args.output_dir,
        max_retries=args.max_retries,
    )

    # Crawl the website
    crawler.crawl(args.url, args.max_pages)


if __name__ == "__main__":
    main()
