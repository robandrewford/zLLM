# Makefile for xLLM

# Variables
PYTHON = python
VENV = .venv
UV = uv
DATA_DIR = data
KNOWLEDGE_DIR = $(DATA_DIR)/knowledge
PROCESSED_DIR = $(DATA_DIR)/processed
RAW_DIR = $(DATA_DIR)/raw
LOGS_DIR = $(DATA_DIR)/logs
TAXONOMY_DIR = $(DATA_DIR)/taxonomy

# Default target
.PHONY: all
all: setup create-dirs build-kb query

# Setup development environment
.PHONY: setup
setup:
	@echo "Setting up development environment..."
	./scripts/setup_dev_env.sh

# Activate virtual environment (note: this needs to be sourced, not run as a make target)
# Use: source $(MAKE) activate
.PHONY: activate
activate:
	@echo "source $(VENV)/bin/activate"

# Build knowledge base from example data
.PHONY: build-kb
build-kb:
	@echo "Building knowledge base from example data..."
	$(PYTHON) examples/comprehensive_kb_example.py

# Build taxonomy
.PHONY: build-taxonomy
build-taxonomy:
	@echo "Building taxonomy..."
	$(PYTHON) -m xllm build-taxonomy --output-dir $(TAXONOMY_DIR)

# Process a PDF file
.PHONY: process-pdf
process-pdf:
	@if [ -z "$(PDF_FILE)" ]; then \
		echo "Error: PDF_FILE is not set. Use 'make process-pdf PDF_FILE=path/to/file.pdf'"; \
		exit 1; \
	fi
	@echo "Processing PDF file: $(PDF_FILE)..."
	$(PYTHON) -m xllm process-pdf $(PDF_FILE) --output-dir $(PROCESSED_DIR)

# Process NVIDIA PDF
.PHONY: process-nvidia-pdf
process-nvidia-pdf:
	@if [ -z "$(PDF_FILE)" ]; then \
		echo "Error: PDF_FILE is not set. Use 'make process-nvidia-pdf PDF_FILE=path/to/file.pdf'"; \
		exit 1; \
	fi
	@echo "Processing NVIDIA PDF file: $(PDF_FILE)..."
	$(PYTHON) -m xllm process-nvidia-pdf $(PDF_FILE) --output-dir $(PROCESSED_DIR)

# Add processed PDF to knowledge base
.PHONY: add-pdf-to-kb
add-pdf-to-kb:
	@if [ -z "$(JSON_FILE)" ]; then \
		echo "Error: JSON_FILE is not set. Use 'make add-pdf-to-kb JSON_FILE=path/to/processed.json'"; \
		exit 1; \
	fi
	@echo "Adding processed PDF to knowledge base: $(JSON_FILE)..."
	$(PYTHON) add_pdf_to_kb.py --input-file $(JSON_FILE) --kb-dir $(KNOWLEDGE_DIR) --save

# Query the knowledge base
.PHONY: query
query:
	@if [ -z "$(QUERY)" ]; then \
		echo "Error: QUERY is not set. Use 'make query QUERY=\"your query\"'"; \
		exit 1; \
	fi
	@echo "Querying knowledge base for: $(QUERY)..."
	$(PYTHON) -m xllm query "$(QUERY)" --knowledge-base-dir $(KNOWLEDGE_DIR)

# Crawl a website
.PHONY: crawl
crawl:
	@if [ -z "$(URL)" ]; then \
		echo "Error: URL is not set. Use 'make crawl URL=https://example.com'"; \
		exit 1; \
	fi
	@echo "Crawling website: $(URL)..."
	$(PYTHON) -m xllm crawl --url "$(URL)" --output-dir $(RAW_DIR)

# Build knowledge base from crawled data
.PHONY: build-kb-from-crawl
build-kb-from-crawl:
	@echo "Building knowledge base from crawled data..."
	$(PYTHON) -m xllm build-kb --input-dir $(RAW_DIR) --output-dir $(KNOWLEDGE_DIR) --save

# Run verification
.PHONY: verify
verify:
	@echo "Running verification..."
	$(PYTHON) scripts/verify_xllm.py --verbose

# Run tests
.PHONY: test
test:
	@echo "Running tests..."
	pytest

# Run tests with coverage
.PHONY: test-cov
test-cov:
	@echo "Running tests with coverage..."
	pytest --cov=src/

# Run type checking
.PHONY: type-check
type-check:
	@echo "Running type checking with pyright..."
	pyright

# Clean up
.PHONY: clean
clean:
	@echo "Cleaning up..."
	rm -rf $(KNOWLEDGE_DIR)/*.txt
	rm -rf $(KNOWLEDGE_DIR)/*.pkl
	rm -rf $(PROCESSED_DIR)/*.json
	rm -rf $(LOGS_DIR)/*.log
	rm -rf *.log

# Clean everything including virtual environment
.PHONY: clean-all
clean-all: clean
	@echo "Cleaning everything including virtual environment..."
	rm -rf $(VENV)

# Create directory structure
.PHONY: create-dirs
create-dirs:
	@echo "Creating directory structure..."
	mkdir -p $(KNOWLEDGE_DIR)
	mkdir -p $(PROCESSED_DIR)
	mkdir -p $(RAW_DIR)
	mkdir -p $(LOGS_DIR)
	mkdir -p $(TAXONOMY_DIR)
	@echo "Directory structure created."

# Help
.PHONY: help
help:
	@echo "Available targets:"
	@echo "  all               - Setup environment and build knowledge base"
	@echo "  setup             - Setup development environment"
	@echo "  create-dirs       - Create directory structure"
	@echo "  build-kb          - Build knowledge base from example data"
	@echo "  build-taxonomy    - Build taxonomy from knowledge base"
	@echo "  process-pdf       - Process a PDF file (use: make process-pdf PDF_FILE=path/to/file.pdf)"
	@echo "  process-nvidia-pdf - Process a NVIDIA PDF file (use: make process-nvidia-pdf PDF_FILE=path/to/file.pdf)"
	@echo "  add-pdf-to-kb     - Add processed PDF to knowledge base (use: make add-pdf-to-kb JSON_FILE=path/to/processed.json)"
	@echo "  query             - Query the knowledge base (use: make query QUERY=\"your query\")"
	@echo "  crawl             - Crawl a website (use: make crawl URL=https://example.com)"
	@echo "  build-kb-from-crawl - Build knowledge base from crawled data"
	@echo "  verify            - Run verification script"
	@echo "  test              - Run tests"
	@echo "  test-cov          - Run tests with coverage"
	@echo "  type-check        - Run type checking with pyright"
	@echo "  clean             - Clean up generated files"
	@echo "  clean-all         - Clean everything including virtual environment"
	@echo "  help              - Show this help message"
