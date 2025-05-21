from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
import uuid
import json
from datetime import date, datetime, time, timedelta


from config import RESEARCH_INPUTS


specialisation = RESEARCH_INPUTS['specialisation']

class AttributedItem(BaseModel):
    """Base model for any item that needs attribution."""
    content: str = Field(..., description="The actual content (fact, statistic, quote, etc.)")
    source_url: str = Field(..., description="URL where this information was found")
    source_text: List[str] = Field(default_factory=list, description="Exact actual word for word extract of the Original paragraph or sentence extracted directly from the source")
    source_name: List[str] = Field(default_factory=list, description="Name of the source")

class SearchMetadata(BaseModel):
    """Metadata about the search that produced this market force."""
    search_query: str = Field(..., description="The exact search query used to find this information")
    search_timestamp: str = Field(..., description="When the search was conducted")
    search_engine: str = Field(default="Default Search Tool", description="The search engine or tool used")
    search_results_count: int = Field(default=0, description="Number of total results found")
    search_position: int = Field(default=0, description="Position in search results where this was found")

# Not using this yet, want to use this to capture the details of the crew used to generate this market report
class Crewdetails(BaseModel):
    """Details about the CrewAI flow and crew used to generate this market report."""
    topic: str = Field(..., description="The topic of the overall output")
    crew_name: str = Field(..., description="The crew used to generate this output")
    start_time: str = Field(..., description="When this crew started")
    end_time: str = Field(..., description="When this crew ended")
    llm_used: str = Field(..., description="The LLM used to generate this output")

class SourceLink(BaseModel):
    """Represents a link to a source with its title."""
    title: str = Field(..., description="Title of the source or key term link")
    url: str = Field(..., description="URL of the source link")
    date: List[str] = Field(default_factory=list, description="Optional publication date for the source")

