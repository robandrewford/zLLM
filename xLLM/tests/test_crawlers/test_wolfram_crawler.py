"""Tests for the Wolfram crawler."""

import pytest
from unittest.mock import patch, MagicMock
from pathlib import Path

from xllm.crawlers.wolfram_crawler import WolframCrawler


@pytest.fixture
def crawler():
    """Create a WolframCrawler instance for testing."""
    # Use a temporary directory for test output
    return WolframCrawler(output_dir=Path("./tests/test_data"))


def test_crawler_initialization():
    """Test that the crawler initializes correctly."""
    crawler = WolframCrawler(
        base_url="https://test.example.com/",
        delay=1.0,
        output_dir=Path("./test_output"),
        batch_size=100,
    )
    
    assert crawler.base_url == "https://test.example.com/"
    assert crawler.delay == 1.0
    assert crawler.output_dir == Path("./test_output")
    assert crawler.batch_size == 100
    assert crawler.url_list == []
    assert crawler.url_parent_category == {}
    assert crawler.category_level == {}
    assert crawler.history == {}
    assert crawler.final_urls == {}


@patch("requests.get")
def test_process_page(mock_get, crawler):
    """Test processing a single page."""
    # Mock the response
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = """
    <ul class="breadcrumb"><a href="/topics/ProbabilityandStatistics.html">Probability & Statistics</a></ul>
    <!-- Begin Content -->
    <h1>Test Page</h1>
    <p>This is a test page.</p>
    <!-- End Content -->
    <h2>See also</h2>
    <a href="/RelatedTopic1.html">Related Topic 1</a>
    <a href="/RelatedTopic2.html">Related Topic 2</a>
    <!-- End See Also -->
    <p class="CrossRefs">
    <a href="/SeeAlso1.html">See Also 1</a>
    <a href="/SeeAlso2.html">See Also 2</a>
    <!-- Begin See Also -->
    """
    mock_get.return_value = mock_response
    
    # Process the page
    result = crawler.process_page("https://mathworld.wolfram.com/TestPage.html")
    
    # Check the result
    assert result is not None
    assert result["url"] == "https://mathworld.wolfram.com/TestPage.html"
    assert result["top_category"] == "Probability & Statistics"
    assert "This is a test page" in result["content"]
    assert "Related Topic 1" in result["related"]
    assert "Related Topic 2" in result["related"]
    assert "See Also 1" in result["see_also"]
    assert "See Also 2" in result["see_also"]


@patch("requests.get")
def test_crawl_basic(mock_get, crawler, tmp_path):
    """Test basic crawling functionality."""
    # Set up the output directory
    crawler.output_dir = tmp_path
    
    # Mock the responses
    mock_response1 = MagicMock()
    mock_response1.status_code = 200
    mock_response1.text = """
    <ul class="breadcrumb"><a href="/topics/ProbabilityandStatistics.html">Probability & Statistics</a></ul>
    <a href="/topics/Distributions.html">Distributions</a>
    """
    
    mock_response2 = MagicMock()
    mock_response2.status_code = 200
    mock_response2.text = """
    <ul class="breadcrumb"><a href="/topics/ProbabilityandStatistics.html">Probability & Statistics</a></ul>
    <!-- Begin Content -->
    <h1>Distributions</h1>
    <p>This is about distributions.</p>
    <!-- End Content -->
    """
    
    # Configure the mock to return different responses for different URLs
    def side_effect(url, timeout=None):
        if "ProbabilityandStatistics" in url:
            return mock_response1
        else:
            return mock_response2
    
    mock_get.side_effect = side_effect
    
    # Crawl with a small max_pages to keep the test fast
    results = crawler.crawl(
        "https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
        max_pages=2
    )
    
    # Check that we got some results
    assert len(results) > 0
    
    # Check that the log files were created
    assert (tmp_path / "crawl_log.txt").exists()
    assert (tmp_path / "crawl_categories.txt").exists()
    
    # Check that the final URLs file was created
    assert (tmp_path / "list_final_URLs.txt").exists() 