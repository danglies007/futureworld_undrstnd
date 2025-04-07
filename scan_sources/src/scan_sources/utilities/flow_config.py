"""Configuration variables for Scan Sources flow.

This module provides a simple dictionary with all configurable parameters
used throughout the application, making it easier for users to modify settings.
"""

# Configuration variables for Scan Sources flow
FLOW_VARIABLES = {
    # Basic scan parameters
    "target_industry": "Coal Mining",
    "target_market": "Global",
    "time_horizon": "3-5 years",
    
    # Advanced scan parameters
    "max_web_sources": 10,
    "max_document_sources": 0,
    
    # Output configuration
    "output_directory": "outputs/coal_mining_scan",
    
    # Optional specified sources
    "specified_sources": [
        "World Coal Association",
        "International Energy Agency",
        "S&P Global",
        "Mining Technology",
        "McKinsey & Company"
    ]
}
