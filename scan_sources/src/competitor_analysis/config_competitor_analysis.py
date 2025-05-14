# Configuration for company analysis research

import os
from datetime import datetime

RESEARCH_INPUTS = {
    # Target company details
    "company_name": "First Abu Dhabi bank",
    "ticker_symbol": "FAB",
    "industry": "Banking",
    "specialisation": "CompanyAnalysis",
    "company_name_short": "FAB",
    
    # Analysis parameters
    "date": datetime.now().strftime('%d %B %Y'),
    "time_period": "2021-2025",
    "focus_areas": [],
    "competitor_names": [],
    
    # Analysis depth
    "detail_level": "comprehensive",  # can be 'brief', 'standard', or 'comprehensive'
    
    # Optional parameters
    "include_esg_analysis": True,
    "include_scenario_planning": True,
    "include_strategic_recommendations": True
}
