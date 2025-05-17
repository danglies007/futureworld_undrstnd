# Configuration for company analysis research

import os
from datetime import datetime

RESEARCH_INPUTS = {
    # Target company details
    "company_name": "Emirates NBD",
    "ticker_symbol": "ENBD",
    "industry": "Banking",
    "specialisation": "CompanyAnalysis",
    "company_name_short": "ENBD",
    
    # Analysis parameters
    "date": datetime.now().strftime('%d %B %Y'),
    "year": datetime.now().strftime('%Y'),
    "time_period": "2022-2025",
    "focus_areas": [],
    "competitor_names": [],
    
    # Analysis depth
    "detail_level": "comprehensive",  # can be 'brief', 'standard', or 'comprehensive'
    "audience": "Expert Investors",
    
    # Optional parameters
    "include_esg_analysis": True,
    "include_scenario_planning": True,
    "include_strategic_recommendations": True
}
