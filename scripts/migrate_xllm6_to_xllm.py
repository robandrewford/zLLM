#!/usr/bin/env python3
"""
Migration script to help transition from xllm6 to xLLM.

This script helps with:
1. Backing up xllm6 code and data
2. Converting xllm6 data tables to xLLM format
3. Converting NVIDIA MVP backend tables to xLLM format
4. Cleaning up after successful migration
"""

import argparse
import logging
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("migrate_xllm")

def backup_xllm6(xllm6_dir, backup_dir):
    """Backup xllm6 code and data."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"xllm6_backup_{timestamp}")

    logger.info(f"Backing up xllm6 to {backup_path}")

    # Create backup directory
    os.makedirs(backup_path, exist_ok=True)

    # Copy xllm6 directory to backup
    shutil.copytree(xllm6_dir, os.path.join(backup_path, "xllm6"), dirs_exist_ok=True)

    logger.info(f"Backup completed successfully")
    return backup_path

def backup_nvidia_mvp(nvidia_mvp_dir, backup_dir):
    """Backup NVIDIA MVP backend tables."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = os.path.join(backup_dir, f"nvidia_mvp_backup_{timestamp}")

    logger.info(f"Backing up NVIDIA MVP backend tables to {backup_path}")

    # Create backup directory
    os.makedirs(backup_path, exist_ok=True)

    # Copy NVIDIA MVP backend tables to backup
    backend_tables_dir = os.path.join(nvidia_mvp_dir, "backend_tables")
    if os.path.exists(backend_tables_dir):
        shutil.copytree(backend_tables_dir, os.path.join(backup_path, "backend_tables"), dirs_exist_ok=True)
        logger.info(f"Backed up NVIDIA MVP backend tables")
    else:
        logger.warning(f"NVIDIA MVP backend tables directory not found: {backend_tables_dir}")

    logger.info(f"Backup completed successfully")
    return backup_path

def convert_data_tables(xllm6_dir, xllm_dir):
    """Convert xllm6 data tables to xLLM format."""
    # List of table files to convert
    table_files = [
        "dictionary.txt",
        "embeddings.txt",
        "word_hash.txt",
        "hash_see.txt",
        "hash_related.txt",
        "hash_category.txt",
        "ngrams_table.txt",
        "word2_pairs.txt",
        "url_map.txt",
        "arr_url.txt",
        "compressed_ngrams_table.txt",
        "compressed_word2_hash.txt",
    ]

    # Create xLLM data directory if it doesn't exist
    os.makedirs(xllm_dir, exist_ok=True)

    converted_files = []

    for table in table_files:
        xllm6_file = os.path.join(xllm6_dir, f"xllm6_{table}")
        xllm_file = os.path.join(xllm_dir, f"xllm_{table}")

        if os.path.exists(xllm6_file):
            logger.info(f"Converting {xllm6_file} to {xllm_file}")

            # For simple conversion, just copy the file with the new name
            # In a real scenario, you might need to transform the data format
            shutil.copy2(xllm6_file, xllm_file)
            converted_files.append(xllm_file)
        else:
            logger.warning(f"Source file {xllm6_file} not found, skipping")

    logger.info(f"Converted {len(converted_files)} data tables")
    return converted_files

def convert_nvidia_backend_tables(nvidia_mvp_dir, xllm_dir):
    """Convert NVIDIA MVP backend tables to xLLM format."""
    # Create xLLM nvidia data directory if it doesn't exist
    nvidia_dir = os.path.join(xllm_dir, "nvidia")
    os.makedirs(nvidia_dir, exist_ok=True)

    # Source directory for NVIDIA MVP backend tables
    backend_tables_dir = os.path.join(nvidia_mvp_dir, "backend_tables")

    if not os.path.exists(backend_tables_dir):
        logger.warning(f"NVIDIA MVP backend tables directory not found: {backend_tables_dir}")
        return []

    # Get all files in the backend tables directory
    backend_files = [f for f in os.listdir(backend_tables_dir) if os.path.isfile(os.path.join(backend_tables_dir, f))]

    converted_files = []

    for file in backend_files:
        source_file = os.path.join(backend_tables_dir, file)
        # Keep the same filename but store in the nvidia subdirectory
        target_file = os.path.join(nvidia_dir, file)

        logger.info(f"Converting {source_file} to {target_file}")

        # Copy the file to the new location
        shutil.copy2(source_file, target_file)
        converted_files.append(target_file)

    logger.info(f"Converted {len(converted_files)} NVIDIA MVP backend tables")
    return converted_files

def clean_up_xllm6(xllm6_dir, dry_run=True):
    """Clean up xllm6 code after successful migration."""
    if dry_run:
        logger.info(f"DRY RUN: Would remove xllm6 directory: {xllm6_dir}")
        return

    logger.info(f"Removing xllm6 directory: {xllm6_dir}")

    try:
        shutil.rmtree(xllm6_dir)
        logger.info(f"Successfully removed xllm6 directory")
    except Exception as e:
        logger.error(f"Error removing xllm6 directory: {e}")

