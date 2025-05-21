#!/bin/bash
# Script to generate requirements.txt directly from UV's current environment

# Exit on error
set -e

echo "🔍 Generating requirements.txt directly from UV's current environment..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing UV..."
    pip install uv
fi

# Get the actual UV list from the current environment
echo "Getting package list directly from UV..."
uv pip list --format=freeze > requirements.uv.actual.txt

# Count packages
PACKAGE_COUNT=$(wc -l < requirements.uv.actual.txt)
echo "✅ Found $PACKAGE_COUNT packages in UV environment"

# Check for known conflicts
if grep -q "embedchain==0.1.125" requirements.uv.actual.txt && grep -q "chromadb==0.6" requirements.uv.actual.txt; then
    echo "⚠️ Detected conflict: embedchain==0.1.125 requires chromadb<0.6.0"
    echo "  Solution: Run ./fix_requirements.py to fix this conflict"
fi

echo "✅ Generated requirements.uv.actual.txt with actual UV packages"
echo ""
echo "To use this file for deployment:"
echo "cp requirements.uv.actual.txt requirements.txt"
