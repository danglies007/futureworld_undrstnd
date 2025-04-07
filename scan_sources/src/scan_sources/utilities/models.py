from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date

# --------------- Input Models ---------------#

class SourceConfig(BaseModel):
    """Configuration for different types of sources to scan."""
    consulting_firms: List[str] = Field(
        default_factory=lambda: [
            "https://www.mckinsey.com",
            "https://www.bain.com",
            "https://www.bcg.com",
        ],
        description="List of URLs for consulting firm websites.",
    )
    gov_non_profit: List[str] = Field(
        default_factory=lambda: [
            "https://www.weforum.org",
            "https://intelligence.weforum.org/",
            "https://www.imf.org",
            "https://www.consilium.europa.eu/en/",
        ],
        description="List of URLs for government and non-profit organization websites.",
    )
    news_sources: List[str] = Field(
        default_factory=lambda: [
            "https://www.economist.com",
            "https://www.wired.com",
            "https://www.technologyreview.com",
            "https://www.forbes.com",
            "https://www.newscientist.com",
            "https://www.bloomberg.com",
            "https://www.cbinsights.com",
        ],
        description="List of URLs for news and tech publication websites.",
    )
    futurists: List[str] = Field(
        default_factory=lambda: [
            "https://futuristspeaker.com/",
            "https://www.futuristgerd.com/",
            "https://burrus.com/",
            "https://www.diamandis.com/",
            "https://www.pearson.uk.com/",
            "https://www.matthewgriffin.info/",
            "https://www.kurzweilai.net/",
            "https://richardvanhooijdonk.com/en/",
        ],
        description="List of URLs for futurist websites/blogs.",
    )
    custom: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Dictionary for custom source types and their URLs.",
    )


class MarketForceInput(BaseModel):
    """Input parameters for the market force scanning crew."""
    target_market: str = Field("Global", description="Geographic or market scope.")
    target_industry: str = Field(..., description="Specific industry to focus on.")
    keywords: List[str] = Field(
        default_factory=lambda: [
            "Forces",
            "Trends",
            "Mega trends",
            "Future of",
            "Signals",
            "Structural shifts",
        ],
        description="Keywords to search for.",
    )
    time_horizon: str = Field("5+ years", description="Time horizon for the analysis.")
    sources_config: SourceConfig = Field(
        default_factory=SourceConfig,
        description="Configuration of sources to scan."
    )
    uploaded_files: List[str] = Field(
        default_factory=list, description="List of paths to user-uploaded files."
    )

# --------------- Intermediate & Output Models ---------------#

class ResearchPlan(BaseModel):
    """Model representing the structured research plan."""
    target_market: str = Field(description="Target market for the research.")
    target_industry: str = Field(description="Target industry for the research.")
    keywords: list[str] = Field(description="List of keywords for the research.")
    time_horizon: str = Field(description="Time horizon for the research.")
    sources_config: dict = Field(description="Configuration for data sources.") # Can be more specific if needed
    uploaded_files: list[str] = Field(default=[], description="List of paths to uploaded files.")

class SourceFinding(BaseModel):
    """Represents a piece of relevant information found in a source."""
    source_name: str = Field(..., description="Name of the source (e.g., website domain, filename).")
    url: Optional[str] = Field(None, description="URL of the source, if applicable.")
    source_type: str = Field(..., description="Type of the source (e.g., 'Web', 'PDF', 'Uploaded').")
    publication_date: Optional[date] = Field(None, description="Publication date, if available.")
    matched_keywords: List[str] = Field(..., description="Keywords that led to this finding.")
    scope_context: str = Field(..., description="Target market and industry context.")
    extracted_text: str = Field(..., description="The relevant text snippet extracted.")

class IdentifiedForce(BaseModel):
    """Represents a distinct market force, trend, or signal identified."""
    name: str = Field(..., description="Concise name for the identified force/trend.")
    description: str = Field(..., description="Detailed description of the force/trend.")
    keywords: List[str] = Field(..., description="Keywords associated with this force/trend.")
    scope: str = Field(..., description="Geographic/market scope relevance.")
    time_horizon: str = Field(..., description="Time horizon relevance.")
    supporting_evidence: List[SourceFinding] = Field(
        ..., description="List of source findings supporting this force/trend."
    )

class MarketForceOutput(BaseModel):
    """Final output containing the list of identified forces and report formats."""
    identified_forces: List[IdentifiedForce] = Field(
        ..., description="List of all identified and validated market forces/trends."
    )
    markdown_table: str = Field(
        ..., description="Detailed summary table in Markdown format."
    )
    markdown_report: str = Field(
        ..., description="Structured narrative report in Markdown format."
    )
