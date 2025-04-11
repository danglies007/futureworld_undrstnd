from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import uuid
import json
from datetime import datetime

class AttributedItem(BaseModel):
    """Base model for any item that needs attribution."""
    content: str = Field(..., description="The actual content (fact, statistic, quote, etc.)")
    source_url: str = Field(..., description="URL where this information was found")
    source_paragraph: Optional[str] = Field(None, description="Original paragraph or context from the source")
    source_name: Optional[str] = Field(None, description="Name of the source")

class SearchMetadata(BaseModel):
    """Metadata about the search that produced this market force."""
    search_query: str = Field(..., description="The exact search query used to find this information")
    search_timestamp: str = Field(..., description="When the search was conducted")
    search_engine: str = Field(default="Default Search Tool", description="The search engine or tool used")
    search_results_count: Optional[int] = Field(None, description="Number of total results found")
    search_position: Optional[int] = Field(None, description="Position in search results where this was found")

class RawMarketForce(BaseModel):
    title: str = Field(..., description="Brief title of the identified market force")
    raw_description: str = Field(..., description="The original description as found in the source")
    # source_origin: str = Field(..., description="Category of the research source", enum=["Futurist", "Academic Paper", "Patent", "Consultant Report", "Industry Publication", "News Article", "Market Research", "Government Report", "Think Tank", "Social Media", "Other"])
    source_name: str = Field(..., description="Name of the specific source")
    source_url: Optional[str] = Field(None, description="URL or reference to the source")
    source_date: Optional[str] = Field(None, description="Date of publication")
    key_terms: List[str] = Field(default_factory=list, description="List of key terms associated with this market force")
    mentioned_entities: List[str] = Field(default_factory=list, description="Companies, technologies, or other entities mentioned")
    raw_findings: List[AttributedItem] = Field(default_factory=list, description="List of raw findings with sources")
    raw_examples: List[AttributedItem] = Field(default_factory=list, description="Examples of the market force in action with sources")
    relevant_facts: List[AttributedItem] = Field(default_factory=list, description="Relevant facts with sources")
    relevant_statistics: List[AttributedItem] = Field(default_factory=list, description="Relevant statistics with sources")
    relevant_data: List[AttributedItem] = Field(default_factory=list, description="Relevant data with sources")
    relevant_quotes: List[AttributedItem] = Field(default_factory=list, description="Relevant quotes with sources")    
    relevance: str = Field(..., description="Relevance of the market force to the research topic")
    related_trends: List[str] = Field(default_factory=list, description="List of related trends associated with this market force")
    related_mega_trends: List[str] = Field(default_factory=list, description="List of related mega trends associated with this market force")
    # possible_signals: List[str] = Field(default_factory=list, description="List of possible signals associated with this market force")
    # possible_structural_shifts: List[str] = Field(default_factory=list, description="List of possible structural shifts associated with this market force")
    # implications_on_future_of_sector: List[str] = Field(default_factory=list, description="List of implications on future of sector associated with this market force")
    sources: List[Dict[str, str]] = Field(
        description="Sources with title and URL for each key term",
        default_factory=list
    )
    search_metadata: Optional[SearchMetadata] = Field(
        None, 
        description="Metadata about the search that found this market force"
    )
    agent_notes: Optional[str] = Field(
        None, 
        description="Agent's notes about finding or processing this market force"
    )

    @field_validator('source_date')
    def validate_date(cls, v, info):
        """Validate that the source_date is not today's date unless confirmed."""
        today = datetime.now().strftime("%Y-%m-%d")
        
        # If source_date is missing, set it to "Unknown" rather than today's date
        if not v:
            return "Unknown"
            
        # If source_date is the same as today, check if it's legitimate
        if v == today:
            # Get the source URL from the data that's being validated
            # In Pydantic v2, we need to use info.data instead of values
            source_url = info.data.get('source_url', '') if hasattr(info, 'data') else ''
            
            # Look for indicators that this is actually published today
            indicators_of_today = [
                'news.', 'daily.', 'today.', '/blog/', '/latest/',
                '/news/', '/daily/', '/today/', '/current/'
            ]
            
            # If none of the indicators are present, mark as unknown
            if not any(indicator in source_url.lower() for indicator in indicators_of_today):
                return "Unknown"  # Suspicious date, mark as unknown
                
        return v

    class Config:
        """Configuration for the model."""
        schema_extra = {
            "example": {
                "title": "Rise of Edge Computing",
                "raw_description": "Edge computing is growing rapidly as IoT devices proliferate",
                "source_name": "Gartner",
                "source_url": "https://www.gartner.com/smarterwithgartner/what-edge-computing-means-for-infrastructure-and-operations-leaders",
                "source_date": "2018-10-03",
                "key_terms": ["edge computing", "IoT", "decentralized computing"],
                "mentioned_entities": ["Gartner", "AWS", "Microsoft"],
                "raw_findings": [
                    {
                        "content": "40% of organizations will have edge computing initiatives by 2023",
                        "source_url": "https://www.gartner.com/smarterwithgartner/what-edge-computing-means-for-infrastructure-and-operations-leaders",
                        "source_paragraph": "Gartner predicts that by 2023, more than 50% of enterprise-generated data will be created and processed outside the data center or cloud, up from less than 10% in 2019. And by 2023, 40% of organizations will have edge computing initiatives, up from about 1% in 2019.",
                        "source_name": "Gartner"
                    }
                ],
                "interesting_facts": [
                    {
                        "content": "Edge computing can reduce latency to under 5ms in many cases",
                        "source_url": "https://www.example.com/edge-computing-whitepaper",
                        "source_paragraph": "Our tests showed that implementing edge computing reduced latency from 100ms to under 5ms for most IoT applications, representing a 95% improvement in response time.",
                        "source_name": "Example Research"
                    }
                ]
            }
        }

