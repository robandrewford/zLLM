#!/usr/bin/env python
"""Simple example demonstrating the use of the HashKnowledgeBase."""

import logging
from pathlib import Path

from xllm.knowledge_base import HashKnowledgeBase

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Create a knowledge base with minimal filtering
kb = HashKnowledgeBase(
    max_tokens_per_word=5,  # Allow longer token sequences
    min_token_frequency=1,  # Include all tokens regardless of frequency
    output_dir=Path("./data/knowledge")
)

# Add more data with repeated terms to increase token frequency
print("Adding data to knowledge base...")

# Add multiple entries with similar content to build up token frequency
for i in range(5):
    kb.add_data({
        "url": f"https://example.com/probability-{i}",
        "category": "Mathematics",
        "content": "Probability is a measure of the likelihood of an event occurring. "
                  "Probability theory is used extensively in statistics, mathematics, science, and philosophy.",
        "related": ["Statistics", "Random Variables", "Mathematics"],
        "see_also": ["Probability Theory", "Bayes' Theorem"]
    })

for i in range(3):
    kb.add_data({
        "url": f"https://example.com/statistics-{i}",
        "category": "Mathematics",
        "content": "Statistics is the discipline that concerns the collection, organization, "
                  "analysis, interpretation, and presentation of data. Statistical analysis "
                  "often uses probability theory.",
        "related": ["Probability", "Data Analysis", "Mathematics"],
        "see_also": ["Statistical Inference", "Descriptive Statistics"]
    })

kb.add_data({
    "url": "https://example.com/normal-distribution",
    "category": "Statistics",
    "content": "The normal distribution is a continuous probability distribution. "
              "It is also called the Gaussian distribution. The normal distribution "
              "is important in statistics and is often used in the natural and social sciences.",
    "related": ["Probability", "Statistics", "Distribution"],
    "see_also": ["Gaussian Distribution", "Bell Curve"]
})

kb.add_data({
    "url": "https://example.com/bayes-theorem",
    "category": "Probability",
    "content": "Bayes' theorem describes the probability of an event, based on prior knowledge "
              "of conditions that might be related to the event. It is fundamental to Bayesian statistics.",
    "related": ["Probability", "Conditional Probability", "Statistics"],
    "see_also": ["Bayesian Statistics", "Probability Theory"]
})

# Save the knowledge base
print("Saving knowledge base...")
kb.save("./data/knowledge")

# Try different queries
print("\nQuerying knowledge base...")
queries = ["probability", "statistics", "bayes", "normal distribution"]

for query in queries:
    print(f"\n--- Query: '{query}' ---")
    results = kb.query(query)
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

print("\nDone!")
