#!/bin/bash
# Script to set up the development environment for xLLM

# Exit on error
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    # Add uv to PATH for this session
    export PATH="$HOME/.cargo/bin:$PATH"
fi

# Create virtual environment with uv
echo "Creating virtual environment with uv..."
uv venv

# Activate virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install required dependencies
echo "Installing required dependencies..."
uv pip install requests numpy pymupdf autocorrect pytest pytest-cov pre-commit ruff pyright

# Install package in development mode
echo "Installing package in development mode..."
uv pip install -e .

# Set up pre-commit hooks
echo "Setting up pre-commit hooks..."
pre-commit install

# Create necessary data directories
echo "Creating data directories..."
mkdir -p data/raw data/processed data/knowledge

# Print success message
echo "Development environment setup complete!"
echo "To activate the virtual environment, run: source .venv/bin/activate"
echo "To run type checking, use: pyright"
