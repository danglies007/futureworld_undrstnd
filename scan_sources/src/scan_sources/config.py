#config.py

import os
from datetime import datetime

# Sources for research
SOURCES_CONSULTING_FIRMS = [
    "https://www.mckinsey.com",
    "https://www.bain.com",
    "https://www.bcg.com",
]

SOURCES_GOV_NON_PROFIT = [
    "https://www.weforum.org",
    "https://intelligence.weforum.org/",
    "https://www.imf.org",
    "https://www.consilium.europa.eu/en/",
]

SOURCES_NEWS_SOURCES = [
    "Financial Times",
    "The Wall Street Journal",
    "Reuters Business",
    "CNBC",
    "Business Insider",
    "The Information",
    "The Times – Business Section",
    "The Economist",
    "The Times",
    "Bloomberg",
    "Forbes",
    "Bloomberg Businessweek",
    "Fast Company",
    "Inc."
]

SOURCES_ACADEMIC = [
    "technology review",
    "newscientist",
    "MIT Sloan Management Review",
    "Harvard Business Review"
]

SOURCES_FUTURISTS = [
    "Thomas Frey",
    "Gerd Leonhard",
    "Daniel Burrus",
    "Peter Diamandis", 
    "Ian Pearson", 
    "Matthew Griffin", 
    "Ray Kurzweil", 
    "Richard Van Hooijdonk",
    "Amy Webb"
]

SOURCES_VENTURE_CAPITAL = [
    "Andreessen Horowitz",
    "ycombinator",
    "cbinsights",
    "pitchbook",
    "crunchbase",
    "sequoia capital",
    "General Catalyst",
    "Khosla Ventures"
]

BUSINESS_INTELLIGENCE_SOURCES = [
    "Pitchbook",
    "Crunchbase",
    "CB Insights",
    "Tracxn",
    "PrivCo",
    "Owler",
    "Dealroom",
    "Preqin",
    "S&P Capital IQ",
    "FactSet"
]

SOURCES_FUTURISTS_OLD = [
    "Ian Pearson",
    "Matthew Griffin",
    "Ray Kurzweil",
    "Richard Van Hooijdonk",
    "Amy Webb",
    "Thomas Frey",
    "Gerd Leonhard",
    "Daniel Burrus"
    "Peter Diamandis"
]

SOURCES_PATENTS = [
    "https://patents.google.com",
    "https://www.uspto.gov",
    "https://www.lens.org",
    "https://www.epo.org/en",
    "https://worldwide.espacenet.com"
]

SOURCES_MINING = [
    "MiningGlobal.com",
    "Mining.com",
    "Mining Magazine",
    "Mining Journal",
    "Mining Technology",
    "Mining Weekly",
    "Mining News"
]

SOURCES_FAVOURITE_SHORT = [
    "Mckinsey",
    "Bain",
    "BCG",
    "World Economic Forum",
    "amy webb",
    "peter diamandis",
    "The Wall Street Journal",
    "ian pearson",
    "gerd leonhard"
    "IMF",
    "World Bank",
    "patents.google.com",
    "Financial Times",
    "Reuters Business",
    "CNBC",
    "Business Insider",
    "The Information",
    "The Times – Business Section",
    "The Economist",
    "The Times",
    "Bloomberg",
    "Forbes",
    "Bloomberg Businessweek",
    "Fast Company",
    "Inc.",
]

# Favourite sources
SOURCES_FAVOURITE = [
    "Mckinsey",
    "Bain",
    "BCG",
    "WEF",
    "ycombinator",
    "https://www.statista.com/outlook/fmo/banking/worldwide",
    "Financial Times",
    "CNBC",
    "The Economist",
    "The Wall Street Journal",
    "Research Gate",
    "https://www.ibef.org/industry/banking-india",
    "PWC",
    "Accenture",
    "EY"
    "Deloitte",
    "Reuters",
    "IMF",
    "Business Insider",
    "The Information",
    "The Times",
    "Forbes",
    "Fast Company",
    "Inc.",
    "Andreessen Horowitz",
    "MIT Sloan Management Review",
    "Harvard Business Review",
    "Amy Webb",
    "Peter Diamandis",
    "Gerd Leonhard",
    "Thomas Frey",
]