class ResearchOutput(BaseModel):
    source_category: str = Field(..., description="Category of the research source")
    summary: str = Field(..., description="Summary of the research findings")
    raw_market_forces: List[RawMarketForce] = Field(..., description="List of identified market forces")

class StructuredMarketForce(BaseModel):
    id: str = Field(..., description="Unique identifier for the market force")
    source_category: str = Field(..., description="Category of the source")
    short_description: str = Field(..., description="Brief description of the market force")
    long_description: str = Field(..., description="Detailed description of the market force")
    examples: List[str] = Field(default_factory=list, description="Examples of the market force in action")
    source_name: str = Field(..., description="Name of the source")
    source_url: Optional[str] = Field(None, description="URL or reference to the source")
    source_date: Optional[str] = Field(None, description="Date of publication")
    key_terms: List[str] = Field(default_factory=list, description="Key terms associated with this market force")
    mentioned_entities: List[str] = Field(default_factory=list, description="Entities mentioned in relation to this market force")
    
    @field_validator('id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"MF-{uuid.uuid4().hex[:8]}"

class ListStructuredMarketForce(BaseModel):
    """Container for a list of structured market forces."""
    market_forces: List[StructuredMarketForce] = Field(default_factory=list, description="List of structured market forces")
    
    # Helper method to add market forces
    def add_market_force(self, market_force: StructuredMarketForce):
        self.market_forces.append(market_force)
    
    # Helper method to get all market forces
    def get_all_market_forces(self) -> List[StructuredMarketForce]:
        return self.market_forces

class ExtractorOutput(BaseModel):
    market_forces: List[StructuredMarketForce] = Field(..., description="Structured market forces extracted from research")

class ConsolidatedMarketForce(BaseModel):
    consolidated_id: str = Field(..., description="Unique identifier for the consolidated market force")
    constituent_forces: List[str] = Field(..., description="IDs of the constituent market forces")
    source_categories: List[str] = Field(..., description="Categories of sources that identified this force")
    canonical_description: str = Field(..., description="Standardised short description")
    consolidated_description: str = Field(..., description="Comprehensive description combining insights from all sources")
    all_examples: List[str] = Field(default_factory=list, description="Combined examples from all sources")
    all_sources: List[Dict[str, str]] = Field(default_factory=list, description="All source references")
    first_identified: Optional[str] = Field(None, description="Earliest date this market force was identified")
    
    @field_validator('consolidated_id', mode='before')
    @classmethod
    def set_consolidated_id_if_none(cls, v):
        return v or f"CMF-{uuid.uuid4().hex[:8]}"

class ConsolidatorOutput(BaseModel):
    consolidated_forces: List[ConsolidatedMarketForce] = Field(..., description="Consolidated market forces")
    
# # Helper function for parsing agent output to Pydantic models
# def parse_agent_output(output: str, expected_model: Any) -> Any:
#     """Parse agent output and convert to a Pydantic model instance"""
#     try:
#         # Try to parse as JSON
#         data = json.loads(output)
#         # Convert to Pydantic model
#         return expected_model.model_validate(data)
#     except (json.JSONDecodeError, ValueError) as e:
#         print(f"Error parsing output: {e}")
#         # Return a basic model instance as fallback
#         if expected_model == ResearchOutput:
#             return ResearchOutput(source_category="Unknown", raw_market_forces=[])
#         elif expected_model == ExtractorOutput:
#             return ExtractorOutput(market_forces=[])
#         elif expected_model == ConsolidatorOutput:
#             return ConsolidatorOutput(consolidated_forces=[])
#         return None

class MarketForceReportSection(BaseModel):
    section_title: str = Field(description="Section title")
    section_content: str = Field(description="Main content of the section")
    key_insights: List[str] = Field(description="Key insights from this section")
    possible_signals: List[str] = Field(
        default_factory=list,
        description="Optional recommendations indicating any changes of this market force, based on findings"
    )
    possible_structural_shifts: List[str] = Field(
        default_factory=list,
        description="Optional recommendations indicating any structural shifts of this market force, based on findings"
    )
    implications_on_future_of_sector: List[str] = Field(
        default_factory=list,
        description="Optional recommendations indicating any implications on future of sector of this market force, based on findings"
    )
    sources: List[Dict[str, str]] = Field(
        description="Sources with title and URL for this section",
        default_factory=list
    )

class MarketForceReport(BaseModel):
    report_title: str = Field(description="Title of the report")
    generation_date: str = Field(description="Report generation date")
    executive_summary: str = Field(description="A concise executive summary")
    key_findings: List[Dict[str, str]] = Field(
        description="List of key findings with their sources",
        default_factory=list
    )
    report_sections: List[MarketForceReportSection] = Field(
        description="Detailed report sections"
    )
    sources: List[Dict[str, str]] = Field(
        description="All sources used in the report",
        default_factory=list
    )


class Source(BaseModel):
    source_id: str
    title: str
    url: str
    publisher: str
    publication_date: str
    author: str
    relevance_score: float
    domain_category: str
    description: str

class SourceIdentificationResults(BaseModel):
    topic: str
    specialisation: str
    date_of_research: str
    total_sources_found: int
    sources: List[Source]

class SourceIdentificationOutput(BaseModel):
    source_identification_results: SourceIdentificationResults