class RawMarketForce(BaseModel):
    raw_market_force_id: str = Field(..., description="Unique identifier for this market force")
    raw_market_force_name: str = Field(..., description="Brief name of the identified market force")
    raw_description: str = Field(..., description="The original description as found in the source")
    key_terms: List[str] = Field(default_factory=list, description="List of key terms associated with this market force")
    mentioned_entities: List[str] = Field(default_factory=list, description="Companies, technologies, or other entities mentioned")
    raw_findings: List[AttributedItem] = Field(default_factory=list, description="List of raw findings with sources")
    raw_examples: List[AttributedItem] = Field(default_factory=list, description="Examples of the market force in action with sources")
    relevant_facts: List[AttributedItem] = Field(default_factory=list, description="Relevant facts with sources")
    relevant_statistics: List[AttributedItem] = Field(default_factory=list, description="Relevant statistics with sources")
    relevant_data: List[AttributedItem] = Field(default_factory=list, description="Relevant data with sources")
    relevant_quotes: List[AttributedItem] = Field(default_factory=list, description="Relevant quotes with sources")    
    # relevance: str = Field(..., description="Relevance of the market force to the research topic")
    related_trends: List[str] = Field(default_factory=list, description="List of related trends associated with this market force")
    related_mega_trends: List[str] = Field(default_factory=list, description="List of related mega trends associated with this market force")
    possible_signals: List[str] = Field(default_factory=list, description="List of possible signals associated with this market force")
    possible_structural_shifts: List[str] = Field(default_factory=list, description="List of possible structural shifts associated with this market force")
    implications_on_future_of_sector: List[str] = Field(default_factory=list, description="List of implications on future of sector associated with this market force")
    sources: List[SourceLink] = Field(
        description="List of unique source documents (title, URL, date) relevant to this market force finding.",
        default_factory=list
    )

    @field_validator('raw_market_force_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"MF-{uuid.uuid4().hex[:8]}"
    # search_metadata: Optional[SearchMetadata] = Field(
    #     None,
    #     description="Metadata about the search that found this market force"
    # )
    # agent_notes: Optional[str] = Field(
    #     None,
    #     description="Agent's notes about finding or processing this market force"
    # )

    # @field_validator('source_date')
    # def validate_date(cls, v, info):
    #     """Validate that the source_date is not today's date unless confirmed."""
    #     today = datetime.now().strftime("%Y-%m-%d")
        
    #     # If source_date is missing, set it to "Unknown" rather than today's date
    #     if not v:
    #         return "Unknown"
            
    #     # If source_date is the same as today, check if it's legitimate
    #     if v == today:
    #         # Get the source URL from the data that's being validated
    #         # In Pydantic v2, we need to use info.data instead of values
    #         source_url = info.data.get('source_url', '') if hasattr(info, 'data') else ''
            
    #         # Look for indicators that this is actually published today
    #         indicators_of_today = [
    #             'news.', 'daily.', 'today.', '/blog/', '/latest/',
    #             '/news/', '/daily/', '/today/', '/current/'
    #         ]
            
    #         # If none of the indicators are present, mark as unknown
    #         if not any(indicator in source_url.lower() for indicator in indicators_of_today):
    #             return "Unknown"  # Suspicious date, mark as unknown
                
    #     return v

    # class Config:
    #     """Configuration for the model."""
    #     schema_extra = {
    #         "example": {
    #             "title": "Rise of Edge Computing",
    #             "raw_description": "Edge computing is growing rapidly as IoT devices proliferate",
    #             "key_terms": ["edge computing", "IoT", "decentralized computing"],
    #             "mentioned_entities": ["Gartner", "AWS", "Microsoft"],
    #             "raw_findings": [
    #                 {
    #                     "content": "40% of organizations will have edge computing initiatives by 2023",
    #                     "source_paragraph": "Gartner predicts that by 2023, more than 50% of enterprise-generated data will be created and processed outside the data center or cloud, up from less than 10% in 2019. And by 2023, 40% of organizations will have edge computing initiatives, up from about 1% in 2019.",
    #                 }
    #             ],
    #             "interesting_facts": [
    #                 {
    #                     "content": "Edge computing can reduce latency to under 5ms in many cases",
    #                     "source_paragraph": "Our tests showed that implementing edge computing reduced latency from 100ms to under 5ms for most IoT applications, representing a 95% improvement in response time.",
    #                 }
    #             ]
    #         }
    #     }

class ResearchOutput(BaseModel):
    source_category: str = Field(..., description="Category of the research source")
    source_title: str = Field(..., description="Title of the research source")
    url: str = Field(..., description="URL of the research source")
    summary: str = Field(..., description="Summary of the research findings")
    raw_market_forces: List[RawMarketForce] = Field(..., description="List of identified market forces")

class StructuredMarketForce(BaseModel):
    id: str = Field(..., description="Unique identifier for the market force")
    source_category: str = Field(..., description="Category of the source")
    short_description: str = Field(..., description="Brief description of the market force")
    long_description: str = Field(..., description="Detailed description of the market force")
    examples: List[str] = Field(default_factory=list, description="Examples of the market force in action")
    source_name: str = Field(..., description="Name of the source")
    source_url: List[str] = Field(default_factory=list, description="URL or reference to the source")
    source_date: List[str] = Field(default_factory=list, description="Date of publication")
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
    all_sources: List[SourceLink] = Field(default_factory=list, description="All source references")
    first_identified: List[str] = Field(default_factory=list, description="Earliest date this market force was identified")
    
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

class KeyFinding(BaseModel):
    """Represents a key finding with its source attribution."""
    finding: str = Field(..., description="The key finding stated concisely")
    source_author: str = Field(..., description="The author of the source")
    source_name: str = Field(..., description="The name of the source")
    source_url: str = Field(..., description="The URL of the source - make sure these are clickable")

class KeyInsight(BaseModel):
    """Represents a key insight, interpreting findings with implications."""
    insight: str = Field(..., description="The key interpretive insight derived from findings (the 'so what?').")
    sources: List[SourceLink] = Field(description="List of SourceLinks that contributed to this insight.",default_factory=list)
    explanation: List[str] = Field(default_factory=list, description="Brief explanation of why this insight matters or the underlying drivers.")
    implications: List[str] = Field(default_factory=list, description="Key implications of this insight for the topic/sector.")

class MarketForceReportSection(BaseModel):
    section_title: str = Field(description="Section title")
    section_content: str = Field(description="Main content of the section")
    key_insights: List[KeyInsight] = Field(description="Key insights from this section")
    possible_signals: List[str] = Field(default_factory=list,description="Optional recommendations indicating any changes of this market force, based on findings")
    possible_structural_shifts: List[str] = Field(default_factory=list,description="Optional recommendations indicating any structural shifts of this market force, based on findings")
    implications_on_future_of_sector: List[str] = Field(default_factory=list,description="Optional recommendations indicating any implications on future of sector of this market force, based on findings")
    sources: List[SourceLink] = Field(description="Sources with title and URL for this section",default_factory=list)

class MarketForceReport(BaseModel):
    report_title: str = Field(description="Title of the report")
    generation_date: str = Field(description="Report generation date")
    executive_summary: str = Field(description="A concise executive summary")
    key_findings: List[KeyFinding] = Field(description="List of key findings with their sources",default_factory=list)
    report_sections: List[MarketForceReportSection] = Field(description="Detailed report sections")
    sources: List[SourceLink] = Field(description="All sources used in the report",default_factory=list)

class MarketForceImpact(BaseModel):
    """Assessment of a market force's impact."""
    impact_level: str = Field(..., description="Level of potential impact (High, Medium, Low)")
    uncertainty_level: str = Field(..., description="Level of uncertainty about relating to how the market force will evolve (High, Medium, Low)")
    time_horizon: str = Field(..., description="Expected time frame for impact (e.g., '1-3 years', '3-5 years')")
    impact_rationale: List[str] = Field(default_factory=list, description="Brief explanation of why this impact assessment was given")

class MarketForce(BaseModel):
    """Information about a specific market force."""
    force_name: str = Field(..., description="Name of the market force")
    force_category_name: str = Field(..., description="Name of the category within which the market force is grouped (e.g., 'Technological', 'Economic', 'Political', 'Environmental', 'Social', 'Regulatory')")
    description: str = Field(..., description="Detailed description of the market force")
    strap_line: str = Field(..., description="Brief summary of the market force, captured in 2 sentences")
    sectors_affected: List[str] = Field(default_factory=list, description="Economic or business sectors most likely to be affected")
    impact_assessment: MarketForceImpact = Field(..., description="Assessment of the potential impact")
    key_findings: List[KeyFinding] = Field(default_factory=list, description="Key factual findings related to this force")
    key_insights: List[KeyInsight] = Field(default_factory=list, description="Key insights derived from this force or related to this force")
    business_implications: List[str] = Field(default_factory=list, description="Business implications of this force")
    related_forces: List[str] = Field(default_factory=list, description="Names of related market forces")
    early_signals: List[str] = Field(default_factory=list, description="Early signals of this market force")
    takeout: str = Field(..., description="Key takeout of the market force, what is the 'so what?' of this market force?")
    sources: List[str] = Field(default_factory=list, description="Source references for this force")

class MarketForceCategory(BaseModel):
    """A category of market forces."""
    force_category_name: str = Field(..., description="Name of the category within which the market force is grouped (e.g., 'Technological', 'Economic', 'Political', 'Environmental', 'Social', 'Regulatory')")
    force_category_description: str = Field(..., description="Description of this category of market forces")
    market_forces: List[MarketForce] = Field(default_factory=list, description="Market forces in this category")
    force_category_key_insights: List[str] = Field(default_factory=list, description="Key insights for this category")

class MarketForceInteraction(BaseModel):
    """Description of interaction between market forces."""
    forces_involved: List[str] = Field(..., description="Names of the market forces that interact")
    interaction_type: str = Field(..., description="Type of interaction (e.g., 'Reinforcing', 'Counteracting')")
    description: str = Field(..., description="Description of how these forces interact")
    potential_outcomes: List[str] = Field(default_factory=list, description="Potential outcomes from this interaction")

class UncertaintyImpactCategory(BaseModel):
    """Category in the uncertainty-impact matrix."""
    category_name: str = Field(..., description="Name of the uncertainty-impact category")
    market_forces: List[str] = Field(default_factory=list, description="Market forces in this category")

class MarketForceAnalysisReport(BaseModel):
    """Comprehensive report on market forces."""
    report_title: str = Field(..., description="Title of the report")
    generation_date: str = Field(..., description="Report generation date")
    executive_summary: str = Field(..., description="A concise executive summary")
    overall_key_findings: List[str] = Field(default_factory=list, description="Overall key factual findings across all market forces")
    overall_key_insights: List[str] = Field(default_factory=list, description="Overall key insights across all market forces based on the overall key findings")
    force_categories: List[MarketForceCategory] = Field(..., description="Categories of market forces with analysis")
    force_interactions: List[MarketForceInteraction] = Field(default_factory=list, description="Analysis of how different market forces interact")
    uncertainty_impact_matrix: List[UncertaintyImpactCategory] = Field(default_factory=list, description="Matrix categorising forces by uncertainty and impact levels")
    strategic_implications: List[str] = Field(default_factory=list, description="Strategic implications derived from market force analysis")
    glossary: List[str] = Field(default_factory=list, description="Glossary of terms used in the report")
    sources: List[str] = Field(default_factory=list, description="All sources used in the report")

# Source Identification

# Simple source for source identification

# class SourceURL(BaseModel):
#     url: str = Field(..., description="URL of the source")

# class SourceIdentificationResultsURLonly(BaseModel):
#     urls: List[SourceURL] = Field(..., description="List of source URLs")

# This is replaced by the Evaluated source model    
# class Source(BaseModel):
#     source_no: int = Field(..., description="Number of the source")
#     source_id: str = Field(..., description="Unique identifier for the source")
#     title: str = Field(..., description="Title of the source")
#     url: str = Field(..., description="URL of the source")
#     source_type: str = Field(..., description="is it a PDF, website, youtube or other")
#     publisher: str = Field(..., description="Publisher of the source")
#     source_date: str = Field(..., description="Date of publication")
#     author: str = Field(..., description="Author of the source")
#     relevance_score: float = Field(..., description="Relevance score of the source")
#     description: str = Field(..., description="Description of the source")

# # This is the old source identification results - now replaced by the new source identification results below
# class SourceIdentificationResults(BaseModel):
#     topic: str = Field(..., description="Topic of the research")
#     specialisation: str = Field(default=specialisation, description="Specialisation of the research")
#     date_of_research: str = Field(..., description="Date when the research was conducted")
#     # total_sources_found: int = Field(..., description="Total number of sources found")
#     urls: List[SourceURL] = Field(..., description="List of sources found")

# class SourceIdentificationOutput(BaseModel):
#     source_identification_results: SourceIdentificationResults = Field(..., description="Results of source identification")


# New models created for the better source identification process, where we have split into multiple agents
# class PotentialSourceURLs(BaseModel):
#     urls: List[str] = Field(..., description="List of potential source URLs")

# class NotApprovedSourceURLs(BaseModel):
#     urls: List[str] = Field(..., description="List of not approved source URLs")

# class ApprovedSourceURLs(BaseModel):
#     urls: List[str] = Field(..., description="List of approved source URLs")

# Models associated with source discovery
class PotentialSource(BaseModel):
    """Represents a potential source discovered in the initial discovery phase."""
    no: int = Field(..., description="Number of the source")
    # id: str = Field(..., description="Unique identifier for the source")
    url: str = Field(..., description="URL of the source")
    title: str = Field(..., description="Title based on search snippet")
    source_type: str = Field(..., description="Source type (PDF, Website, Other)")
    publication_date: List[str] = Field(default_factory=list, description="Apparent publication date if visible")
    initial_relevance: str = Field(..., description="Brief reason why this source appears promising")

    # @field_validator('id', mode='before')
    # @classmethod
    # def set_id_if_none(cls, v):
    #     return v or f"PSRC-{uuid.uuid4().hex[:8]}"

class PotentialSources(BaseModel):
    potential_sources: List[PotentialSource] = Field(..., description="List of potential sources")

class PotentialSourceURL(BaseModel):
    url: str = Field(..., description="URL of the source")

class PotentialSourcesURLOnly(BaseModel):
    urls: List[PotentialSourceURL] = Field(..., description="List of potential source URLs")

class SourceDiscoveryResults(BaseModel):
    """Results from the source discovery phase."""
    topic: str = Field(..., description="Topic of the research")
    specialisation: str = Field(..., description="Specialisation of the research")
    date_of_discovery: str = Field(..., description="Date when the sources were discovered")
    total_pot_sources_found: int = Field(..., description="Total number of sources found based on the list of potential sources")
    potential_sources: List[PotentialSource] = Field(..., description="List of potential sources for evaluation")

class EvaluatedSource(BaseModel):
    """Represents a source that has been evaluated for quality."""
    no: int = Field(..., description="Number of the source")
    # id: str = Field(..., description="Source ID")
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Source Title")
    source_type: str = Field(..., description="Source type (PDF, Website, Other)")
    publisher: List[str] = Field(default_factory=list, description="Publisher if known")
    source_date: List[str] = Field(default_factory=list, description="Apparent publication date if visible")
    author: List[str] = Field(default_factory=list, description="Author if known")
    relevance_score: float = Field(..., description="Relevance score of the source")
    credibility_score: float = Field(..., description="Credibility score of the source")
    recency_score: float = Field(..., description="Recency score of the source")
    total_score: float = Field(..., description="Sum of relevance, credibility and recency scores of the source")
    accessible: bool = Field(..., description="Whether the source is accessible (not paywalled)")

class EvaluatedSources(BaseModel):
    evaluated_sources: List[EvaluatedSource] = Field(..., description="List of evaluated sources")

# Models associated with source evaluation
class NotApprovedSource(BaseModel):
    """Represents a source that has been evaluated for quality."""
    no: int = Field(..., description="Number of the source")
    id: str = Field(..., description="Source ID")
    url: str = Field(..., description="Source URL")
    title: str = Field(..., description="Source Title")
    relevance_score: float = Field(..., description="Relevance score (1-10)")
    credibility_score: float = Field(..., description="Credibility score (1-10)")
    recency_score: float = Field(..., description="Recency score (1-10)")
    total_score: float = Field(..., description="Combined quality score (sum of relevance, credibility and recency scores)")
    accessible: bool = Field(..., description="Whether the source is accessible (not paywalled)")

    @field_validator('id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return f"NASC-{uuid.uuid4().hex[:8]}"


class NotApprovedSources(BaseModel):
    not_approved_sources: List[NotApprovedSource] = Field(..., description="List of not approved sources")    

class ApprovedSource(BaseModel):
    """Represents a source that has been evaluated for quality."""
    no: int = Field(..., description="Number of the approved source")
    # id: str = Field(..., description="Unique identifier for the approved source")
    url: str = Field(..., description="URL of the approved source")
    title: str = Field(..., description="Title of the approved source")
    source_type: str = Field(..., description="Source type (PDF, Website, Other)")
    publisher: List[str] = Field(default_factory=list, description="Publisher if known")
    source_date: List[str] = Field(default_factory=list, description="Publication date if known")
    author: List[str] = Field(default_factory=list, description="Author if known")
    description: List[str] = Field(default_factory=list, description="Brief description of the source content")
    relevance_score: float = Field(..., description="Relevance score for the approved source")
    credibility_score: float = Field(..., description="Credibility score for the approved source")
    recency_score: float = Field(..., description="Recency score for the approved source")
    total_score: float = Field(..., description="Combined quality score for the approved source (sum of relevance, credibility and recency scores)")
    accessible: bool = Field(..., description="Whether the source is accessible (not paywalled)")

    # @field_validator('id', mode='before')
    # @classmethod
    # def set_id_if_none(cls, v):
    #     return v or f"ASRC-{uuid.uuid4().hex[:8]}"

class ApprovedSources(BaseModel):
    approved_sources: List[ApprovedSource] = Field(..., description="List of approved sources")



class SourceEvaluationResults(BaseModel):
    """Results from the source evaluation phase."""
    topic: str = Field(..., description="Topic of the research")
    specialisation: str = Field(..., description="Specialisation of the research")
    date_of_evaluation: str = Field(..., description="Date when the evaluation was conducted")
    total_sources_not_approved: int = Field(..., description="Total number of sources that did not pass quality criteria and were not approved")
    total_sources_approved: int = Field(..., description="Number of sources that passed quality criteria - total score above the threshold and were approved")
    quality_threshold: float = Field(..., description="Minimum quality score required for approval - minimum total score")
    not_approved_sources: List[NotApprovedSource] = Field(..., description="List of sources that did not pass quality criteria and were not approved")
    approved_sources: List[ApprovedSource] = Field(..., description="List of evaluated high quality sources with quality scores above the threshold")

class SourceApprovedResults(BaseModel):
    """Results approved in the source evaluation process"""
    topic: str = Field(..., description="Topic of the research")
    specialisation: str = Field(..., description="Specialisation of the research")
    date_of_approval: str = Field(..., description="Date when the approval was conducted")
    total_sources_approved: int = Field(..., description="Number of sources that passed quality criteria")
    quality_threshold: float = Field(..., description="Minimum quality score required for approval")
    approved_sources: List[ApprovedSource] = Field(..., description="List of evaluated sources of a high quality with quality scores above the threshold")

class SourceIdentificationResults(BaseModel):
    """Results approved in the source evaluation process"""
    topic: str = Field(..., description="Topic of the research")
    specialisation: str = Field(..., description="Specialisation of the research")
    date_of_approval: str = Field(..., description="Date when the research was conducted")
    total_sources_approved: int = Field(..., description="Number of sources that passed quality criteria")
    quality_threshold: float = Field(..., description="Minimum quality score required for approval")
    approved_sources: List[ApprovedSource] = Field(..., description="List of evaluated sources of a high quality with quality scores above the threshold")


# #Renamed this from the origial SourceEvaluationResults to SourceDiscoveryResults
# class SourceIdentificationResults(BaseModel):
#     """Results from the source evaluation phase."""
#     topic: str = Field(..., description="Topic of the research")
#     specialisation: str = Field(..., description="Specialisation of the research")
#     date_of_evaluation: str = Field(..., description="Date when the evaluation was conducted")
#     total_sources_evaluated: int = Field(..., description="Total number of sources evaluated")
#     total_sources_approved: int = Field(..., description="Number of sources that passed quality criteria")
#     quality_threshold: float = Field(..., description="Minimum quality score required for approval")
#     urls: List[EvaluatedSource] = Field(..., description="List of evaluated sources")

# This is the old source identification results - now replaced by the new source discovery results below
class EvaluatedSource(BaseModel):
    """Represents a source that has been evaluated for quality."""
    eval_source_no: int = Field(..., description="Should be the same as the pot_source_no from the SourceDiscoveryResults")
    eval_source_id: str = Field(..., description="Should inherit from the pot_source_id from the SourceDiscoveryResults")
    eval_source_url: str = Field(..., description="Should inherit from the pot_source_url from the SourceDiscoveryResults")
    eval_source_title: str = Field(..., description="Should inherit from the pot_source_title from the SourceDiscoveryResults")
    eval_source_source_type: str = Field(..., description="Should inherit from the pot_source_source_type from the SourceDiscoveryResults")
    eval_source_publisher: List[str] = Field(default_factory=list, description="Publisher if known")
    publication_date: List[str] = Field(default_factory=list, description="Publication date, if known, from the source or source metadata")
    author: List[str] = Field(default_factory=list, description="Author if known, if know, from the source or source metadata")
    relevance_score: float = Field(..., description="Relevance score (1-10)")
    credibility_score: float = Field(..., description="Credibility score (1-10)")
    recency_score: float = Field(..., description="Recency score (1-10)")
    total_score: float = Field(..., description="Combined quality score")
    accessible: bool = Field(..., description="Whether the source is accessible (not paywalled)")


# class SourceIdentificationResults(BaseModel):
#     topic: str = Field(..., description="Topic of the research")
#     specialisation: str = Field(default=specialisation, description="Specialisation of the research")
#     date_of_research: str = Field(..., description="Date when the research was conducted")
#     total_sources_found: int = Field(..., description="Total number of sources found")
#     urls: List[EvaluatedSource] = Field(..., description="List of sources found")

class SourceURL(BaseModel):
    url: str = Field(..., description="URL of the source")

class SourceIdentificationResultsURLonly(BaseModel):
    urls: List[SourceURL] = Field(..., description="List of source URLs")



# Models for Implications (1st, 2nd and 3rd order)
class ImplicationOrder(BaseModel):
    """Represents the order of an implication (1st, 2nd, or 3rd)."""
    order: int = Field(..., description="Order of implication (1, 2, or 3)")
    description: str = Field(..., description="Description of what this order means")

class ImplicationCategory(BaseModel):
    """Category for grouping implications."""
    name: str = Field(..., description="Name of the implication category")
    description: str = Field(..., description="Description of this category")

class Implication(BaseModel):
    """Represents a specific implication derived from market forces."""
    implication_id: str = Field(..., description="Unique identifier for this implication")
    implication_order: int = Field(..., description="Order of implication (1, 2, or 3)")
    implication_title: str = Field(..., description="Brief title of the implication")
    implication_description: str = Field(..., description="Detailed description of the implication")
    category: ImplicationCategory = Field(..., description="Category this implication belongs to")
    parent_implications_ids: List[str] = Field(default_factory=list, description="IDs of parent implications (if any)")
    parent_implications_names: List[str] = Field(default_factory=list, description="Names of parent implications (if any) obtained from FirstOrderImplication or SecondOrderImplication")
    parent_market_forces_ids: List[str] = Field(default_factory=list, description="IDs of parent market forces (if any) - For the FirstOrderImplication, Use the raw_market_force_id from the ResearchOutput, and for the SecondOrderImplication and ThirdOrderImplication, use the parent_market_forces_id from the FirstOrderImplication or SecondOrderImplication")
    parent_market_forces_names: List[str] = Field(default_factory=list, description="Names of parent market forces (if any) - For the FirstOrderImplication, Use the raw_market_force_name from the ResearchOutput, and for the SecondOrderImplication and ThirdOrderImplication, use the parent_market_forces_name from the FirstOrderImplication or SecondOrderImplication")
    impact_level: str = Field(..., description="Estimated impact level (High, Medium, Low) - with a rationale")
    time_horizon: str = Field(..., description="Expected time frame for manifestation - with a rationale")
    uncertainty: str = Field(..., description="Level of uncertainty (High, Medium, Low) - with a rationale")
    scenario_development: List[str] = Field(default_factory=list, description="For 2nd and 3rd order implications, Mini-scenarios illustrating how the implication might manifest")
    indicators: List[str] = Field(default_factory=list, description="For 2nd and 3rd order implications, Key indicators or signals that would suggest the implication or scenario is emerging")
    alternative_futures: List[str] = Field(default_factory=list, description="For 3rd order implications, Alternative futures based on different manifestations")
    wild_card_events: List[str] = Field(default_factory=list, description="For 3rd order implications, Wild card or black swan events that could accelerate or trigger the shift")
    business_relevance: List[str] = Field(default_factory=list, description="Specific relevance to the business if provided")
    strategic_considerations: List[str] = Field(default_factory=list, description="Strategic considerations arising from this implication, provide more than one")
    potential_opportunities: List[str] = Field(default_factory=list, description="Potential opportunities arising, provide more than one")
    potential_threats: List[str] = Field(default_factory=list, description="Potential threats or challenges arising, provide more than one")
    
    @field_validator('implication_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"IMP-{uuid.uuid4().hex[:8]}"

class FirstOrderImplication(BaseModel):
    """Represents a first-order implication derived from market forces."""
    first_order_implications: List[Implication] = Field(default_factory=list, description="List of first-order implications")

class SecondOrderImplication(BaseModel):
    """Represents a second-order implication derived from first-order implications."""
    second_order_implications: List[Implication] = Field(default_factory=list, description="List of second-order implications")

class ThirdOrderImplication(BaseModel):
    """Represents a third-order implication derived from second-order implications."""
    third_order_implications: List[Implication] = Field(default_factory=list, description="List of third-order implications")

class ImplicationAnalysisReport(BaseModel):
    """Complete report of implications analysis."""
    implications_report_title: str = Field(..., description="Title of the implications analysis report")
    implications_report_generation_date: str = Field(..., description="Report generation date")
    topic: str = Field(..., description="The topic the implications analysis is focused on")
    business_context: List[str] = Field(default_factory=list, description="Business context if provided")
    implications_report_executive_summary: str = Field(..., description="Concise executive summary of key findings")
    implications_report_methodology: str = Field(..., description="Description of the methodology used for implications analysis")
    first_order_implications: List[Implication] = Field(default_factory=list, description="List of first-order implications recieved from the analyse_first_order_implications task")
    second_order_implications: List[Implication] = Field(default_factory=list, description="List of second-order implications recieved from the analyse_second_order_implications task")
    third_order_implications: List[Implication] = Field(default_factory=list, description="List of third-order implications recieved from the analyse_third_order_implications task")
    cross_cutting_themes: List[str] = Field(default_factory=list, description="Cross-cutting themes identified across implications")
    strategic_recommendations: List[str] = Field(default_factory=list, description="Strategic recommendations based on implications analysis")
    critical_uncertainties: List[str] = Field(default_factory=list, description="Critical uncertainties identified in the analysis")
    conclusion: str = Field(..., description="Overall conclusion of the implications analysis")