# Configuration variables for Foresight flow

FLOW_VARIABLES = {
    "sector": "Mining",  # Can be changed to any sector focus
    "report_type": "Strategic Foresight Report",
    "topic": "Future of Mining", # OPTIONAL, Any areas or important themes that should be considered
    "year": 2025, # What is the current year
    "audience_level": "Strategic Decision Makers", # OPTIONAL, Can be changed to any audience level focus
    "company": "Exxaro Resources Limited", # OPTIONAL, Can be changed to any company focus
    "company_short": "Exxaro Resources Limited", # OPTIONAL, Short name used for naming
    "geography": "Global", # Can be changed to any geography focus
    "specified_sources": [  # List of required sources to be consulted (can be names or URLs)
        "Harvard Business Review",
        "https://hbr.org",
        "McKinsey Global Institute",
        "Gartner",
        "World Economic Forum",
        "https://ftsg.com/"
    ]
}