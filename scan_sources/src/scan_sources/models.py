from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, field_validator
import uuid
import json
from datetime import datetime

class RawMarketForce(BaseModel):
    title: str = Field(..., description="Brief title of the identified market force")
    raw_description: str = Field(..., description="The original description as found in the source")
    # source_origin: str = Field(..., description="Category of the research source", enum=["Futurist", "Academic Paper", "Patent", "Consultant Report", "Industry Publication", "News Article", "Market Research", "Government Report", "Think Tank", "Social Media", "Other"])
    source_name: str = Field(..., description="Name of the specific source")
    source_url: Optional[str] = Field(None, description="URL or reference to the source")
    source_date: Optional[str] = Field(None, description="Date of publication")
    key_terms: List[str] = Field(default_factory=list, description="List of key terms associated with this market force")
    mentioned_entities: List[str] = Field(default_factory=list, description="Companies, technologies, or other entities mentioned")
    raw_findings: List[str] = Field(default_factory=list, description="List of raw findings associated with this market force")
    raw_examples: List[str] = Field(default_factory=list, description="Examples of the market force in action")
    interesting_facts: List[str] = Field(default_factory=list, description="Interesting facts associated with this market force")
    interesting_statistics: List[str] = Field(default_factory=list, description="Interesting statistics associated with this market force")
    interesting_quotes: List[str] = Field(default_factory=list, description="Interesting quotes associated with this market force")
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

class ResearchOutput(BaseModel):
    source_category: str = Field(..., description="Category of the research source")
    summary: str = Field(..., description="Summary of the research findings")
    raw_market_forces: List[RawMarketForce] = Field(..., description="List of identified market forces")

# class StructuredMarketForce(BaseModel):
#     id: str = Field(..., description="Unique identifier for the market force")
#     source_category: str = Field(..., description="Category of the source")
#     short_description: str = Field(..., description="Brief description of the market force")
#     long_description: str = Field(..., description="Detailed description of the market force")
#     examples: List[str] = Field(default_factory=list, description="Examples of the market force in action")
#     source_name: str = Field(..., description="Name of the source")
#     source_url: Optional[str] = Field(None, description="URL or reference to the source")
#     source_date: Optional[str] = Field(None, description="Date of publication")
#     key_terms: List[str] = Field(default_factory=list, description="Key terms associated with this market force")
#     mentioned_entities: List[str] = Field(default_factory=list, description="Entities mentioned in relation to this market force")
    
#     @field_validator('id', mode='before')
#     @classmethod
#     def set_id_if_none(cls, v):
#         return v or f"MF-{uuid.uuid4().hex[:8]}"

# class ExtractorOutput(BaseModel):
#     market_forces: List[StructuredMarketForce] = Field(..., description="Structured market forces extracted from research")

# class ConsolidatedMarketForce(BaseModel):
#     consolidated_id: str = Field(..., description="Unique identifier for the consolidated market force")
#     constituent_forces: List[str] = Field(..., description="IDs of the constituent market forces")
#     source_categories: List[str] = Field(..., description="Categories of sources that identified this force")
#     canonical_description: str = Field(..., description="Standardised short description")
#     consolidated_description: str = Field(..., description="Comprehensive description combining insights from all sources")
#     all_examples: List[str] = Field(default_factory=list, description="Combined examples from all sources")
#     all_sources: List[Dict[str, str]] = Field(default_factory=list, description="All source references")
#     first_identified: Optional[str] = Field(None, description="Earliest date this market force was identified")
    
#     @field_validator('consolidated_id', mode='before')
#     @classmethod
#     def set_consolidated_id_if_none(cls, v):
#         return v or f"CMF-{uuid.uuid4().hex[:8]}"

# class ConsolidatorOutput(BaseModel):
#     consolidated_forces: List[ConsolidatedMarketForce] = Field(..., description="Consolidated market forces")
    
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