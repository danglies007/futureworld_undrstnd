#!/bin/bash

# Activate the scan-sources virtual environment
SOURCE_VENV="/Users/alex/Documents/Coding/undrstnd/scan_sources/.venv/bin/activate"

if [ -f "$SOURCE_VENV" ]; then
    echo "Activating scan-sources virtual environment..."
    source "$SOURCE_VENV"
else
    echo "Warning: scan-sources virtual environment not found at $SOURCE_VENV"
    echo "Using current Python environment instead"
    
    # Install requirements if needed
    pip install -r requirements.txt
fi

# Run the Streamlit app
streamlit run src/app.py
