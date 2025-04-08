from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import date
import ast
import re

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
    patent_sources: List[str] = Field(
        default_factory=lambda: [
            "https://worldwide.espacenet.com/",
            "https://patents.google.com/",
            "https://www.uspto.gov/",
            "https://www.wipo.int/",
        ],
        description="List of URLs for patent databases.",
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

class ResearchItem(BaseModel):
    """Model representing an individual research item to be processed."""
    id: str = Field(..., description="Unique identifier for the research item.")
    topic: str = Field(..., description="Main topic of the research item.")
    keywords: List[str] = Field(..., description="Keywords related to this research item.")
    scope: str = Field(..., description="Scope of the research item (e.g., industry, market).")
    time_horizon: str = Field(..., description="Time horizon for this research item.")

class ResearchPlan(BaseModel):
    """Model representing the structured research plan."""
    target_market: str = Field(description="Target market for the research.")
    target_industry: str = Field(description="Target industry for the research.")
    keywords: List[str] = Field(description="List of keywords for the research.")
    time_horizon: str = Field(description="Time horizon for the research.")
    sources_config: Dict[str, Any] = Field(description="Configuration for data sources.")
    uploaded_files: List[str] = Field(default=[], description="List of paths to uploaded files.")
    research_items: List[ResearchItem] = Field(default_factory=list, description="List of research items to process.")

    @classmethod
    def from_crew_output(cls, crew_output: Any) -> "ResearchPlan":
        """Parse a CrewOutput object into a ResearchPlan."""
        if hasattr(crew_output, "raw_output"):
            raw_output = crew_output.raw_output
        elif isinstance(crew_output, dict) and "raw_output" in crew_output:
            raw_output = crew_output["raw_output"]
        else:
            raw_output = str(crew_output)
        
        print(f"Parsing raw output: {raw_output[:100]}...")
        
        # Extract key components using regex for more reliable parsing
        target_market = cls._extract_value(raw_output, r"target_market=['\"]([^'\"]+)['\"]")
        target_industry = cls._extract_value(raw_output, r"target_industry=['\"]([^'\"]+)['\"]")
        time_horizon = cls._extract_value(raw_output, r"time_horizon=['\"]([^'\"]+)['\"]")
        
        # Extract keywords list
        keywords = []
        if "keywords=" in raw_output:
            keywords_match = re.search(r"keywords=(\[[^\]]+\])", raw_output)
            if keywords_match:
                keywords_str = keywords_match.group(1)
                try:
                    keywords = ast.literal_eval(keywords_str)
                except (SyntaxError, ValueError):
                    # Fallback to simple string parsing
                    keywords = keywords_str.strip("[]").replace("'", "").split(", ")
        
        # Extract sources_config if present
        sources_config = {}
        if "sources_config=" in raw_output:
            sources_config_match = re.search(r"sources_config=({[^}]+})", raw_output)
            if sources_config_match:
                try:
                    sources_config_str = sources_config_match.group(1)
                    sources_config = ast.literal_eval(sources_config_str)
                except (SyntaxError, ValueError):
                    # Default to empty dict if parsing fails
                    sources_config = {}
        
        # Extract uploaded_files if present
        uploaded_files = []
        if "uploaded_files=" in raw_output:
            uploaded_files_match = re.search(r"uploaded_files=(\[[^\]]*\])", raw_output)
            if uploaded_files_match:
                try:
                    uploaded_files_str = uploaded_files_match.group(1)
                    uploaded_files = ast.literal_eval(uploaded_files_str)
                except (SyntaxError, ValueError):
                    # Default to empty list if parsing fails
                    uploaded_files = []
        
        # Create research items from keywords
        research_items = []
        for i, keyword in enumerate(keywords):
            research_items.append(
                ResearchItem(
                    id=f"item_{i+1}",
                    topic=keyword,
                    keywords=[keyword],
                    scope=target_industry or "General",
                    time_horizon=time_horizon or "3-5 years"
                )
            )
        
        # Create and return the ResearchPlan
        return cls(
            target_market=target_market or "Global",
            target_industry=target_industry or "General",
            keywords=keywords,
            time_horizon=time_horizon or "3-5 years",
            sources_config=sources_config,
            uploaded_files=uploaded_files,
            research_items=research_items
        )
    
    @staticmethod
    def _extract_value(text: str, pattern: str) -> Optional[str]:
        """Extract a value using regex pattern."""
        match = re.search(pattern, text)
        return match.group(1) if match else None

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
