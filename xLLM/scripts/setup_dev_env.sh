#!/bin/bash
# Script to set up the development environment for xLLM

# Exit on error
set -e

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Create a virtual environment using uv
echo "Creating virtual environment with uv..."
uv venv

# Activate the virtual environment
echo "Activating virtual environment..."
source .venv/bin/activate

# Install the package in development mode using uv
echo "Installing package in development mode with uv..."
uv pip install -e ".[dev,docs]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create data directories
echo "Creating data directories..."
mkdir -p data/raw data/processed data/knowledge

# Print success message
echo "Development environment set up successfully!"
echo "To activate the virtual environment, run:"
echo "  source .venv/bin/activate" 