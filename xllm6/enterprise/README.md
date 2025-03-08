# Project Overview

## Understanding the Codebase Structure

This codebase represents a sophisticated information retrieval and processing system with several interconnected components. Here's how they fit together:

### 1. Web Crawler with Tor Browsing Features

The web crawler functionality is primarily implemented in:

- **`crawl_directory.py`**: The main crawler that systematically navigates through Wolfram Alpha's math website, specifically targeting the mathematics categories and content.
- **`tor_crawling.py`**: A supplementary tool that enables crawling through Tor network for anonymity and to avoid IP blocking.
- **`data.py`**: Provides additional proxy capabilities for web crawling.

The crawler outputs are stored in:

- **`crawl_dump_wolfram/`**: Contains the crawled content from Wolfram Alpha, organized in zip files.
- Various log files like `crawl_log_all.txt`, `crawl_content_log.txt`, etc., which track the crawling process.

### 2. PDF Parser

The PDF parsing functionality is implemented in:

- **`xllm6/PDF_Chunking_Nvidia.py`**: A specialized parser for Nvidia financial reports that extracts structured data from PDFs. This parser can identify tables, titles, lists, and other structured content in PDFs.

### 3. Data Enrichment/Augmentation

The data augmentation component is stored in:

- **`data_augmentation/`**: Contains additional data sources (LaTeX files of books, academic papers) to enrich the knowledge base beyond what was crawled from Wolfram Alpha. These sources include mathematical textbooks and papers that complement the web-crawled content.

### 4. LLM Processing Components

The system has evolved through several versions:

#### LLM5

- Located in `llm5/`
- Processes webpages from Wolfram Alpha's Probability & Statistics category
- Creates knowledge tables and provides search functionality
- According to the README, this is an older version that's no longer maintained

#### XLLM5

- Located in `xllm5/`
- An improved version of LLM5 with faster execution, smaller tables, and simplified architecture
- Uses a more efficient data structure (hash of hash instead of hash of lists)

#### XLLM6

- Located in `xllm6/`
- The latest evolution with additional features like "x-embeddings" (multi-token words)
- Includes specialized functionality for processing Nvidia financial reports
- Contains the PDF parser for Nvidia documents

### 5. Nvidia MVP

- Located in `nvidia-mvp/`
- A specialized implementation focused on Nvidia financial reports
- Contains backend tables generated from parsing Nvidia PDFs
- Part of an "Enterprise xLLM" solution mentioned in the README

## How These Components Work Together

The system functions as an integrated pipeline:

1. **Data Collection**: The web crawler collects mathematical content from Wolfram Alpha, while the PDF parser extracts information from Nvidia financial reports.

2. **Data Processing**: The collected data is processed and structured into various tables and knowledge bases.

3. **Data Enrichment**: Additional sources from the `data_augmentation` directory supplement the crawled data.

4. **Knowledge Representation**: The processed data is organized into efficient data structures (primarily hash tables) by the LLM components.

5. **Query Processing**: The system can answer queries using the knowledge base it has built.

## Architecture Notes

- **Integrated System**: The web crawler, PDF parser, and LLM components are part of an integrated system, not separate functions. They work together to build a comprehensive knowledge base.

- **Evolution of Components**: XLLM5 is indeed a prior version of XLLM6, with XLLM6 adding new features like x-embeddings and improved architecture.

- **Nvidia Focus**: The Nvidia PDF parser is specifically part of XLLM6 and the Nvidia MVP, showing a specialized application of the technology for financial reports.

- **Database Compilation**: The database is compiled from both the Wolfram Alpha crawl and the Nvidia PDF parsing, not just the PDF parser. However, there are separate knowledge bases for different domains.

- **Purpose**: The overall system is a specialized information retrieval and question-answering system focused on mathematical and financial domains, with an emphasis on efficient knowledge representation and retrieval.

The codebase represents a sophisticated approach to domain-specific knowledge extraction, representation, and retrieval that combines web crawling, PDF parsing, and efficient data structures to create a specialized question-answering system.

## Enterprise Version

The tech doc for `xllm-enterprise-v2.py` is [xllm-enterprise-v2.pdf](https://github.com/robandrewford/zLLM/blob/main/xllm6/enterprise/xllm-enterprise-v2.pdf). The previous version (xllm-enterprise.py) is no longer maintained. I also created a library `xllm_enterprise_util.py`. Both `xllm-enterprise-v2-user.py` and `xllm-enterprise-dev.py` use that library. The former is essentially the same as xllm-enterprise-v2.py but much shorter since all the functions have been moved to the library. The latter also uses the same algorithms and architecture with recent additions (relevancy scores) but it serves a different purpose: testing a large number of prompts.

All input data (repository.txt augmented with repository2.txt) comes from one part of an anonymized corporate corpus, dealing with one sub-LLM. The augmented data (concatenation of the two files) is in repository3.txt.

**Notes**:

- `xllm-enterprise-v2-user.py` calls the real-time fine-tuning function. The user enters one prompt at a time, from the keyboard, including command options.
- `xllm-enterprise-v2-dev.py` does not call the real-time fine-tuning function. The test prompts with correct answers are loaded from a text file: [enterprise_sample_prompts.txt](https://github.com/robandrewford/zLLM/blob/main/xllm6/enterprise/enterprise_sample_prompts.txt). A prompt and corresponding answer are in a same row, separated by " | ". For documentation, see [LLM-scores.pdf](https://github.com/robandrewford/zLLM/blob/main/xllm6/enterprise/LLM-scores.pdf).

**More documentation**:

All the material is documented in my book "Building Disruptive AI & LLM Apps from Scratch", available on MLtechniques.com e-store, [here](https://mltechniques.com/shop/).

Additional resources:

- See [here](https://mltblog.com/47DisG5).
