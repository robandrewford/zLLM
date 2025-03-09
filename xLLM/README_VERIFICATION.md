# xLLM Verification

This directory contains scripts to verify that the xLLM functionality works correctly.

## Verification Script

The main verification script is `verify_xllm.py`. This script verifies:

1. Knowledge base construction
2. Query processing and results
3. Performance metrics

### Usage

```bash
# Basic usage
python scripts/verify_xllm.py

# With verbose output
python scripts/verify_xllm.py --verbose

# With custom test queries file
python scripts/verify_xllm.py --test-queries-file scripts/test_queries.txt
```

### Command-line Options

- `--verbose`: Print detailed information about the verification process
- `--test-queries-file PATH`: Path to a file containing test queries (one per line)

### Test Queries File

A sample test queries file is provided at `scripts/test_queries.txt`. You can create your own test queries file with the following format:

```text
# Comments start with #
query 1
query 2
query 3
```

## Verification Process

The verification script performs the following checks:

### 1. Knowledge Base Construction

Verifies that the knowledge base can be constructed correctly:

- Dictionary table
- Embeddings table
- Word hash table
- Hash see table
- Hash related table
- Hash category table
- N-grams table
- Compressed tables

### 2. Query Processing

Tests a set of queries and verifies the results:

- Basic keyword queries
- Multi-token word queries
- Relevance scoring
- Result formatting

### 3. Performance Metrics

Measures performance metrics:

- Knowledge base construction time
- Query response time
- Memory usage

## Interpreting Results

The script outputs a summary of the verification results, including:

- Overall pass/fail status
- Detailed information about any issues found
- Performance metrics

Example output:

```text
Verification PASSED
```

If any verification fails, the script will provide details about the failures:

```text
Verification FAILED
Knowledge base errors: 1
Query processing errors: 0
```

## Verification Report

The verification script generates a detailed report of the verification results. This report includes:

- Overall status
- Knowledge base verification results
- Query processing verification results
- Performance metrics

Example report:

```markdown
# xLLM Verification Report

Generated on: 2025-03-09 14:30:45

## Overall Status: PASS

## Knowledge Base Verification

Status: PASS
Time taken: 0.25 seconds
Knowledge base path: xLLM/data/knowledge/test/knowledge_base.pkl

## Query Processing Verification

Status: PASS
Time taken: 1.50 seconds
Queries processed: 5

## Query Results

### Query: machine learning
Time taken: 0.30 seconds
Result:

```text
Machine learning is a field of artificial intelligence that uses statistical techniques to give computer systems the ability to "learn" from data, without being explicitly programmed.
```

## Troubleshooting

If the verification fails, check the following:

1. Ensure that xLLM is properly installed and configured
2. Check that the data paths are correct
3. Review the detailed errors to identify specific issues
4. Make necessary adjustments to the xLLM implementation
5. Re-run the verification script to confirm fixes

### Common Issues and Solutions

#### Missing Knowledge Base

If the verification fails because the knowledge base is missing, you can:

1. Check that the knowledge base file exists at the expected location
2. Run the knowledge base construction script to create it
3. Use the test knowledge base if available

#### Module Import Errors

If the verification fails because of module import errors, check that:

1. The xLLM package is properly installed
2. The module structure matches the expected structure
3. The necessary dependencies are installed

#### Query Processing Errors

If the verification fails because of query processing errors, check that:

1. The query processing implementation is correct
2. The knowledge base is correctly loaded and used
3. The relevance scoring algorithm is working as expected

## Adding Custom Verification Tests

To add custom verification tests:

1. Create a new test queries file with your custom queries
2. Run the verification script with your custom test queries file
3. Review the results and make necessary adjustments

## Migration Completion

The migration from xllm6 to xLLM has been completed. The xllm6 code has been removed, and all functionality has been migrated to xLLM. The verification script has been updated to verify the xLLM functionality without comparing it to xllm6.

For more information about the migration process, see the migration checklist at `scripts/xllm_migration_checklist.md`.
