# models.py
from pydantic import BaseModel, Field, HttpUrl, create_model
from typing import List, Optional, Dict, Union, Type, Any
from enum import Enum
from datetime import datetime

# EXISTING MODELS

# Research Plan for market forces
class Market_Force(BaseModel):
    market_force_id: int
    market_force_short_description: str
    market_force_long_description: str
    research_objectives: List[str]
    content_examples: List[str]
    minimum_sources: List[str]
    source_priority: List[str]
    quality_criteria: List[str]
    integration_approach: List[str]

class Market_Force_Plan(BaseModel):
    market_forces: List[Market_Force]

class Research_Strategy(BaseModel):
    """Research strategy model for interpreter agent output"""
    key_research_questions: List[str]
    core_areas_to_investigate: List[str]
    source_evaluation_framework: List[str]
    evidence_gathering_approach: List[str]
    integration_approach: List[str]

# NEW RESEARCH OUTPUT MODELS

# Source type enum for categorizing information sources
class SourceType(str, Enum):
    ACADEMIC = "academic"
    NEWS = "news"
    INDUSTRY_REPORT = "industry_report"
    CONSULTING = "consulting"
    PATENT = "patent"
    GOVERNMENT = "government"
    FUTURIST = "futurist"
    SOCIAL_MEDIA = "social_media"
    INTERVIEW = "interview"
    OTHER = "other"

# Confidence level enum
class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

# Time horizon enum
class TimeHorizon(str, Enum):
    IMMEDIATE = "immediate"  # 0-12 months
    SHORT_TERM = "short_term"  # 1-2 years
    MEDIUM_TERM = "medium_term"  # 2-5 years
    LONG_TERM = "long_term"  # 5-10 years
    FAR_FUTURE = "far_future"  # 10+ years

# Base research finding class - enhanced with additional fields
class ResearchFinding(BaseModel):
    source: str = Field(..., description="Source of the information")
    source_type: SourceType = Field(..., description="Type of source")
    title: str = Field(..., description="Title or headline of the finding")
    summary: str = Field(..., description="Summary of the key information")
    relevance: str = Field(..., description="Relevance to the market force being researched")
    date_published: Optional[str] = Field(None, description="Publication date if available")
    url: Optional[str] = Field(None, description="URL to the source if available")
    key_points: List[str] = Field(default_factory=list, description="List of key points from this source")
    confidence_level: ConfidenceLevel = Field(default=ConfidenceLevel.MEDIUM, description="Confidence in this finding")
    time_horizon: Optional[TimeHorizon] = Field(None, description="Time horizon this finding relates to")
    
    # Fields for integration and cross-referencing
    related_market_forces: List[str] = Field(default_factory=list, description="Related market forces this finding might impact")
    tags: List[str] = Field(default_factory=list, description="Tags for categorization and cross-referencing")
    
    # Field for raw content or quotes if needed
    original_content: Optional[str] = Field(None, description="Original quotes or content from source")

# Base research output with common fields across all research types
class BaseResearchOutput(BaseModel):
    market_force_id: Union[int, str] = Field(..., description="ID of the market force being researched")
    market_force_title: str = Field(..., description="Title of the market force")
    research_type: str = Field(..., description="Type of research conducted")
    summary: str = Field(..., description="Summary of research findings")
    key_insights: List[str] = Field(..., description="Key insights from this research")
    findings: List[ResearchFinding] = Field(..., description="Detailed findings")
    limitations: str = Field(..., description="Limitations of this research")
    research_date: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Date research was conducted")
    
    # Integration fields
    cross_cutting_themes: List[str] = Field(default_factory=list, description="Themes that cut across multiple research areas")
    contradictions: List[str] = Field(default_factory=list, description="Contradictions with other research findings")
    supporting_evidence: List[str] = Field(default_factory=list, description="Evidence supporting other research findings")

# Internet research model
class InternetResearch(BaseResearchOutput):
    research_type: str = Field(default="Internet Research", const=True)
    internet_research: str = Field(..., description="Comprehensive internet research findings")
    keywords_used: List[str] = Field(default_factory=list, description="Keywords used in the research")
    search_engines: List[str] = Field(default_factory=list, description="Search engines used")
    websites_consulted: List[str] = Field(default_factory=list, description="List of websites consulted")

# News analysis model
class NewsAnalysis(BaseResearchOutput):
    research_type: str = Field(default="News Analysis", const=True)
    news_analysis: str = Field(..., description="Comprehensive news analysis")
    media_sentiment: str = Field(..., description="Overall sentiment in media coverage")
    emerging_narratives: List[str] = Field(default_factory=list, description="Emerging narratives identified in news")
    time_period_covered: str = Field(..., description="Time period covered in the news analysis")
    publication_sources: List[str] = Field(default_factory=list, description="News sources analyzed")

