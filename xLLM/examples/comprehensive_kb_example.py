#!/usr/bin/env python
"""Comprehensive example demonstrating the HashKnowledgeBase functionality."""

import logging
import json
from pathlib import Path

from xllm.knowledge_base import HashKnowledgeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_sample_data():
    """Create sample data for the knowledge base."""
    return [
        {
            "url": "https://example.com/probability",
            "category": "Mathematics",
            "content": "Probability is a measure of the likelihood of an event occurring. "
                      "It is quantified as a number between 0 and 1, where 0 indicates impossibility "
                      "and 1 indicates certainty. The higher the probability of an event, the more "
                      "likely it is that the event will occur.",
            "related": ["Statistics", "Random Variables", "Mathematics"],
            "see_also": ["Probability Theory", "Bayes' Theorem"]
        },
        {
            "url": "https://example.com/statistics",
            "category": "Mathematics",
            "content": "Statistics is the discipline that concerns the collection, organization, "
                      "analysis, interpretation, and presentation of data. Statistical analysis "
                      "often uses probability theory and is essential for data science.",
            "related": ["Probability", "Data Analysis", "Mathematics"],
            "see_also": ["Statistical Inference", "Descriptive Statistics"]
        },
        {
            "url": "https://example.com/normal-distribution",
            "category": "Statistics",
            "content": "The normal distribution is a continuous probability distribution. "
                      "It is also called the Gaussian distribution. The normal distribution "
                      "is important in statistics and is often used in the natural and social sciences.",
            "related": ["Probability", "Statistics", "Distribution"],
            "see_also": ["Gaussian Distribution", "Bell Curve"]
        },
        {
            "url": "https://example.com/bayes-theorem",
            "category": "Probability",
            "content": "Bayes' theorem describes the probability of an event, based on prior knowledge "
                      "of conditions that might be related to the event. It is fundamental to Bayesian statistics.",
            "related": ["Probability", "Conditional Probability", "Statistics"],
            "see_also": ["Bayesian Statistics", "Probability Theory"]
        },
        {
            "url": "https://example.com/data-science",
            "category": "Computer Science",
            "content": "Data science is an interdisciplinary field that uses scientific methods, processes, "
                      "algorithms and systems to extract knowledge and insights from structured and "
                      "unstructured data. It employs techniques from statistics, computer science, "
                      "and information science.",
            "related": ["Statistics", "Machine Learning", "Artificial Intelligence"],
            "see_also": ["Big Data", "Data Mining", "Predictive Analytics"]
        }
    ]

def initialize_kb():
    """Initialize the knowledge base with sample data."""
    # Create a knowledge base
    kb = HashKnowledgeBase(
        max_tokens_per_word=3,
        min_token_frequency=1,
        output_dir=Path("./data/knowledge")
    )

    # Initialize stopwords
    kb.stopwords = set(["a", "an", "the", "and", "or", "but", "is", "are", "was", "were",
                        "be", "been", "being", "in", "on", "at", "to", "for", "with", "by",
                        "about", "of", "from"])

    # Add sample data
    sample_data = create_sample_data()
    for data in sample_data:
        kb.add_data(data)

    # Manually add entries to the compressed n-grams table
    # This is normally done during a build phase
    kb.compressed_ngrams_table = {}
    for word in kb.dictionary:
        # Create a simple mapping from each word to itself
        sorted_word = "~".join(sorted(word.split("~")))
        if sorted_word not in kb.compressed_ngrams_table:
            kb.compressed_ngrams_table[sorted_word] = []
        kb.compressed_ngrams_table[sorted_word].append(word)

    return kb

def save_and_load_kb(kb, save_path):
    """Save and load the knowledge base."""
    # Save the knowledge base
    logger.info(f"Saving knowledge base to {save_path}")
    kb.save(save_path)

    # Load the knowledge base
    logger.info(f"Loading knowledge base from {save_path}")
    new_kb = HashKnowledgeBase()
    new_kb.load(save_path)

    return new_kb

def query_kb(kb):
    """Query the knowledge base with various queries."""
    queries = [
        "probability",
        "statistics",
        "bayes",
        "normal distribution",
        "data science",
        "machine learning"
    ]

    results_by_query = {}

    for query in queries:
        logger.info(f"Querying for: '{query}'")
        results = kb.query(query)
        results_by_query[query] = results

        print(f"\n--- Query: '{query}' ---")
        print(f"Found {len(results)} results")

        for i, result in enumerate(results[:3], 1):  # Show top 3 results
            print(f"\nResult {i}:")
            print(f"Word: {result.get('word', 'N/A')}")
            print(f"Score: {result.get('score', 0):.2f}")
            print(f"Count: {result.get('count', 0)}")

            # Print URLs (up to 2)
            urls = result.get('urls', {})
            if urls:
                print("URLs:")
                for j, (url_id, count) in enumerate(urls.items()):
                    if j >= 2:  # Limit to 2 URLs
                        print("  - ...")
                        break
                    url_index = int(url_id)
                    if url_index < len(kb.arr_url):
                        print(f"  - {kb.arr_url[url_index]} (count: {count})")

            # Print categories (up to 2)
            categories = result.get('categories', {})
            if categories:
                print("Categories:")
                for j, (category, count) in enumerate(categories.items()):
                    if j >= 2:  # Limit to 2 categories
                        print("  - ...")
                        break
                    print(f"  - {category} (count: {count})")

    return results_by_query

def analyze_kb(kb):
    """Analyze the knowledge base structure."""
    print("\n--- Knowledge Base Analysis ---")
    print(f"Dictionary size: {len(kb.dictionary)} words")
    print(f"URL count: {len(kb.arr_url)} URLs")

    # Top words by frequency
    top_words = sorted(kb.dictionary.items(), key=lambda x: x[1], reverse=True)[:10]
    print("\nTop words by frequency:")
    for word, count in top_words:
        print(f"  - {word}: {count}")

    # Category distribution
    categories = {}
    for word_categories in kb.hash_category.values():
        for category, count in word_categories.items():
            categories[category] = categories.get(category, 0) + count

    print("\nCategory distribution:")
    for category, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
        print(f"  - {category}: {count}")

def main():
    """Main function."""
    # Initialize knowledge base
    kb = initialize_kb()

    # Save and load knowledge base
    kb = save_and_load_kb(kb, "./data/knowledge")

    # Query knowledge base
    results = query_kb(kb)

    # Analyze knowledge base
    analyze_kb(kb)

    print("\nDone!")

if __name__ == "__main__":
    main()
