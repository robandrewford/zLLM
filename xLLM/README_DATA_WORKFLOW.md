# xLLM Data Processing Workflow

This document explains the complete data processing workflow for xLLM, which allows you to:

1. Process PDFs from a source directory
2. Process scraped web content from another directory
3. Combine the processed data
4. Compile the combined data into backend tables for LLM embeddings

## Directory Structure

The workflow uses the following directory structure:

```text
data/
├── pdfs/                  # Source PDF files
├── scraped/               # Source scraped web content
├── processed/
│   ├── pdfs/             # Processed PDF data
│   └── scraped/          # Processed scraped data
├── combined/             # Combined data from both sources
└── knowledge/            # Compiled backend tables for LLM embeddings
```

## Workflow Steps

### 1. Process PDFs

PDFs are processed using the `PDFProcessor` from the `xllm.processors` module. This processor:

- Extracts text content from PDFs
- Identifies document structure (headings, paragraphs, tables)
- Recognizes entities and key concepts
- Outputs structured JSON data

### 2. Process Scraped Web Content

Scraped web content is processed using the `WebContentProcessor` from the `xllm.processors` module. This processor:

- Cleans HTML and extracts meaningful content
- Identifies document structure
- Extracts metadata (title, author, publication date)
- Recognizes entities and key concepts
- Outputs structured JSON data

### 3. Combine Processed Data

The processed data from both sources is combined into a unified format. Each entry in the combined data includes:

- Source information (PDF or web)
- Original file name
- Processed content
- Extracted entities and concepts
- Metadata

### 4. Compile Backend Tables

The combined data is compiled into backend tables using the `HashKnowledgeBase` from the `xllm.knowledge_base` module. These tables include:

- Dictionary table: Maps words to their frequencies
- Embeddings table: Vector representations of words
- Word hash table: Associations between tokens
- Hash see/related/category tables: Semantic relationships
- N-grams table: Multi-token word sequences
- Compressed tables: Optimized versions for efficient querying

## Using the Workflow

### Basic Usage

To run the complete workflow:

```bash
python scripts/data_processing_workflow.py
```

This will process all PDFs in `data/pdfs/` and all scraped content in `data/scraped/`, combine them, and compile backend tables in `data/knowledge/`.

### Advanced Usage

You can customize the workflow with various options:

```bash
python scripts/data_processing_workflow.py \
  --pdf-dir custom/pdf/path \
  --scrape-dir custom/scrape/path \
  --processed-dir custom/processed/path \
  --combined-dir custom/combined/path \
  --tables-dir custom/tables/path
```

### Skipping Steps

You can skip certain steps if you've already completed them:

```bash
# Skip PDF processing
python scripts/data_processing_workflow.py --skip-pdfs

# Skip scraped content processing
python scripts/data_processing_workflow.py --skip-scraped

# Skip combining (use existing combined data)
python scripts/data_processing_workflow.py --skip-combine --existing-combined-file path/to/combined.json
```

## Using the Backend Tables with LLMs

The compiled backend tables can be used with any LLM as embeddings. The tables provide:

1. **Semantic Understanding**: The embeddings capture semantic relationships between concepts
2. **Domain-Specific Knowledge**: The tables contain domain-specific knowledge from your PDFs and scraped content
3. **Efficient Retrieval**: The compressed tables enable efficient retrieval of relevant information

To use the tables with an LLM:

1. Load the tables into memory
2. When processing a query, use the tables to retrieve relevant context
3. Provide the context to the LLM along with the query
4. The LLM can then generate responses grounded in your specific data

## Integration with xLLM

The backend tables are automatically integrated with xLLM's query engine. To use them:

```bash
python -m xllm query "your query here" --knowledge-base path/to/tables
```

You can also create multiple knowledge bases for different domains or projects:

```bash
# Create a finance-specific knowledge base
python scripts/data_processing_workflow.py --pdf-dir finance/pdfs --tables-dir data/knowledge/finance

# Create a technical knowledge base
python scripts/data_processing_workflow.py --pdf-dir technical/pdfs --tables-dir data/knowledge/technical

# Query the finance knowledge base
python -m xllm query "financial performance trends" --knowledge-base data/knowledge/finance

# Query the technical knowledge base
python -m xllm query "technical specifications" --knowledge-base data/knowledge/technical
```

## Performance Considerations

- **Memory Usage**: Processing large PDFs or many files can require significant memory
- **Processing Time**: The complete workflow can take time for large datasets
- **Storage Requirements**: The backend tables can be large, especially for comprehensive knowledge bases

For large datasets, consider:

- Processing in batches
- Using a machine with sufficient RAM
- Compressing the tables after compilation
