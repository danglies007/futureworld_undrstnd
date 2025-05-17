from typing import List, Optional, Dict, Any, Literal
from pydantic import BaseModel, Field, field_validator
import uuid
import json
from datetime import date, datetime, time, timedelta

from pydantic_core.core_schema import nullable_schema


from config_competitor_analysis import RESEARCH_INPUTS

# Google VertexAI does not like OPtional, had to change to Nullable=true
# Changing from nullable=true to default_factory=list or default="" or default=0


specialisation = RESEARCH_INPUTS.get('specialisation', 'CompanyAnalysis')

class SourceLink(BaseModel):
    """Represents a link to a source with its title."""
    title: str = Field(..., description="Title of the source")
    url: str = Field(..., description="URL of the source link")
    date: str = Field(default="", description="Publication date for the source")

class AttributedItem(BaseModel):
    """Base model for any item that needs attribution."""
    content: str = Field(..., description="The actual content (fact, statistic, quote, etc.)")
    source_url: str = Field(..., description="URL where this information was found")
    source_text: str = Field(default="", description="Exact word-for-word extract from the source")
    source_name: str = Field(default="", description="Name of the source")
    quote_author: str = Field(default="", description="Author of the quote e.g. CEO Mr. John Doe")
    source_date: str = Field(default="", description="Date of the source")

# Models for Company Source Identification

