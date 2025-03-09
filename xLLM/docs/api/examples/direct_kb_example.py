#!/usr/bin/env python
"""Direct manipulation example for the HashKnowledgeBase."""

import logging
from pathlib import Path

from xllm.knowledge_base import HashKnowledgeBase  # pyright: ignore

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("xLLM/data/logs/direct_kb_example.log"), logging.StreamHandler()],
)

# Create a knowledge base
kb = HashKnowledgeBase(
    max_tokens_per_word=3, min_token_frequency=1, output_dir=Path("./data/knowledge")
)

# Directly add entries to the dictionary and other data structures
print("Directly adding entries to the knowledge base...")

# Add words to the dictionary
words = ["probability", "statistics", "distribution", "normal", "bayes"]
for word in words:
    kb.dictionary[word] = 10  # Count of 10

    # Add to URL map
    kb.url_map[word] = {"0": 5, "1": 5}  # URL IDs 0 and 1 with count 5 each

    # Add to category map
    kb.hash_category[word] = {"Mathematics": 7, "Statistics": 3}

    # Add to related topics map
    kb.hash_related[word] = {"Mathematics": 5, "Data Analysis": 5}

    # Add to see also map
    kb.hash_see[word] = {"Probability Theory": 3, "Statistical Analysis": 3}

# Add URLs
kb.arr_url = ["https://example.com/probability", "https://example.com/statistics"]

# Add to compressed n-grams table
kb.compressed_ngrams_table = {
    "probability": ["probability"],
    "statistics": ["statistics"],
    "distribution": ["distribution"],
    "normal": ["normal"],
    "bayes": ["bayes"],
}

# Save the knowledge base
print("Saving knowledge base...")
kb.save("./data/knowledge")

# Query the knowledge base
print("\nQuerying knowledge base...")
queries = ["probability", "statistics", "bayes", "normal"]

for query in queries:
    print(f"\n--- Query: '{query}' ---")
    results = kb.query(query)
    print(f"Found {len(results)} results")

    for i, result in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(f"Word: {result.get('word', 'N/A')}")
        print(f"Score: {result.get('score', 0):.2f}")
        print(f"Count: {result.get('count', 0)}")

        # Print URLs
        urls = result.get("urls", {})
        if urls:
            print("URLs:")
            for url_id, count in urls.items():
                url_index = int(url_id)
                if url_index < len(kb.arr_url):
                    print(f"  - {kb.arr_url[url_index]} (count: {count})")

        # Print categories
        categories = result.get("categories", {})
        if categories:
            print("Categories:")
            for category, count in categories.items():
                print(f"  - {category} (count: {count})")

print("\nDone!")
