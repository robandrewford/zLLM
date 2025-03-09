"""
Tor-based web crawler for accessing websites that block regular crawlers.
This module uses the Tor network to rotate IP addresses and avoid blocking.
"""

import argparse
import json
import logging
import time
from pathlib import Path
import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("tor_crawler")


class TorCrawler:
    """Crawler using Tor network to avoid 403 errors."""

    def __init__(
        self,
        tor_proxy="socks5://127.0.0.1:9050",  # Default Tor SOCKS proxy
        delay=2.5,
        output_dir="data/scraped",
        max_retries=3,
        circuit_retries=2,
    ):
        """Initialize the Tor crawler.

        Args:
            tor_proxy: Tor SOCKS proxy URL
            delay: Delay between requests in seconds
            output_dir: Directory to save crawled data
            max_retries: Maximum number of retries for failed requests
            circuit_retries: Maximum number of circuit rebuilds to try
        """
        self.tor_proxy = tor_proxy
        self.delay = delay
        self.output_dir = Path(output_dir)
        self.max_retries = max_retries
        self.circuit_retries = circuit_retries

        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Set up the session with the Tor proxy
        self.session = self._create_tor_session()

        logger.info(f"Tor crawler initialized with proxy: {tor_proxy}")

    def _create_tor_session(self):
        """Create a new Tor session.

        Returns:
            requests.Session object configured to use Tor
        """
        session = requests.Session()
        session.proxies = {
            "http": self.tor_proxy,
            "https": self.tor_proxy,
        }

        # Set a user agent to avoid being blocked
        session.headers.update(
            {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.5",
                "Connection": "keep-alive",
                "Upgrade-Insecure-Requests": "1",
                "Cache-Control": "max-age=0",
            }
        )

        return session

    def _renew_tor_circuit(self):
        """
        Renew the Tor circuit to get a new IP address.
        """
        logger.info("Renewing Tor circuit to get a new IP address...")

        # First try using the control port
        success = False

        try:
            # Try to use the stem library if available
            from stem import Signal  # type: ignore
            from stem.control import Controller  # type: ignore

            with Controller.from_port(port=9051) as controller:
                controller.authenticate()  # You might need to provide a password here
                controller.signal(Signal.NEWNYM)
                logger.info("Successfully renewed Tor circuit via control port")
                success = True
                time.sleep(self.delay)  # Wait for the new circuit to be established
        except Exception as e:
            logger.warning(f"Failed to renew Tor circuit via control port: {e}")

        if not success:
            logger.warning(
                "Please restart the Tor service manually or install stem with 'pip install stem'"
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
        for circuit_retry in range(self.circuit_retries):
            for retry in range(self.max_retries):
                try:
                    # Make the request
                    response = self.session.get(url, timeout=30)

                    # If successful
                    if response.status_code == 200:
                        # Create page data
                        page_data = {
                            "url": url,
                            "status_code": response.status_code,
                            "content": response.text,
                            "headers": dict(response.headers),
                            "timestamp": time.time(),
                        }

                        logger.info(f"Successfully crawled: {url}")
                        return page_data
                    else:
                        logger.warning(
                            f"Failed: {url} with status {response.status_code}"
                        )
                except requests.exceptions.RequestException as e:
                    logger.warning(f"Request Error: {url} - {e}")
                except Exception as e:
                    logger.warning(f"Error: {url} - {e}")

                # If we're going to retry
                if retry < self.max_retries - 1:
                    # Exponential backoff
                    wait_time = self.delay * (2**retry)
                    logger.info(f"Retrying in {wait_time:.2f} seconds...")
                    time.sleep(wait_time)

            # If we've exhausted all retries for this circuit
            if circuit_retry < self.circuit_retries - 1:
                logger.info("Renewing Tor circuit and trying again...")
                self._renew_tor_circuit()

        # If we've exhausted all retries and circuit rebuilds
        logger.error(
            f"Failed to crawl {url} after {self.max_retries} retries and {self.circuit_retries} circuit rebuilds"
        )
        return None

    def _extract_links(self, page_data):
        """Extract links from page data.

        Args:
            page_data: Dictionary with page data

        Returns:
            List of URLs
        """
        urls = []

        try:
            # Parse the HTML
            soup = BeautifulSoup(page_data["content"], "html.parser")

            # Find all links
            for link in soup.find_all("a", href=True):
                url = link["href"]

                # Convert relative URLs to absolute URLs
                if url.startswith("/"):
                    # Get the base URL
                    base_url = "/".join(
                        page_data["url"].split("/")[:3]
                    )  # http(s)://domain.com
                    url = base_url + url
                elif not url.startswith(("http://", "https://")):
                    # Skip non-HTTP URLs (like javascript:, mailto:, etc.)
                    continue

                # Only add if it's a valid URL
                if "wolfram.com" in url:
                    urls.append(url)
        except Exception as e:
            logger.error(f"Error extracting links: {e}")

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
    """Main function to run the Tor crawler."""
    parser = argparse.ArgumentParser(description="Tor Crawler")
    parser.add_argument(
        "--url", type=str, required=True, help="Starting URL for crawling"
    )
    parser.add_argument(
        "--tor-proxy",
        type=str,
        default="socks5://127.0.0.1:9050",
        help="Tor SOCKS proxy URL",
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
    parser.add_argument(
        "--circuit-retries",
        type=int,
        default=2,
        help="Maximum number of circuit rebuilds to try",
    )
    args = parser.parse_args()

    # Create the crawler
    crawler = TorCrawler(
        tor_proxy=args.tor_proxy,
        delay=args.delay,
        output_dir=args.output_dir,
        max_retries=args.max_retries,
        circuit_retries=args.circuit_retries,
    )

    # Crawl the website
    crawler.crawl(args.url, args.max_pages)


if __name__ == "__main__":
    main()