def clean_up_nvidia_mvp(nvidia_mvp_dir, dry_run=True):
    """Clean up NVIDIA MVP backend tables after successful migration."""
    if dry_run:
        logger.info(f"DRY RUN: Would remove NVIDIA MVP backend tables directory: {nvidia_mvp_dir}/backend_tables")
        return

    backend_tables_dir = os.path.join(nvidia_mvp_dir, "backend_tables")

    if os.path.exists(backend_tables_dir):
        logger.info(f"Removing NVIDIA MVP backend tables directory: {backend_tables_dir}")

        try:
            shutil.rmtree(backend_tables_dir)
            logger.info(f"Successfully removed NVIDIA MVP backend tables directory")
        except Exception as e:
            logger.error(f"Error removing NVIDIA MVP backend tables directory: {e}")
    else:
        logger.warning(f"NVIDIA MVP backend tables directory not found: {backend_tables_dir}")

def main():
    """Main function to migrate from xllm6 to xLLM."""
    parser = argparse.ArgumentParser(description="Migrate from xllm6 to xLLM")
    parser.add_argument("--xllm6-dir", type=str, default="xllm6",
                        help="Directory containing xllm6 files")
    parser.add_argument("--nvidia-mvp-dir", type=str, default="nvidia-mvp",
                        help="Directory containing NVIDIA MVP files")
    parser.add_argument("--xllm-dir", type=str, default="xLLM/data/knowledge",
                        help="Directory to store xLLM knowledge base files")
    parser.add_argument("--backup-dir", type=str, default="backups",
                        help="Directory to store backups")
    parser.add_argument("--clean-up", action="store_true",
                        help="Clean up xllm6 code after successful migration")
    parser.add_argument("--clean-up-nvidia", action="store_true",
                        help="Clean up NVIDIA MVP backend tables after successful migration")
    parser.add_argument("--force", action="store_true",
                        help="Force clean up without confirmation")
    parser.add_argument("--skip-xllm6", action="store_true",
                        help="Skip xllm6 migration and only process NVIDIA MVP backend tables")
    parser.add_argument("--skip-nvidia", action="store_true",
                        help="Skip NVIDIA MVP backend tables migration and only process xllm6")
    args = parser.parse_args()

    # Create backup directory
    os.makedirs(args.backup_dir, exist_ok=True)

    xllm6_backup_path = None
    nvidia_backup_path = None
    xllm6_converted_files = []
    nvidia_converted_files = []

    # Process xllm6 if not skipped
    if not args.skip_xllm6:
        # Check if xllm6 directory exists
        if not os.path.exists(args.xllm6_dir):
            logger.error(f"xllm6 directory not found: {args.xllm6_dir}")
            if args.skip_nvidia:
                return 1
        else:
            # Backup xllm6
            xllm6_backup_path = backup_xllm6(args.xllm6_dir, args.backup_dir)

            # Convert data tables
            xllm6_converted_files = convert_data_tables(args.xllm6_dir, args.xllm_dir)

            # Clean up xllm6 if requested
            if args.clean_up:
                if args.force:
                    clean_up_xllm6(args.xllm6_dir, dry_run=False)
                else:
                    confirmation = input(f"Are you sure you want to remove the xllm6 directory? This cannot be undone. (y/N): ")
                    if confirmation.lower() == 'y':
                        clean_up_xllm6(args.xllm6_dir, dry_run=False)
                    else:
                        logger.info("Clean up of xllm6 aborted")

    # Process NVIDIA MVP backend tables if not skipped
    if not args.skip_nvidia:
        # Check if NVIDIA MVP directory exists
        if not os.path.exists(args.nvidia_mvp_dir):
            logger.error(f"NVIDIA MVP directory not found: {args.nvidia_mvp_dir}")
            if args.skip_xllm6 or not os.path.exists(args.xllm6_dir):
                return 1
        else:
            # Backup NVIDIA MVP backend tables
            nvidia_backup_path = backup_nvidia_mvp(args.nvidia_mvp_dir, args.backup_dir)

            # Convert NVIDIA MVP backend tables
            nvidia_converted_files = convert_nvidia_backend_tables(args.nvidia_mvp_dir, args.xllm_dir)

            # Clean up NVIDIA MVP backend tables if requested
            if args.clean_up_nvidia:
                if args.force:
                    clean_up_nvidia_mvp(args.nvidia_mvp_dir, dry_run=False)
                else:
                    confirmation = input(f"Are you sure you want to remove the NVIDIA MVP backend tables? This cannot be undone. (y/N): ")
                    if confirmation.lower() == 'y':
                        clean_up_nvidia_mvp(args.nvidia_mvp_dir, dry_run=False)
                    else:
                        logger.info("Clean up of NVIDIA MVP backend tables aborted")

    # Print summary
    logger.info(f"Migration completed successfully")

    if xllm6_backup_path:
        logger.info(f"xllm6 backup saved to: {xllm6_backup_path}")
        logger.info(f"Converted {len(xllm6_converted_files)} xllm6 data tables to xLLM format")

    if nvidia_backup_path:
        logger.info(f"NVIDIA MVP backup saved to: {nvidia_backup_path}")
        logger.info(f"Converted {len(nvidia_converted_files)} NVIDIA MVP backend tables to xLLM format")

    return 0

if __name__ == "__main__":
    sys.exit(main())
