"""Command modules for the xLLM CLI."""

from xllm.cli.commands.build_kb_command import register as register_build_kb
from xllm.cli.commands.build_taxonomy_command import register as register_build_taxonomy
from xllm.cli.commands.crawl_command import register as register_crawl
from xllm.cli.commands.process_pdf_command import register as register_process_pdf
from xllm.cli.commands.process_enterprise_pdf_command import (
    register as register_process_enterprise_pdf,
)
from xllm.cli.commands.query_command import register as register_query
from xllm.cli.commands.query_enterprise_kb_command import register as register_query_enterprise_kb

# Re-export for convenience
build_kb_command = register_build_kb
build_taxonomy_command = register_build_taxonomy
crawl_command = register_crawl
process_pdf_command = register_process_pdf
process_enterprise_pdf_command = register_process_enterprise_pdf
query_command = register_query
query_enterprise_kb_command = register_query_enterprise_kb

__all__ = [
    "build_kb_command",
    "build_taxonomy_command",
    "crawl_command",
    "process_pdf_command",
    "process_enterprise_pdf_command",
    "query_command",
    "query_enterprise_kb_command",
]
