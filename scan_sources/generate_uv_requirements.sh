#!/bin/bash
# Script to generate clean requirements.txt using UV

# Exit on error
set -e

echo "🔍 Generating clean requirements.txt using UV..."

# Check if UV is installed
if ! command -v uv &> /dev/null; then
    echo "UV is not installed. Installing UV..."
    pip install uv
fi

# Create a temporary virtual environment
echo "Creating temporary virtual environment..."
uv venv temp_venv_uv
source temp_venv_uv/bin/activate

# Install current requirements
echo "Installing current packages..."
uv pip install -r requirements.txt

# Generate clean requirements file
echo "Generating clean requirements.txt with UV..."
uv pip freeze > requirements.uv.txt

# Find key packages and their versions
echo "Key package versions:"
grep -E "crewai|litellm|openai|agentops" requirements.uv.txt

# Compare with current requirements
echo "Comparing with current requirements.txt..."
DIFF_COUNT=$(diff -y --suppress-common-lines requirements.txt requirements.uv.txt | wc -l)
echo "Found $DIFF_COUNT differences between requirements files"

# Clean up
deactivate
rm -rf temp_venv_uv

echo "✅ Generated requirements.uv.txt with UV"
echo "Review the file and if satisfied, replace your requirements.txt with it:"
echo "cp requirements.uv.txt requirements.txt"