CUSTOM_SOURCES = [
    "https://futuristspeaker.com/future-of-banking/reinventing-the-banking-industry-how-financial-institutions/",
    "https://www.oliverwyman.com/our-expertise/insights/2024/sep/five-key-trends-shaping-digital-banks-future.html",
    "https://www.synpulse.com/en/insights/the-future-of-banking-technology-trends-and-developments-on-the-path-to-the-next-generation-of-banking",
    "https://www.linkedin.com/pulse/10-most-important-banking-financial-technology-trends-bernard-marr-2bzre/",
    "https://innowise.com/blog/digital-banking-trends/",
    "https://innowise.com/blog/generative-ai-in-banking/",
    "https://www.mckinsey.com/industries/financial-services/our-insights/fintechs-a-new-paradigm-of-growth#/",
    "https://www.researchandmarkets.com/report/online-banking?utm_source=CI&utm_medium=PressRelease&utm_code=wqz9jp&utm_campaign=1600080+-+Global+Digital+Banking+Markets+Report+2021-2026+-+The+Rise+of+the+On-Demand+Economy+%26+Customer+Self-Service+Tilts+Digital+Banking+Technologies+into+the+Mass+Adoption+Stage&utm_exec=chdo54prd",
    "https://theuxda.com/blog/5-ways-future-money-will-disrupt-banking-experience",
    "https://www.ey.com/en_kw/industries/financial-services/unlocking-the-future-of-banking-the-transformative-power-of-generative-ai",
    "https://www.accenture.com/us-en/insights/banking/top-10-trends-banking-2025",
    "https://www.forbes.com/councils/forbesfinancecouncil/2025/02/05/the-future-of-banking-when-data-transforms-into-action/",
    "https://www.weforum.org/stories/2025/05/retail-investment-participation-empowerment/",
    "https://blogs.lse.ac.uk/internationaldevelopment/2025/05/09/the-world-bank-and-the-new-global-economic-disorder/",
    "https://rfi.global/the-future-of-banking-five-strategies-for-banks-and-fintechs/"
]



# Combined dictionary for backward compatibility
SPECIFIED_SOURCES = {
    "consulting_firms": SOURCES_CONSULTING_FIRMS,
    "gov_non_profit": SOURCES_GOV_NON_PROFIT,
    "news_sources": SOURCES_NEWS_SOURCES,
    "futurists": SOURCES_FUTURISTS
}

# Flatten source categories into individual variables for templating
ALL_SOURCES_FLATTENED = {
    f"sources_{key}": value for key, value in {
        "consulting_firms": SOURCES_CONSULTING_FIRMS,
        "gov_non_profit": SOURCES_GOV_NON_PROFIT,
        "news_sources": SOURCES_NEWS_SOURCES,
        "futurists": SOURCES_FUTURISTS,
        "patents": SOURCES_PATENTS,
    }.items()
}

SOURCES_TESTING = [
    "mckinsey"
    "bain"
    "wef"
    "Amy Webb"
    "BCG"
]

# Definitions

# Market Forces and Future Signals - How they are unpacked
MARKET_FORCE_DEFINITIONS = {
    "environment_definition": "Context (the how): The macro environment within which markets and businesses operate. This includes external factors like political and economic conditions, technology developments, social trends, regulatory shifts and ecology that influence businesses.​  Impact (the why): Understanding the environment helps businesses anticipate changes and adapt strategically to remain competitive and compliant.",
    
    "market_definition": "Context (the how): The market refers to the specific industries including competitors, customer demographics and demand trends.​ Impact (the why): Analysing the market helps businesses identify opportunities, understand their competitive position, and tailor strategies to meet market demands.",

    "business_definition": "Context (the hoßw): The business models that will be required to be successful in the market and environment. This encompasses internal operations, resources, and capabilities, such as organisational structure, technology, partnerships and capital.​ Impact (the why): Businesses need to configure their business models to optimise performance, leverage strengths, and align capabilities with external opportunities.",
    
    "market_force_definition": "Global market forces set the stage for business environments by driving shifts in supply, demand, and competition across industries. A market force is a significant external driver that influences how industries, markets, and societies evolve over time. It represents a broad pattern or pressure — legal, economic, technological, regulatory, environmental, or social — that shapes behaviors, decisions, and value creation. Market forces often persist over the medium to long term, exhibit measurable or emerging momentum, and may carry varying levels of impact and uncertainty. Identifying market forces helps organizations anticipate change, uncover opportunities or threats, and inform strategic responses. examples include Russia / Ukraine conflict​, Climate change​, Inflation and rising costs, Energy security Growing middle class, Rapid urbanisation",
    
    "key_finding_definition": "A key finding is a factual observation or data point extracted directly from a source (e.g., 'Market size reached X billion').",
    
    "key_insight_definition": "A key insight is an interpretation of one or more findings, explaining the 'so what?' and its significance or implications (e.g., 'The market size growth indicates rapid adoption driven by Y factors, implying Z for future strategy').",
}


RESEARCH_INPUTS = {
    'specialisation': 'Various',
    'topic': 'Global Market Forces affecting the Mining Industry',
    'topic_short': 'Mining_Forces', # used for file naming
    'market': '',
    'business': 'Exxaro Resources Limited',
    'audience': 'Expert',
    'specific_points_of_interest': [''],
    'research_sources': SOURCES_TESTING,
    'minimum_number_of_sources': 5,
    'maximum_number_of_sources': 5,
    'minimum_number_of_forces': 0,
    'source_score_threshold': 10,
    'date': datetime.now().strftime('%d %B %Y'),
    'market_force_definition': MARKET_FORCE_DEFINITIONS
}
