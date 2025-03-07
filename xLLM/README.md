# xLLM: Extensible Large Language Model

A modular knowledge extraction and query system designed for processing and organizing information from various sources including web crawls and PDFs.

## Features

- **Web Crawling**: Crawl websites like Wolfram Alpha to extract structured knowledge
- **PDF Processing**: Extract structured information from PDF documents, including tables and hierarchical content
- **Knowledge Base**: Efficiently store and query extracted knowledge using hash-based data structures
- **Query Engine**: Search and retrieve information from the knowledge base with relevance ranking
- **Modular Architecture**: Easily extend with new data sources, processors, and query methods

## Architecture

The system consists of several modular components:

1. **Crawlers**: Extract data from web sources
   - `BaseCrawler`: Abstract interface for all crawlers
   - `WolframCrawler`: Implementation for Wolfram Alpha

2. **Processors**: Process and structure raw data
   - `BaseProcessor`: Abstract interface for all processors
   - `PDFProcessor`: Implementation for PDF documents

3. **Knowledge Base**: Store and organize knowledge
   - `BaseKnowledgeBase`: Abstract interface for all knowledge bases
   - `HashKnowledgeBase`: Implementation using hash tables

4. **Query Engine**: Search and retrieve information
   - `BaseQueryEngine`: Abstract interface for all query engines
   - `KnowledgeQueryEngine`: Implementation for knowledge base queries

## Installation

### Using uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/yourusername/xLLM.git
cd xLLM

# Run the setup script
./scripts/setup_dev_env.sh
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/xLLM.git
cd xLLM

# Create a virtual environment with uv
uv venv
source .venv/bin/activate

# Install the package
uv pip install -e ".[dev]"
```

## Usage

### Command Line Interface

xLLM provides a command-line interface for common tasks:

```bash
# Crawl a website
python -m xllm crawl --url "https://mathworld.wolfram.com/topics/ProbabilityandStatistics.html" --output-dir data/raw

# Process a PDF document
python -m xllm process-pdf path/to/document.pdf --output-dir data/processed

# Build a knowledge base
python -m xllm build-kb --input-dir data/raw --output-dir data/knowledge --save

# Query the knowledge base
python -m xllm query "normal distribution" --knowledge-base-dir data/knowledge
```

### Python API

```python
from xllm.crawlers import WolframCrawler
from xllm.processors import PDFProcessor
from xllm.knowledge_base import HashKnowledgeBase
from xllm.query_engine import KnowledgeQueryEngine

# Initialize components
crawler = WolframCrawler()
processor = PDFProcessor()
kb = HashKnowledgeBase()
query_engine = KnowledgeQueryEngine(kb)

# Crawl and process data
data = crawler.crawl("https://mathworld.wolfram.com/ProbabilityandStatistics.html")
processed_data = processor.process_file("path/to/document.pdf")

# Add data to knowledge base
for item in data:
    kb.add_data(item)
kb.add_data(processed_data)

# Build derived tables
kb.build_derived_tables()

# Save the knowledge base
kb.save("data/knowledge")

# Query the knowledge base
results = query_engine.query("normal distribution")
print(query_engine.format_results(results))
```

## Development

### Setup Development Environment

```bash
# Run the setup script
./scripts/setup_dev_env.sh

# Activate the virtual environment
source .venv/bin/activate

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src/
```

### Code Style

This project uses ruff for linting and formatting:

```bash
# Check code style
ruff check .

# Format code
ruff format .
```

## Project Structure

```
xLLM/
├── data/                    # Data storage
│   ├── raw/                 # Raw crawled data
│   ├── processed/           # Processed data
│   └── knowledge/           # Knowledge base data
├── scripts/                 # Utility scripts
├── src/                     # Source code
│   └── xllm/                # Main package
│       ├── crawlers/        # Web crawling components
│       ├── processors/      # Data processing components
│       ├── knowledge_base/  # Knowledge base components
│       └── query_engine/    # Query engine components
└── tests/                   # Test suite
```

## License

MIT
