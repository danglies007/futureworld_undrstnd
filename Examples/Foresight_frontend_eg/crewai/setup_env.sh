#!/bin/bash

# Activate the virtual environment
source .venv/bin/activate

# Install required dependencies if not already installed
pip install -e .

# Print the Python path
echo "Python path:"
python -c "import sys; print(sys.path)"

# Check if crewai is installed
echo "Checking for crewai package:"
python -c "import crewai; print(f'crewai version: {crewai.__version__}')" || echo "crewai not found"

# Make the script executable
chmod +x setup_env.sh
