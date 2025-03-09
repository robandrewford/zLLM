# xllm6 to xLLM Migration Verification

This directory contains scripts to verify the migration from xllm6 to xLLM.

## Verification Script

The main verification script is `verify_xllm_vs_xllm6.py`. This script tests various aspects of both implementations to ensure that the migration from xllm6 to xLLM maintains functional equivalence.

### What the Script Verifies

The script verifies the following aspects:

1. **Knowledge Base Construction**: Ensures that the knowledge base construction process produces equivalent results.
2. **Query Processing**: Verifies that queries return the same or equivalent results.
3. **Data Tables**: Compares the structure and content of data tables.
4. **NVIDIA MVP Backend**: Verifies NVIDIA-specific functionality and backend tables.
5. **Performance**: Compares performance metrics between the two implementations.

### Usage

```bash
python scripts/verify_xllm_vs_xllm6.py [options]
```

#### Options

- `--output`, `-o`: Output file for the verification report (default: `verification_report.md`)
- `--verbose`, `-v`: Enable verbose output

### Output

The script generates a comprehensive Markdown report that includes:

- A summary of all tests
- Detailed results for each test category
- Differences found between the implementations
- Performance metrics

### Example

```bash
# Run the verification script with default options
python scripts/verify_xllm_vs_xllm6.py

# Run with verbose output and custom report location
python scripts/verify_xllm_vs_xllm6.py --verbose --output custom_report.md
```

## Interpreting the Results

The verification report categorizes tests as either PASS or FAIL:

- ✅ PASS: The test passed, indicating functional equivalence.
- ❌ FAIL: The test failed, indicating a difference that needs to be addressed.

For each failed test, the report includes details about the differences found, which can help identify what needs to be fixed in the xLLM implementation.

## Completion Criteria

The migration is considered complete when:

1. All core functionality tests pass
2. All NVIDIA MVP functionality tests pass
3. All output verification tests pass
4. Performance is equivalent or better
5. All additional features are implemented and tested
6. Documentation is updated to reflect the new system

## Troubleshooting

If you encounter issues with the verification script:

1. Check that both xllm6 and xLLM are properly installed and configured.
2. Ensure that all required data files are present.
3. Check the log file (`xllm_verification.log`) for detailed error messages.
4. If specific tests are failing, examine the differences reported to understand what needs to be fixed.

## Notes on Intentional Differences

If there are intentional differences between xllm6 and xLLM (e.g., improvements or bug fixes), these should be documented in the migration checklist (`xllm_migration_checklist.md`).
