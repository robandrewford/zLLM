# xLLM: A Modular Knowledge Extraction and Query System

xLLM is a modular system designed for extracting, organizing, and querying knowledge from various sources including web crawls and PDFs.

## Features

- **Web Crawling**: Extract information from websites with customizable crawlers
- **PDF Processing**: Extract structured data from PDF documents
- **Knowledge Base**: Store and index extracted information for efficient retrieval
- **Query Engine**: Search and retrieve information from the knowledge base
- **Taxonomy Builder**: Create hierarchical taxonomies from extracted knowledge
- **Enterprise Support**: Special features for enterprise knowledge management

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/xLLM.git
cd xLLM

# Set up the development environment
make setup

# Activate the virtual environment
source .venv/bin/activate
```

## Usage

### Command Line Interface

xLLM provides a command-line interface for common operations:

```bash
# Build a knowledge base from crawled data
xllm build-kb --input-dir data/raw --output-dir data/knowledge --save

# Process a PDF file
xllm process-pdf path/to/document.pdf --output-dir data/processed

# Query the knowledge base
xllm query "your query here" --knowledge-base-dir data/knowledge

# Build a taxonomy
xllm build-taxonomy --output-dir data/taxonomy
```

### Using the Makefile

The project includes a Makefile with common tasks:

```bash
# Set up the development environment
make setup

# Create the directory structure
make create-dirs

# Build a knowledge base from example data
make build-kb

# Process a PDF file
make process-pdf PDF_FILE=path/to/file.pdf

# Query the knowledge base
make query QUERY="your query"

# Run tests
make test

# Run type checking
make type-check
```

### Python API

```python
from xllm.core import Config
from xllm.crawlers import WolframCrawler
from xllm.processors import PDFProcessor
from xllm.knowledge_base import HashKnowledgeBase
from xllm.query_engine import QueryEngine

# Initialize configuration
config = Config()

# Crawl a website
crawler = WolframCrawler(output_dir=config.raw_dir)
crawler.crawl("https://example.com", max_pages=100)

# Process a PDF
processor = PDFProcessor(output_dir=config.processed_dir)
result = processor.process_file("path/to/document.pdf")

# Build a knowledge base
kb = HashKnowledgeBase(output_dir=config.knowledge_dir)
kb.add_data(result)
kb.save()

# Query the knowledge base
query_engine = QueryEngine(kb)
results = query_engine.query("your query")
```

## Project Structure

```
xLLM/
├── .github/                      # GitHub workflows and templates
├── docs/                         # Documentation
│   ├── api/                      # API documentation
│   ├── guides/                   # User guides
│   └── diagrams/                 # Diagrams (mermaid files)
├── examples/                     # Example usage scripts
├── scripts/                      # Utility scripts
│   ├── dev/                      # Development scripts
│   └── ci/                       # CI scripts
├── src/
│   └── xllm/                     # Main package
│       ├── cli/                  # Command-line interface
│       ├── core/                 # Core functionality
│       ├── crawlers/             # Web crawlers
│       ├── knowledge_base/       # Knowledge base functionality
│       ├── processors/           # Document processors
│       ├── query_engine/         # Query engine
│       ├── taxonomy/             # Taxonomy functionality
│       ├── enterprise/           # Enterprise features
│       └── utils/                # Utility functions
├── tests/                        # Tests mirror the src structure
│   ├── unit/                     # Unit tests
│   └── integration/              # Integration tests
├── Makefile                      # Project Makefile
├── pyproject.toml                # Project configuration
└── README.md                     # This file
```

## Development

### Setting Up the Development Environment

```bash
# Set up the development environment
make setup

# Run tests
make test

# Run type checking
make type-check
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin feature-name`
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Documentation

For more detailed documentation, see:

- [Data Workflow Guide](docs/guides/data_workflow.md)
- [Verification Guide](docs/guides/verification.md)