# Patent research model
class PatentResearch(BaseResearchOutput):
    research_type: str = Field(default="Patent Research", const=True)
    patent_research: str = Field(..., description="Comprehensive patent research findings")
    innovation_trends: List[str] = Field(default_factory=list, description="Innovation trends identified")
    key_companies: List[str] = Field(default_factory=list, description="Key companies filing relevant patents")
    technology_implications: str = Field(..., description="Implications of the patent research")
    patent_filing_trends: Dict[str, int] = Field(default_factory=dict, description="Trends in patent filings over time")

# Consulting insights model
class ConsultingInsights(BaseResearchOutput):
    research_type: str = Field(default="Consulting Insights", const=True)
    consulting_insights: str = Field(..., description="Comprehensive consulting insights")
    strategic_recommendations: List[str] = Field(default_factory=list, description="Strategic recommendations from consultants")
    market_outlook: str = Field(..., description="Market outlook according to consulting firms")
    industry_challenges: List[str] = Field(default_factory=list, description="Industry challenges identified")
    consulting_firms: List[str] = Field(default_factory=list, description="Consulting firms whose reports were analyzed")

# Future trends model
class FutureTrends(BaseResearchOutput):
    research_type: str = Field(default="Future Trends", const=True)
    future_trends: str = Field(..., description="Comprehensive future trends analysis")
    timeframe_distribution: Dict[TimeHorizon, int] = Field(default_factory=dict, description="Distribution of trends by timeframe")
    potential_disruptions: List[str] = Field(default_factory=list, description="Potential market disruptions")
    visionary_perspectives: List[Dict[str, str]] = Field(default_factory=list, description="Perspectives from industry visionaries")
    scenario_analyses: List[Dict[str, Any]] = Field(default_factory=list, description="Different future scenarios analyzed")

# Document analysis model
class DocumentAnalysis(BaseResearchOutput):
    research_type: str = Field(default="Document Analysis", const=True)
    document_analysis: str = Field(..., description="Comprehensive document analysis")
    regulatory_insights: Optional[List[str]] = Field(None, description="Insights from regulatory documents")
    market_data: Optional[Dict[str, Any]] = Field(None, description="Key market data extracted from documents")
    document_types: List[str] = Field(default_factory=list, description="Types of documents analyzed")
    document_sources: List[str] = Field(default_factory=list, description="Sources of the documents analyzed")

# Final research synthesis model - used by the integration crew
class ResearchSynthesis(BaseModel):
    market_force_id: Union[int, str] = Field(..., description="ID of the market force being researched")
    market_force_title: str = Field(..., description="Title of the market force")
    market_force_description: str = Field(..., description="Full description of the market force")
    
    # Executive summary and key findings
    executive_summary: str = Field(..., description="Executive summary of all research")
    key_findings: List[str] = Field(..., description="Key findings across all research")
    
    # Integrated insights from all research types
    integrated_insights: Dict[str, Any] = Field(..., description="Integrated insights from all research types")
    
    # Evidence and supporting data
    supporting_evidence: List[ResearchFinding] = Field(..., description="Key supporting evidence")
    contradictory_evidence: List[ResearchFinding] = Field(default_factory=list, description="Contradictory evidence")
    
    # Impact analysis
    implications: Dict[str, List[str]] = Field(..., description="Implications for different stakeholders")
    time_horizon_analysis: Dict[TimeHorizon, List[str]] = Field(..., description="Analysis by time horizon")
    confidence_assessment: str = Field(..., description="Overall confidence assessment of findings")
    
    # Future outlook and recommendations
    future_outlook: str = Field(..., description="Future outlook based on integrated research")
    recommendations: List[str] = Field(..., description="Strategic recommendations based on findings")
    
    # Research metadata
    research_date: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Date research was synthesized")
    research_types_included: List[str] = Field(..., description="Types of research included in this synthesis")
    
    # References and sources
    references: List[Dict[str, str]] = Field(..., description="References to all sources")
    
    # Raw research data for traceability
    raw_research_data: Dict[str, Any] = Field(..., description="Raw data from individual research types")
    
    # Cross-cutting themes and patterns
    cross_cutting_themes: List[Dict[str, Any]] = Field(..., description="Themes that cut across multiple research areas")
    unexpected_connections: List[str] = Field(default_factory=list, description="Unexpected connections found")
    
    # Gaps and limitations
    research_gaps: List[str] = Field(default_factory=list, description="Gaps in the research")
    limitations: str = Field(..., description="Limitations of the integrated research")