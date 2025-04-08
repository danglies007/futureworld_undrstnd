#config.py

import os

USER_INPUT_VARIABLES = {
    "work_type": "Tsunamis of Change - Signal Scanner",
    "current_year": "2025",
    "topic": "Market Forces",
    "industry": "Coal Mining",
    "market": "Globally", # define the market for analysis
    "company": "", # add company name
    "company_short": "", # add short company name
    "company_website": "" # add company website
} 

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
    "https://www.economist.com",
    "https://www.wired.com",
    "https://www.technologyreview.com",
    "https://www.forbes.com",
    "https://www.newscientist.com",
    "https://www.bloomberg.com",
    "https://www.cbinsights.com",
]

SOURCES_FUTURISTS = [
    "https://futuristspeaker.com/",
    "https://www.futuristgerd.com/",
    "https://burrus.com/",
    "https://www.diamandis.com/",
    "https://www.pearson.uk.com/",
    "https://www.matthewgriffin.info/",
    "https://www.kurzweilai.net/",
    "https://richardvanhooijdonk.com/en/",
]

SOURCES_PATENTS = [
    "https://patents.google.com",
    "https://www.uspto.gov",
    "https://www.lens.org",
    "https://www.epo.org/en",
    "https://worldwide.espacenet.com"

]
# Combined dictionary for backward compatibility
SPECIFIED_SOURCES = {
    "consulting_firms": SOURCES_CONSULTING_FIRMS,
    "gov_non_profit": SOURCES_GOV_NON_PROFIT,
    "news_sources": SOURCES_NEWS_SOURCES,
    "futurists": SOURCES_FUTURISTS
}
