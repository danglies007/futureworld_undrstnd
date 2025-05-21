#!/bin/bash
# Script to validate requirements.txt before deployment

# Exit on error
set -e

echo "🔍 Validating requirements.txt..."

# Create a temporary virtual environment
echo "Creating temporary virtual environment..."
python -m venv temp_venv
source temp_venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Try to install all requirements
echo "Installing requirements to verify compatibility..."
pip install -r requirements.txt

# Test importing key packages
echo "Testing imports of key packages..."
python -c "
import crewai
import litellm
import openai
import agentops
import pandas
import numpy
import torch
print('✅ All key imports successful')
"

# Verify CrewAI version
CREW_VERSION=$(python -c "import crewai; print(crewai.__version__)")
echo "✅ CrewAI version: $CREW_VERSION"

# Verify LiteLLM version
LITELLM_VERSION=$(python -c "import litellm; print(litellm.__version__)")
echo "✅ LiteLLM version: $LITELLM_VERSION"

# Check for any potential conflicts
echo "Checking for dependency conflicts..."
pip check

# Generate a requirements.txt with pinned versions
echo "Generating requirements-lock.txt with exact versions..."
pip freeze > requirements-lock.txt
echo "✅ Created requirements-lock.txt with exact versions"

# Clean up
deactivate
rm -rf temp_venv

echo "✅ Requirements validation complete!"
echo "You can use requirements-lock.txt for deployment to ensure exact package versions."
