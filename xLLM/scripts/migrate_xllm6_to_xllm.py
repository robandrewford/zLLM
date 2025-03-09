#!/usr/bin/env python3
"""
Migration script to help with the xllm6 to xLLM migration process.

This script helps with:
1. Creating backups of xllm6 code and data
2. Running verification tests
3. Generating reports of differences

Usage:
    python scripts/migrate_xllm6_to_xllm.py [--backup] [--verify] [--report]
"""

import argparse
import datetime
import shutil
import subprocess
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))


def create_backup(backup_dir=None):
    """
    Create a backup of xllm6 code and data.

    Args:
        backup_dir: Directory to store the backup (default: backup_YYYYMMDD_HHMMSS)
    """
    if backup_dir is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"backup_{timestamp}"

    # Create backup directory
    backup_path = Path(__file__).resolve().parent.parent.parent / backup_dir
    backup_path.mkdir(exist_ok=True)

    # Backup xllm6 directory
    xllm6_path = Path(__file__).resolve().parent.parent.parent / "xllm6"
    xllm6_backup_path = backup_path / "xllm6"

    print(f"Creating backup of xllm6 to {xllm6_backup_path}...")
    if xllm6_path.exists():
        shutil.copytree(xllm6_path, xllm6_backup_path)
        print(f"Backup of xllm6 created at {xllm6_backup_path}")
    else:
        print(f"Warning: xllm6 directory not found at {xllm6_path}")

    # Backup NVIDIA MVP backend tables
    nvidia_mvp_path = Path(__file__).resolve().parent.parent.parent / "nvidia-mvp"
    nvidia_mvp_backup_path = backup_path / "nvidia-mvp"

    print(f"Creating backup of NVIDIA MVP backend tables to {nvidia_mvp_backup_path}...")
    if nvidia_mvp_path.exists():
        shutil.copytree(nvidia_mvp_path, nvidia_mvp_backup_path)
        print(f"Backup of NVIDIA MVP backend tables created at {nvidia_mvp_backup_path}")
    else:
        print(f"Warning: NVIDIA MVP directory not found at {nvidia_mvp_path}")

    return backup_path


def run_verification(verbose=False, test_queries_file=None, copy_missing=False):
    """
    Run verification tests.

    Args:
        verbose: Whether to print detailed information
        test_queries_file: Path to file with test queries
        copy_missing: Whether to copy missing data files from xllm6 to xLLM

    Returns:
        True if verification passed, False otherwise
    """
    verify_script = Path(__file__).resolve().parent / "verify_xllm_vs_xllm6.py"

    cmd = [sys.executable, str(verify_script)]
    if verbose:
        cmd.append("--verbose")
    if test_queries_file:
        cmd.extend(["--test-queries-file", test_queries_file])
    if copy_missing:
        cmd.append("--copy-missing")

    print(f"Running verification: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)

    print(result.stdout)
    if result.stderr:
        print(f"Errors:\n{result.stderr}")

    return result.returncode == 0


def generate_report(output_file=None):
    """
    Generate a report of differences between xllm6 and xLLM.

    Args:
        output_file: File to write the report to (default: migration_report_YYYYMMDD_HHMMSS.md)
    """
    if output_file is None:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"migration_report_{timestamp}.md"

    output_path = Path(__file__).resolve().parent.parent / output_file

    print(f"Generating migration report to {output_path}...")

    # Run verification with verbose output and capture results
    verify_script = Path(__file__).resolve().parent / "verify_xllm_vs_xllm6.py"
    cmd = [sys.executable, str(verify_script), "--verbose"]
    result = subprocess.run(cmd, capture_output=True, text=True)

    # Generate report
    with open(output_path, "w") as f:
        f.write("# xllm6 to xLLM Migration Report\n\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("## Verification Results\n\n")
        f.write("```\n")
        f.write(result.stdout)
        f.write("```\n\n")

        if result.stderr:
            f.write("### Errors\n\n")
            f.write("```\n")
            f.write(result.stderr)
            f.write("```\n\n")

        f.write("## Migration Status\n\n")
        f.write("- [ ] Knowledge Base Construction\n")
        f.write("- [ ] Query Processing\n")
        f.write("- [ ] NVIDIA-specific Functionality\n")
        f.write("- [ ] Performance Metrics\n\n")

        f.write("## Notes\n\n")
        f.write("Add any notes or observations here.\n\n")

        f.write("## Next Steps\n\n")
        f.write("1. Address any issues identified in the verification\n")
        f.write("2. Re-run verification to confirm fixes\n")
        f.write("3. Complete the migration checklist\n")

    print(f"Migration report generated at {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="xllm6 to xLLM migration helper")
    parser.add_argument(
        "--backup", action="store_true", help="Create a backup of xllm6 code and data"
    )
    parser.add_argument("--verify", action="store_true", help="Run verification tests")
    parser.add_argument("--report", action="store_true", help="Generate a report of differences")
    parser.add_argument(
        "--copy-missing",
        "-c",
        action="store_true",
        help="Copy missing data files from xllm6 to xLLM",
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Print detailed information")
    parser.add_argument("--test-queries-file", type=str, help="Path to file with test queries")
    parser.add_argument("--output-file", type=str, help="File to write the report to")
    parser.add_argument("--backup-dir", type=str, help="Directory to store the backup")
    args = parser.parse_args()

    # If no actions specified, show help
    if not (args.backup or args.verify or args.report or args.copy_missing):
        parser.print_help()
        return 1

    # Create backup
    if args.backup:
        backup_path = create_backup(args.backup_dir)
        print(f"Backup created at {backup_path}")

    # Copy missing files
    if args.copy_missing:
        print("Copying missing data files...")
        verify_script = Path(__file__).resolve().parent / "verify_xllm_vs_xllm6.py"
        cmd = [sys.executable, str(verify_script), "--copy-missing", "--init-only"]
        if args.verbose:
            cmd.append("--verbose")

        result = subprocess.run(cmd, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(f"Errors:\n{result.stderr}")

    # Run verification
    if args.verify:
        success = run_verification(args.verbose, args.test_queries_file, args.copy_missing)
        if not success:
            print("Verification failed. See output for details.")
            return 1
        print("Verification passed!")

    # Generate report
    if args.report:
        report_path = generate_report(args.output_file)
        print(f"Report generated at {report_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