class CompanySource(BaseModel):
    """Represents an identified source about a company."""
    source_id: str = Field(..., description="Unique identifier for the source")
    title: str = Field(..., description="Title of the source")
    url: str = Field(..., description="URL of the source")
    source_type: str = Field(..., description="Type: annual_report, financial_statement, press_release, news_article, analyst_report, etc.")
    publisher: str = Field(default="", description="Publisher of the source")
    source_date: str = Field(default="", description="Date of publication")
    author: str = Field(default="", description="Author of the source")
    relevance_score: float = Field(..., description="Relevance score (1-10)")
    description: str = Field(default="", description="Brief description of the source content")
    
    @field_validator('source_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"SRC-{uuid.uuid4().hex[:8]}"

class CompanySourceIdentificationResults(BaseModel):
    """Results of source identification for company analysis."""
    company_name: str = Field(..., description="Name of the company being analyzed")
    ticker_symbol: str = Field(default="", description="Stock ticker symbol, if applicable")
    industry: str = Field(default="", description="Industry the company operates in")
    date_of_identification: str = Field(..., description="Date when the sources were identified")
    total_sources_found: int = Field(..., description="Total number of sources found")
    internal_sources: List[CompanySource] = Field(default_factory=list, description="Sources from the company itself (annual reports, etc.)")
    external_sources: List[CompanySource] = Field(default_factory=list, description="Sources from external analysts and news")

# Models for Internal Analysis

class HistoricalValue(BaseModel):
    year: str = Field(..., description="Year or period")
    value: float = Field(..., description="Value for this period")

class FinancialMetric(BaseModel):
    """Represents a key financial metric with historical data."""
    metric_name: str = Field(..., description="Name of the financial metric")
    metric_description: str = Field(default="", description="Description of what this metric represents")
    unit: str = Field(..., description="Unit of measurement (USD, %, ratio, etc.)")
    current_value: float = Field(default=0, nullable=True, description="Most recent value")
    historical_values: List[HistoricalValue] = Field(default_factory=list, description="Historical values for this metric, typically found in previous years financial statements")
    trend: str = Field(default="", description="Trend description (increasing, decreasing, stable, volatile)")
    source: List[SourceLink] = Field(default_factory=list, description="Source of this information")

class FinancialMetricCategory(BaseModel):
    """A category of financial metrics."""
    category_name: str = Field(..., description="Name of the financial metric category")
    metrics: List[FinancialMetric] = Field(..., description="Financial metrics in this category")

# For BusinessSegment
class ProfitabilityMetric(BaseModel):
    """A profitability metric for a business segment."""
    metric_name: str = Field(..., description="Name of the profitability metric")
    value: float = Field(..., description="Value of the metric")


class BusinessSegment(BaseModel):
    """Represents a business segment or division of the company."""
    segment_name: str = Field(..., description="Name of the business segment")
    segment_description: str = Field(..., description="Description of the segment's activities")
    revenue: float = Field(default=0, nullable=True, description="Revenue of this segment - if revenue is not available use alternative metric for size e.g. net income etc")
    revenue_contribution: float = Field(default=0, nullable=True, description="Percentage of total revenue from this segment")
    growth_rate: float = Field(default=0, nullable=True, description="Growth rate of this segment")
    profitability_metrics: List[ProfitabilityMetric] = Field(default_factory=list, description="Key profitability metrics for this segment")
    key_products_services: List[str] = Field(default_factory=list, description="Key products or services in this segment")
    geographical_presence: List[str] = Field(default_factory=list, description="Geographical regions this segment operates in")
    strategic_focus: str = Field(default="", description="Strategic focus for this segment per company statements")
    source_statements: List[AttributedItem] = Field(default_factory=list, description="Direct statements from sources")
    
class StrategicPriority(BaseModel):
    """Represents a strategic priority stated by the company."""
    priority_id: str = Field(..., description="Unique identifier for this priority")
    priority_name: str = Field(..., description="Name/title of the strategic priority")
    priority_description: str = Field(..., description="Detailed description of the priority")
    related_initiatives: List[str] = Field(default_factory=list, description="Initiatives related to this priority, include any statements, data, or metrics relating to the initiative from company sources")
    expected_outcomes: List[str] = Field(default_factory=list, description="Expected outcomes from this priority, include any statements, data, or metrics relating to the outcome from company sources")
    timeline: str = Field(default="", description="Timeline for implementation or expected results - include any statements, data, or metrics relating to the timeline from company sources")
    investment_level: str = Field(default="", description="Level of investment (financial, resource allocation) - include any statements, data, or metrics relating to the investment from company sources")
    progress_indicators: List[str] = Field(default_factory=list, description="Indicators used to measure progress, include any statements, data, or metrics relating to the indicator from company sources")
    source_statements: List[AttributedItem] = Field(default_factory=list, description="Direct statements from sources")
    
    @field_validator('priority_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"STRAT-{uuid.uuid4().hex[:8]}"

class CapitalAllocation(BaseModel):
    """Represents how the company allocates its capital."""
    category: str = Field(..., description="Category of capital allocation")
    description: str = Field(..., description="Description of this allocation category")
    percentage: float = Field(default=0, nullable=True, description="Percentage of total capital allocation")
    amount: float = Field(default=0, nullable=True, description="Monetary amount allocated")
    currency: str = Field(default="", description="Currency of the amount")
    trend: str = Field(default="", description="Trend in this allocation (increasing, stable, decreasing)")
    rationale: str = Field(default="", description="Company's stated rationale for this allocation")
    source: List[SourceLink] = Field(default_factory=list, description="Source of this information")

class RiskFactor(BaseModel):
    """Represents a risk factor identified by the company."""
    risk_id: str = Field(..., description="Unique identifier for this risk")
    risk_name: str = Field(..., description="Name/title of the risk factor")
    risk_description: str = Field(default="", description="Detailed description of the risk")
    risk_category: str = Field(..., description="Category of risk (operational, financial, regulatory, etc.)")
    potential_impact: str = Field(..., description="Potential impact if risk materializes")
    mitigation_strategies: List[str] = Field(default_factory=list, description="Strategies to mitigate this risk")
    management_assessment: str = Field(default="", description="Management's assessment of likelihood/severity")
    source_statements: List[AttributedItem] = Field(default_factory=list, description="Direct statements from sources")
    
    @field_validator('risk_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"RISK-{uuid.uuid4().hex[:8]}"

class CostStructureItem(BaseModel):
    """Represents a component of a company's cost structure with flexible value types."""
    cost_category: str = Field(..., description="Category of cost (e.g., 'Technology investment')")
    value: str = Field(..., description="Value or description of the cost (can be numeric or descriptive)")
    percentage: str = Field(default="", description="Percentage of total costs, if available")
    notes: str = Field(default="", description="Additional notes about this cost component")

class BusinessModelComponent(BaseModel):
    """Component of the company's business model."""
    component_name: str = Field(..., description="Name of the business model component")
    component_description: str = Field(default="", description="Description of this component")
    strengths: List[str] = Field(default_factory=list, description="Strengths of this component")
    weaknesses: List[str] = Field(default_factory=list, description="Weaknesses of this component")
    evolution: str = Field(default="", description="How this component has evolved over time")
    future_direction: str = Field(default="", description="Likely future direction for this component")
    sources: List[SourceLink] = Field(default_factory=list, description="Sources for this analysis")

class BusinessModel(BaseModel):
    """Comprehensive representation of a company's business model."""
    model_id: str = Field(..., description="Unique identifier for this business model")
    model_description: str = Field(..., description="Overall description of the business model")
    value_creation: str = Field(..., description="How the company creates value for customers")
    value_capture: str = Field(..., description="How the company captures value (monetization)")
    revenue_streams: List[str] = Field(default_factory=list, description="Key revenue streams")
    cost_structure: List[CostStructureItem] = Field(default_factory=list, description="Breakdown of cost structure by category")
    key_resources: List[str] = Field(default_factory=list, description="Key resources required for the business model")
    key_activities: List[str] = Field(default_factory=list, description="Key activities performed in the business model")
    key_partnerships: List[str] = Field(default_factory=list, description="Key partnerships and supplier relationships")
    customer_segments: List[str] = Field(default_factory=list, description="Target customer segments")
    customer_relationships: str = Field(default="", description="How the company builds relationships with customers")
    channels: List[str] = Field(default_factory=list, description="Channels used to reach customers")
    scalability: str = Field(default="", description="Assessment of the business model's scalability")
    sustainability: str = Field(default="", description="Long-term sustainability assessment")
    defensibility: str = Field(default="", description="How defensible the business model is against competition")
    components: List[BusinessModelComponent] = Field(default_factory=list, description="Detailed components of the business model")
    evolution_history: List[str] = Field(default_factory=list, description="How the business model has evolved over time")
    future_direction: str = Field(default="", description="Anticipated future evolution of the business model")
    alignment: str = Field(default="", description="Alignment between described and actual business model")
    assessment: str = Field(default="", description="Overall assessment of the business model")
    
    @field_validator('model_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"BM-{uuid.uuid4().hex[:8]}"

class BusinessModelAnalysis(BaseModel):
    """Analysis of a company's business model(s) integrating internal and external perspectives."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    business_models: List[BusinessModel] = Field(..., description="Business models analyzed")
    internal_perspective: str = Field(default="", description="How the company describes its own business model")
    external_perspective: str = Field(default="", description="How external analysts perceive the business model") 
    model_alignment: str = Field(default="", description="Assessment of alignment between described and actual business model")
    sustainability_assessment: str = Field(default="", description="Assessment of the business model's sustainability")
    coherence_assessment: str = Field(default="", description="Assessment of how well business model components fit together")
    business_model_evolution: str = Field(default="", description="How the business model has evolved and may evolve")
    sources: List[SourceLink] = Field(default_factory=list,  description="Sources used for this analysis")
    analysis_summary: str = Field(..., description="Summary of key findings from the business model analysis")

# New models to add to competitor_analysis_models.py

# Alternative approach for mission_vision_values
# class MissionVisionValues(BaseModel):
#     """Company's stated mission, vision, and values."""
#     mission: str = Field(default=None, nullable=True, description="Company's mission statement")
#     vision: str = Field(default=None, nullable=True, description="Company's vision statement")
#     values: List[str] = Field(default=None, nullable=True, description="Company's core values")


class AnnualReportAnalysisResult(BaseModel):
    """Analysis results from company annual reports."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    company_overview: str = Field(..., description="Overview of the company from annual reports")
    business_model: str = Field(..., description="Description of the company's business model")
    # mission_vision_values: MissionVisionValues = Field(default=None, nullable=True)
    business_segments: List[BusinessSegment] = Field(default_factory=list, description="Key business segments")
    strategic_priorities: List[StrategicPriority] = Field(default_factory=list, description="Strategic priorities from annual reports")
    risk_factors: List[RiskFactor] = Field(default_factory=list, description="Risk factors identified from annual reports")
    leadership_statements: List[AttributedItem] = Field(default_factory=list, description="Significant statements from leadership")
    future_outlook: str = Field(default="", description="Company's stated future outlook from annual reports")
    management_discussion_and_analysis: List[AttributedItem] = Field(default_factory=list, description="Management's discussion and analysis")
    sources_analyzed: List[SourceLink] = Field(..., description="Annual report sources analyzed")

# For FinancialAnalysisResult

class SegmentFinancialPerformance(BaseModel):
    """Financial performance metrics for a specific business segment."""
    segment_name: str = Field(..., description="Name of the business segment")
    metrics: List[FinancialMetric] = Field(..., description="Financial metrics for this segment")

class FinancialAnalysisResult(BaseModel):
    """Analysis results from company financial statements."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    financial_metrics: List[FinancialMetricCategory] = Field(..., description="Financial metrics by category")
    capital_allocation: List[CapitalAllocation] = Field(default_factory=list, description="Capital allocation breakdown")
    segment_financial_performance: List[SegmentFinancialPerformance] = Field(default_factory=list, description="Financial performance by business segment")
    sources_analyzed: List[SourceLink] = Field(..., description="Financial document sources analyzed")

class StrategyAnalysisResult(BaseModel):
    """Analysis results from company strategy documents."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    strategy_overview: str = Field(..., description="Overview of the company's strategy")
    strategic_priorities: List[StrategicPriority] = Field(..., description="Strategic priorities from strategy documents")
    business_model_components: List[BusinessModelComponent] = Field(default_factory=list, description="Components of the business model")
    innovation_focus: str = Field(default="", description="Focus areas for innovation and R&D")
    market_positioning: str = Field(default="", description="Market positioning statements")
    competitive_advantages: List[str] = Field(default_factory=list, description="Claimed competitive advantages")
    growth_strategies: List[AttributedItem] = Field(default_factory=list, description="Growth strategies (organic/inorganic)")
    digital_transformation: str = Field(default="", description="Digital transformation initiatives")
    sustainability_strategy: str = Field(default="", description="ESG/Sustainability strategy")
    sources_analyzed: List[SourceLink] = Field(..., description="Strategy document sources analyzed")



class CompanyInternalAnalysis(BaseModel):
    """Complete internal analysis of a company based on company documents."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    company_overview: str = Field(..., description="Overview of the company from internal documents")
    # mission_vision_values: MissionVisionValues = Field(default=None, nullable=True, description="Company's stated mission, vision, and values")
    strategic_priorities: List[StrategicPriority] = Field(..., description="Strategic priorities stated by the company")
    business_model: str = Field(..., description="Description of the company's business model")
    business_segments: List[BusinessSegment] = Field(default_factory=list, description="Key business segments")
    growth_strategies: List[AttributedItem] = Field(default_factory=list, description="Growth strategies (organic/inorganic)")
    financial_performance: List[FinancialMetricCategory] = Field(..., description="Financial performance metrics by category")
    market_positioning: str = Field(default="", description="Market positioning statements")
    competitive_advantages: List[str] = Field(default_factory=list, description="Claimed competitive advantages")
    capital_allocation: List[CapitalAllocation] = Field(..., description="Capital allocation breakdown")
    risk_factors: List[RiskFactor] = Field(..., description="Risk factors identified by the company")
    leadership_statements: List[AttributedItem] = Field(default_factory=list, description="Significant statements from leadership")
    future_outlook: str = Field(default="", description="Company's stated future outlook")
    sources_analyzed: List[SourceLink] = Field(..., description="Sources analyzed for this internal analysis")
    analysis_summary: str = Field(..., description="Summary of key findings from internal analysis")

# Models for External Analysis


# For CompetitorAssessment
class ComparisonMetric(BaseModel):
    """A metric for comparing companies."""
    category: str = Field(..., description="Category of the metric")
    metric_name: str = Field(..., description="Name of the metric")
    company_value: str = Field(..., description="Value for the analyzed company")
    competitor_value: str = Field(..., description="Value for the competitor")
    difference: str = Field(default="", description="Difference description")

class CompetitorAssessment(BaseModel):
    """Represents an assessment of a key competitor."""
    competitor_name: str = Field(..., description="Name of the competitor")
    competitor_description: str = Field(..., description="Brief description of the competitor")
    relative_market_position: str = Field(..., description="Relative market position compared to analyzed company")
    competitive_advantages: List[str] = Field(default_factory=list, description="Competitive advantages of this competitor")
    competitive_disadvantages: List[str] = Field(default_factory=list, description="Competitive disadvantages of this competitor")
    key_strategies: List[str] = Field(default_factory=list, description="Key strategies being pursued by this competitor")
    recent_developments: List[AttributedItem] = Field(default_factory=list, description="Recent significant developments")
    comparison_metrics: List[ComparisonMetric] = Field(default_factory=list, description="Comparative metrics vs. analyzed company")
    threat_level: str = Field(..., description="Assessment of threat level (high, medium, low) - also provide rationale (and data if available) for this assessment")
    sources: List[SourceLink] = Field(default_factory=list, description="Sources for this competitor assessment")

class MarketTrend(BaseModel):
    """Represents a market trend affecting the company."""
    trend_id: str = Field(..., description="Unique identifier for this trend")
    trend_name: str = Field(..., description="Name of the market trend")
    trend_description: str = Field(..., description="Detailed description of the trend")
    potential_impact: str = Field(..., description="Potential impact on the company")
    timeframe: str = Field(..., description="Timeframe for this trend (short, medium, long term) - provide rationale (and data if available) for this assessment")
    industry_adoption: str = Field(..., description="Level of adoption in the industry - provide rationale (and data if available) for this assessment")
    company_positioning: str = Field(..., description="How the company is positioned for this trend - provide rationale (and data if available) for this assessment")
    supporting_evidence: List[AttributedItem] = Field(default_factory=list, description="Evidence supporting this trend")
    
    @field_validator('trend_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"TREND-{uuid.uuid4().hex[:8]}"

class AnalystPerspective(BaseModel):
    """Represents a perspective from a financial/industry analyst."""
    analyst_name: str = Field(default="", description="Name of the analyst")
    firm: str = Field(default="", description="Name of the analyst's firm or source of this perspective")
    rating: str = Field(default="", description="Rating (buy, hold, sell, etc.)")
    target_price: float = Field(default=0, nullable=True, description="Target price, if provided")
    summary: str = Field(..., description="Summary of the analyst's view")
    strengths_identified: List[str] = Field(default_factory=list, description="Strengths identified by the analyst - do not make this up, if you cannot find info leave it blank")
    concerns_identified: List[str] = Field(default_factory=list, description="Concerns identified by the analyst - do not make this up, if you cannot find info leave it blank")
    key_assumptions: List[str] = Field(default_factory=list, description="Key assumptions made by the analyst - do not make this up, if you cannot find info leave it blank")
    date: str = Field(..., description="Date of this perspective")
    source: List[SourceLink] = Field(..., description="Source of this perspective")

class NewsHighlight(BaseModel):
    """Represents a significant news item about the company."""
    highlight_id: str = Field(..., description="Unique identifier for this news highlight")
    title: str = Field(..., description="Title of the news item")
    date: str = Field(..., description="Date of publication")
    summary: str = Field(..., description="Summary of the news item")
    impact_assessment: str = Field(..., description="Assessment of potential impact on the company")
    market_reaction: str = Field(default="", description="How the market reacted, if applicable")
    source: List[SourceLink] = Field(..., description="Source of this news item")
    
    @field_validator('highlight_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"NEWS-{uuid.uuid4().hex[:8]}"

class NewsMediaAnalysisResult(BaseModel):
    """Analysis results from news and media coverage."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    company_perception: str = Field(..., description="Overall external perception of the company")
    news_highlights: List[NewsHighlight] = Field(..., description="Significant recent news")
    key_events: List[AttributedItem] = Field(default_factory=list, description="Important events affecting the company")
    leadership_perception: str = Field(default="", description="External perception of company leadership")
    product_launches: List[AttributedItem] = Field(default_factory=list, description="Product/service launches and their market reception")
    company_culture: str = Field(default="", description="External perception of company culture")
    crisis_management: List[AttributedItem] = Field(default_factory=list, description="Assessment of company's crisis responses")
    controversies: List[AttributedItem] = Field(default_factory=list, description="Public controversies or challenges")
    media_sentiment_trend: str = Field(..., description="Trend in media sentiment (positive, negative, neutral)")
    sources_analyzed: List[SourceLink] = Field(..., description="News and media sources analyzed")

# For ExternalFinancialAnalysisResult
class ValuationMetric(BaseModel):
    """A valuation metric with industry comparison."""
    metric_name: str = Field(..., description="Name of the valuation metric")
    company_value: str = Field(..., description="Value for the company")
    industry_average: str = Field(default="", description="Industry average")
    comparison: str = Field(default="", description="Comparison to industry")

class StrengthWeaknessCategory(BaseModel):
    """A category of financial strengths or weaknesses."""
    category: str = Field(..., description="Category name")
    items: List[str] = Field(default_factory=list, description="Items in this category")

class ExternalFinancialAnalysisResult(BaseModel):
    """Analysis results from external financial analyses."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    financial_performance_external: List[FinancialMetricCategory] = Field(..., description="Financial performance according to external sources")
    analyst_perspectives: List[AnalystPerspective] = Field(default_factory=list, description="Perspectives from industry/financial analysts")
    stock_performance: str = Field(default="", description="Stock price performance assessment")
    valuation_metrics: List[ValuationMetric] = Field(default_factory=list, description="Key valuation metrics compared to industry")
    financial_strengths: List[StrengthWeaknessCategory] = Field(default_factory=list, description="Identified financial strengths")
    financial_weaknesses: List[StrengthWeaknessCategory] = Field(default_factory=list, description="Identified financial weaknesses")
    capital_allocation: str = Field(default="", description="Commentary on capital allocation decisions")
    financial_risks: List[str] = Field(default_factory=list, description="Financial risks highlighted by external analysts")
    comparison_with_competitors: List[str] = Field(default_factory=list, description="Comparison with key competitors")
    sources_analyzed: List[SourceLink] = Field(..., description="Financial analysis sources analyzed")

# For MarketPositionAnalysisResult

class MarketShareItem(BaseModel):
    """Market share data for a specific segment, region, or product."""
    category: str = Field(..., description="Category (segment, region, product line)")
    category_name: str = Field(..., description="Name of the specific category item")
    market_share: float = Field(..., description="Market share percentage")
    trend: str = Field(default="", description="Trend description")
    source: List[SourceLink] = Field(default_factory=list, description="Source of this information")

class MarketPositionAnalysisResult(BaseModel):
    """Analysis results regarding market position and competitive landscape."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    industry_position: str = Field(default="", description="Position in the industry according to external sources")
    competitors: List[CompetitorAssessment] = Field(..., description="Assessment of key competitors")
    competitor_market_assessment: str = Field(default="", description="Market assessment from key competitors")
    market_trends: List[MarketTrend] = Field(..., description="Relevant market trends")
    customer_perception: str = Field(default="", description="How customers perceive the company")
    market_share_data: List[MarketShareItem] = Field(default_factory=list, description="Market share estimates and trends")
    competitive_advantages_external: List[str] = Field(default_factory=list, description="Externally recognized competitive advantages")
    competitive_disadvantages_external: List[str] = Field(default_factory=list, description="Externally recognized competitive disadvantages")
    esg_assessment: str = Field(default="", description="Environmental, Social, Governance assessment")
    sources_analyzed: List[SourceLink] = Field(..., description="Market and competitive analysis sources analyzed")

class SWOT(BaseModel):
    """SWOT analysis based on external perspectives."""
    strengths: List[AttributedItem] = Field(..., description="Identified strengths with sources")
    weaknesses: List[AttributedItem] = Field(..., description="Identified weaknesses with sources")
    opportunities: List[AttributedItem] = Field(..., description="Identified opportunities with sources")
    threats: List[AttributedItem] = Field(..., description="Identified threats with sources")

class CompanyExternalAnalysis(BaseModel):
    """Complete external analysis of a company based on external sources."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    company_perception: str = Field(..., description="Overall external perception of the company")
    industry_position: str = Field(..., description="Position in the industry according to external sources")
    competitors: List[CompetitorAssessment] = Field(..., description="Assessment of key competitors")
    market_trends: List[MarketTrend] = Field(..., description="Relevant market trends")
    analyst_perspectives: List[AnalystPerspective] = Field(default_factory=list, description="Perspectives from multiple industry/financial analysts")
    news_highlights: List[NewsHighlight] = Field(..., description="Significant recent news")
    financial_performance_external: List[FinancialMetricCategory] = Field(..., description="Financial performance according to external sources")
    swot_analysis: SWOT = Field(..., description="SWOT analysis from external perspective")
    customer_perception: str = Field(default="", description="How customers perceive the company")
    esg_assessment: str = Field(default="", description="Environmental, Social, Governance assessment")
    sources_analyzed: List[SourceLink] = Field(..., description="Sources analyzed for this external analysis")
    analysis_summary: str = Field(..., description="Summary of key findings from external analysis")

# Models for Integrated Analysis

class CompetitiveAdvantage(BaseModel):
    """Assessment of a competitive advantage."""
    advantage_id: str = Field(..., description="Unique identifier for this advantage")
    advantage_name: str = Field(..., description="Name of the competitive advantage")
    advantage_description: str = Field(..., description="Detailed description of the advantage")
    sustainability: str = Field(..., description="Assessment of how sustainable this advantage is")
    internal_evidence: List[AttributedItem] = Field(default_factory=list, description="Evidence from company documents")
    external_evidence: List[AttributedItem] = Field(default_factory=list, description="Evidence from external sources")
    
    @field_validator('advantage_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"ADV-{uuid.uuid4().hex[:8]}"

class CompetitivePositionAnalysis(BaseModel):
    """Analysis of a company's competitive position integrating internal and external perspectives."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    market_positioning: str = Field(..., description="Analysis of market positioning")
    competitive_advantages: List[CompetitiveAdvantage] = Field(..., description="Identified competitive advantages")
    competitive_disadvantages: List[AttributedItem] = Field(default_factory=list, description="Identified competitive disadvantages")
    key_competitors: List[CompetitorAssessment] = Field(..., description="Assessment of key competitors")
    points_of_differentiation: List[str] = Field(default_factory=list, description="Points of differentiation (real vs. perceived)")
    sustainability_assessment: str = Field(..., description="Assessment of how sustainable the competitive advantages are")
    customer_perception: str = Field(default="", description="Customer perception and brand strength")
    emerging_threats: List[str] = Field(default_factory=list, description="Emerging competitive threats")
    defensive_moats: List[str] = Field(default_factory=list, description="Defensive moats and barriers to entry")
    internal_external_alignment: str = Field(..., description="Assessment of alignment between internal claims and external validation")
    sources: List[SourceLink] = Field(default_factory=list, description="Sources used for this analysis")
    analysis_summary: str = Field(..., description="Summary of key findings from the competitive position analysis")

class KeyInsight(BaseModel):
    """Key insight from the integrated analysis."""
    insight_id: str = Field(..., description="Unique identifier for this insight")
    insight_title: str = Field(..., description="Brief title for this insight")
    insight_description: str = Field(..., description="Detailed description of the insight")
    supporting_internal_evidence: List[AttributedItem] = Field(default_factory=list, description="Supporting evidence from internal analysis")
    supporting_external_evidence: List[AttributedItem] = Field(default_factory=list, description="Supporting evidence from external analysis")
    implications: List[str] = Field(default_factory=list, description="Implications of this insight")
    confidence_level: str = Field(..., description="Confidence level in this insight (high, medium, low)")
    
    @field_validator('insight_id', mode='before')
    @classmethod
    def set_id_if_none(cls, v):
        return v or f"INSIGHT-{uuid.uuid4().hex[:8]}"

class StrategicInsightsAnalysis(BaseModel):
    """Analysis of strategic insights by comparing internal priorities with external market realities."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    strategic_analysis: str = Field(..., description="Analysis of company strategy")
    key_insights: List[KeyInsight] = Field(..., description="Key insights from the integrated analysis")
    strategic_priorities_alignment: str = Field(..., description="Assessment of alignment between strategic priorities and market opportunities")
    execution_capacity: str = Field(..., description="Analysis of execution capacity versus strategic ambitions")
    performance_assessment: str = Field(..., description="Assessment of performance against stated strategic objectives")
    strategic_blind_spots: List[str] = Field(default_factory=list, description="Identified strategic blind spots and cognitive biases")
    resource_allocation: str = Field(..., description="Assessment of resource allocation alignment with strategy")
    strategic_options: List[str] = Field(default_factory=list, description="Potential strategic options available")
    key_risks: List[AttributedItem] = Field(default_factory=list, description="Key risks to strategic execution")
    strategic_inflection_points: List[str] = Field(default_factory=list, description="Strategic inflection points and decision triggers")
    sources: List[SourceLink] = Field(default_factory=list, description="Sources used for this analysis")
    analysis_summary: str = Field(..., description="Summary of key findings from the strategic insights analysis")

class PERSTELFactor(BaseModel):
    """A factor in PERSTEL analysis."""
    factor_type: str = Field(..., description="Type of factor (Political, Economic, Regulatory, Social, Technological, Environmental, Legal)")
    factor_name: str = Field(..., description="Name of this specific factor")
    factor_description: str = Field(..., description="Detailed description of the factor")
    potential_impact: str = Field(..., description="Potential impact on the company")
    company_response: str = Field(default="", description="How the company is responding to this factor")
    sources: List[SourceLink] = Field(default_factory=list, description="Sources for this factor")

class PERSTELDimensionAssessment(BaseModel):
    """Assessment of one dimension of the PERSTEL analysis."""
    dimension: str = Field(..., description="Name of the PERSTEL dimension")
    key_factors: List[str] = Field(default_factory=list, description="Key factors in this dimension")
    company_awareness: str = Field(default="", description="Company's awareness of these factors")
    future_developments: str = Field(default="", description="Potential future developments")
    comparative_positioning: str = Field(default="", description="Positioning vs. competitors")

class PERSTELAnalysis(BaseModel):
    """Analysis applying the PERSTEL framework to macro factors affecting the company."""
    company_name: str = Field(..., description="Name of the company")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    perstel_analysis: List[PERSTELFactor] = Field(..., description="PERSTEL analysis factors")
    dimension_assessments: List[PERSTELDimensionAssessment] = Field(default_factory=list, description="Assessments for each PERSTEL dimension")
    company_awareness: str = Field(..., description="Overall assessment of company's awareness of macro factors")
    blind_spots: List[str] = Field(default_factory=list, description="Potential blind spots or underappreciated factors")
    comparative_positioning: str = Field(..., description="Overall assessment of positioning vs. competitors")
    future_implications: str = Field(..., description="Implications of macro factors for future strategy")
    perstel_summary: str = Field(..., description="Summary of PERSTEL analysis findings")
    sources: List[SourceLink] = Field(..., description="Sources used in this analysis")


#  Old CompanyIntegratedAnalysis
# class CompanyIntegratedAnalysis(BaseModel):
#     """Comprehensive integrated analysis combining internal and external perspectives."""
#     company_name: str = Field(..., description="Name of the company")
#     analysis_date: str = Field(..., description="Date when the analysis was conducted")
#     executive_summary: str = Field(..., description="Executive summary of key findings")
#     company_background: str = Field(..., description="Background and history of the company")
#     business_model_analysis: List[BusinessModel] = Field(..., description="Analysis of business model(s)")
#     market_positioning: Optional[str] = Field(None, description="Analysis of market positioning")
#     competitive_advantages: List[CompetitiveAdvantage] = Field(..., description="Identified competitive advantages")
#     competitive_disadvantages: List[AttributedItem] = Field(default_factory=list, description="Identified competitive disadvantages")
#     performance_assessment: str = Field(..., description="Assessment of overall performance")
#     strategic_analysis: str = Field(..., description="Analysis of company strategy")
#     future_outlook: Optional[str] = Field(None, description="Outlook for the company's future")
#     key_insights: List[KeyInsight] = Field(..., description="Key insights from the integrated analysis")
#     perstel_analysis: List[PERSTELFactor] = Field(default_factory=list, description="PERSTEL analysis factors")
#     strategic_options: List[str] = Field(default_factory=list, description="Potential strategic options available")
#     key_risks: List[AttributedItem] = Field(default_factory=list, description="Key risks facing the company")
#     sources: List[SourceLink] = Field(..., description="All sources used in the integrated analysis")
#     recommendations: Optional[List[str]] = Field(None, description="Strategic recommendations based on analysis")    

class CompanyIntegratedAnalysis(BaseModel):
    """Comprehensive integrated analysis combining all detailed analyses into a cohesive view."""
    company_name: str = Field(..., description="Name of the company")
    ticker_symbol: str = Field(default="", description="Stock ticker symbol if applicable")
    industry: str = Field(default="", description="Industry the company operates in")
    analysis_date: str = Field(..., description="Date when the analysis was conducted")
    executive_summary: str = Field(..., description="Executive summary of key findings")
    company_background: str = Field(..., description="Background and history of the company")
    business_model_analysis: BusinessModelAnalysis = Field(..., description="Complete business model analysis")
    competitive_position_analysis: CompetitivePositionAnalysis = Field(..., description="Complete competitive position analysis")
    strategic_insights_analysis: StrategicInsightsAnalysis = Field(..., description="Complete strategic insights analysis")
    perstel_analysis: PERSTELAnalysis = Field(..., description="Complete PERSTEL analysis")
    # internal_analysis_reference: CompanyInternalAnalysis = Field(..., description="Reference to the original internal analysis")
    # external_analysis_reference: CompanyExternalAnalysis = Field(..., description="Reference to the original external analysis")
    internal_external_alignment: str = Field(..., description="Assessment of overall alignment between internal and external perspectives")
    alignment_areas: List[str] = Field(default_factory=list, description="Areas where internal and external perspectives strongly align")
    misalignment_areas: List[str] = Field(default_factory=list, description="Areas where internal and external perspectives significantly differ")
    performance_assessment: str = Field(..., description="Integrated assessment of overall performance")
    future_outlook: str = Field(..., description="Integrated outlook for the company's future")
    strategic_options: List[str] = Field(default_factory=list, description="Potential strategic options available")
    key_risks: List[AttributedItem] = Field(default_factory=list, description="Key risks facing the company")
    recommendations: List[str] = Field(default_factory=list, description="Strategic recommendations based on all analyses")
    recommendation_rationales: List[AttributedItem] = Field(default_factory=list, description="Rationales for each recommendation with supporting evidence")
    sources: List[SourceLink] = Field(..., description="All sources used in the integrated analysis")

# Research Input Config

class CompanyAnalysisInputs(BaseModel):
    """Configuration for company analysis research."""
    company_name: str = Field(..., description="Name of the company to analyze")
    ticker_symbol: str = Field(default="", description="Stock ticker symbol if applicable")
    industry: str = Field(default="", description="Industry the company operates in")
    specialisation: str = Field(default="CompanyAnalysis", description="Type of analysis specialization")
    time_period: str = Field(default="", description="Time period for analysis (e.g., '2020-2023')")
    focus_areas: List[str] = Field(default_factory=list, description="Specific areas to focus on")
    competitor_names: List[str] = Field(default_factory=list, description="Known key competitors to include")


