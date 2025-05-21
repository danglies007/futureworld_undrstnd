# Undrstnd AI Research Platform Frontend

A Streamlit-based frontend for the Undrstnd AI Research Platform that provides interfaces for:

- Market Forces Scanner
- Competitor Analysis

## Setup

1. Install the required dependencies:

```bash
pip install -r requirements.txt
```

2. Ensure that the main Undrstnd codebase is properly set up and accessible.

## Running the Frontend

From the frontend directory, run:

Run the script

```bash
cd /Users/alex/Documents/Coding/undrstnd && sh frontend/run_frontend.sh
```


```bash
streamlit run src/app.py
```

## Logging

To run the log analyzer

```
cd /Users/alex/Documents/Coding/undrstnd && python -m frontend.src.utils.log_analyzer logs/process_output_20250519_171256.log --report
```

## Features

### Market Forces Scanner

- Configure research parameters including topic, market, and business
- Specify custom sources or use predefined source categories
- Set minimum and maximum number of sources to analyze
- Define specific points of interest for the research
- View generated reports directly in the interface

### Competitor Analysis

- Configure company details and analysis parameters
- Specify competitors and focus areas
- Set analysis options including ESG analysis, scenario planning, and strategic recommendations
- View internal, external, and integrated analysis reports

## Future Development

This frontend is designed to be a starting point that can be migrated to a more robust solution in the future. The dedicated frontend folder structure allows for easy expansion and migration to other frameworks like React, Vue, or Angular when needed.
