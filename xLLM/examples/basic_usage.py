"""Basic usage example for xLLM."""

from pathlib import Path

from xllm.core import Config
from xllm.crawlers import WolframCrawler
from xllm.processors import PDFProcessor
from xllm.knowledge_base import HashKnowledgeBase
from xllm.query_engine import QueryEngine


def main():
    """Run a basic example of xLLM functionality."""
    # Initialize configuration
    config = Config()

    # Ensure directories exist
    config.data_dir.mkdir(exist_ok=True)
    config.raw_dir.mkdir(exist_ok=True, parents=True)
    config.processed_dir.mkdir(exist_ok=True, parents=True)
    config.knowledge_dir.mkdir(exist_ok=True, parents=True)

    # Example 1: Crawl a website
    print("Example 1: Crawling a website")
    crawler = WolframCrawler(output_dir=config.raw_dir)
    crawler.crawl(
        "https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html",
        max_pages=5,  # Limit to 5 pages for the example
    )
    print("Crawling complete\n")

    # Example 2: Process a PDF (if available)
    pdf_path = Path("examples/sample.pdf")
    if pdf_path.exists():
        print("Example 2: Processing a PDF")
        processor = PDFProcessor(output_dir=config.processed_dir)
        result = processor.process_file(pdf_path)
        print(f"PDF processing complete. Extracted {len(result.get('pages', []))} pages\n")

    # Example 3: Build a knowledge base
    print("Example 3: Building a knowledge base")
    kb = HashKnowledgeBase(output_dir=config.knowledge_dir)

    # Add data from crawled files
    for crawl_file in config.raw_dir.glob("crawl_*.txt"):
        print(f"Adding data from {crawl_file}")
        with open(crawl_file, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split("\t")
                if len(parts) >= 3:
                    url, category, content = parts[0], parts[1], parts[2]
                    kb.add_data(
                        {
                            "url": url,
                            "category": category,
                            "content": content,
                        }
                    )

    # Save the knowledge base
    kb.save()
    print("Knowledge base built and saved\n")

    # Example 4: Query the knowledge base
    print("Example 4: Querying the knowledge base")
    query_engine = QueryEngine(kb)
    results = query_engine.query("probability")

    print("Query results:")
    for i, result in enumerate(results[:5], 1):  # Show top 5 results
        print(f"{i}. {result['word']} (score: {result['score']:.2f})")

    print("\nExample complete")


if __name__ == "__main__":
    main()
