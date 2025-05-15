from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
load_dotenv()

# Ignore warnings
import warnings
from pydantic import PydanticDeprecatedSince20
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

# File management imports
import os
import datetime

# Debugging imports
import litellm
litellm._turn_on_debug()

# Import LLMs
from config.llm_config import (
    llm_gpt4o, 
    llm_gpt4o_mini,
    llm_gpt4o_mini_accurate,
    llm_gpt4o_accurate,
    llm_claude_3_7_sonnet,
    llm_claude_3_5_sonnet,
    llm_gemini_2_5_pro,
    llm_gemini_2_0_flash,
    llm_gemini_2_5_flash
)

# Import CrewAI tools
from crewai_tools import (
    FirecrawlCrawlWebsiteTool,
    FirecrawlScrapeWebsiteTool,
    FirecrawlSearchTool,
    SerperDevTool, 
    PDFSearchTool,
    ScrapeWebsiteTool,
    BraveSearchTool,
    ScrapflyScrapeWebsiteTool,
    SeleniumScrapingTool
)

# Import Custom tools
from tools.file_downloader import FileDownloaderTool

# Import Research variables to support naming
from config import RESEARCH_INPUTS

# Import Pydantic models
from models import (
    CompanySourceIdentificationResults,
    CompanyInternalAnalysis,
    CompanyExternalAnalysis,
    IntegratedCompanyAnalysis,
    CompanySource,
    BusinessSegment,
    StrategicPriority,
    FinancialMetric,
    CapitalAllocation,
    RiskFactor,
    CompetitorAssessment,
    MarketTrend,
    AnalystPerspective,
    NewsHighlight,
    SWOT,
    CompetitiveAdvantage,
    KeyInsight,
    PERSTELFactor,
    BusinessModelComponent
)

# ===========================
# Internal Analysis Crew
# ===========================

@CrewBase
class InternalAnalysisCrew():
    """Company Internal Analysis Crew"""

    research_inputs = RESEARCH_INPUTS
    agents_config = 'config/internal_agents.yaml'
    tasks_config = 'config/internal_tasks.yaml'
    
    @agent
    def company_source_identifier(self) -> Agent:
        return Agent(
            config=self.agents_config['company_source_identifier'],
            llm=llm_gpt4o_accurate,
            tools=[BraveSearchTool(), ScrapeWebsiteTool()],
            verbose=True,
            cache=True,
            function_calling_llm=llm_gpt4o
        )

    @agent
    def annual_report_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['annual_report_analyzer'],
            llm=llm_gpt4o_accurate,
            tools=[FileDownloaderTool(), PDFSearchTool()],
            verbose=True,
            respect_context_window=True,
            cache=True,
            function_calling_llm=llm_gpt4o
        )

    @agent
    def financial_statement_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_statement_analyst'],
            llm=llm_gpt4o_accurate,
            tools=[FileDownloaderTool(), PDFSearchTool()],
            verbose=True,
            respect_context_window=True,
            cache=True,
            function_calling_llm=llm_gpt4o
        )

    @agent
    def strategy_document_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['strategy_document_analyst'],
            llm=llm_gpt4o_accurate,
            tools=[FileDownloaderTool(), PDFSearchTool()],
            verbose=True,
            respect_context_window=True,
            cache=True,
            function_calling_llm=llm_gpt4o
        )

    @agent
    def internal_analysis_consolidator(self) -> Agent:
        return Agent(
            config=self.agents_config['internal_analysis_consolidator'],
            llm=llm_gpt4o_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True
        )

    @task
    def identify_company_internal_sources(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['identify_company_internal_sources'],
            output_file=f'outputs/internal_sources_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=CompanySourceIdentificationResults
        )

    @task
    def analyze_annual_reports(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['analyze_annual_reports'],
            output_file=f'outputs/annual_report_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[self.identify_company_internal_sources()],
            async_execution=False,
            output_pydantic=CompanyInternalAnalysis
        )

    @task
    def analyze_financial_statements(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['analyze_financial_statements'],
            output_file=f'outputs/financial_statement_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[self.identify_company_internal_sources()],
            async_execution=False,
            output_pydantic=CompanyInternalAnalysis
        )

    @task
    def analyze_strategy_documents(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['analyze_strategy_documents'],
            output_file=f'outputs/strategy_document_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[self.identify_company_internal_sources()],
            async_execution=False,
            output_pydantic=CompanyInternalAnalysis
        )

    @task
    def consolidate_internal_analysis(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['consolidate_internal_analysis'],
            output_file=f'outputs/consolidated_internal_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[
                self.analyze_annual_reports(),
                self.analyze_financial_statements(),
                self.analyze_strategy_documents()
            ],
            output_pydantic=CompanyInternalAnalysis
        )

    @crew
    def crew(self) -> Crew:
        """Creates the InternalAnalysisCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

# ===========================
# External Analysis Crew
# ===========================

@CrewBase
class ExternalAnalysisCrew():
    """Company External Analysis Crew"""

    research_inputs = RESEARCH_INPUTS
    agents_config = 'config/external_agents.yaml'
    tasks_config = 'config/external_tasks.yaml'
    
    @agent
    def external_source_identifier(self) -> Agent:
        return Agent(
            config=self.agents_config['external_source_identifier'],
            llm=llm_gpt4o_accurate,
            tools=[BraveSearchTool(), ScrapeWebsiteTool()],
            verbose=True,
            cache=True,
            function_calling_llm=llm_gpt4o
        )

    @agent
    def news_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['news_analyst'],
            llm=llm_gpt4o_accurate,
            tools=[ScrapeWebsiteTool(), FileDownloaderTool(), PDFSearchTool()],
            verbose=True,
            respect_context_window=True,
            cache=True,
            function_calling_llm=llm_gpt4o
        )

    @agent
    def financial_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_analyst'],
            llm=llm_gpt4o_accurate,
            tools=[ScrapeWebsiteTool(), FileDownloaderTool(), PDFSearchTool()],
            verbose=True,
            respect_context_window=True,
            cache=True,
            function_calling_llm=llm_gpt4o
        )

    @agent
    def market_position_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['market_position_analyst'],
            llm=llm_gpt4o_accurate,
            tools=[ScrapeWebsiteTool(), FileDownloaderTool(), PDFSearchTool()],
            verbose=True,
            respect_context_window=True,
            cache=True,
            function_calling_llm=llm_gpt4o
        )

    @agent
    def external_analysis_consolidator(self) -> Agent:
        return Agent(
            config=self.agents_config['external_analysis_consolidator'],
            llm=llm_gpt4o_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True
        )

    @task
    def identify_company_external_sources(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['identify_company_external_sources'],
            output_file=f'outputs/external_sources_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=CompanySourceIdentificationResults
        )

    @task
    def analyze_news_and_media(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['analyze_news_and_media'],
            output_file=f'outputs/news_media_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[self.identify_company_external_sources()],
            async_execution=False,
            output_pydantic=CompanyExternalAnalysis
        )

    @task
    def analyze_external_financials(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['analyze_external_financials'],
            output_file=f'outputs/external_financial_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[self.identify_company_external_sources()],
            async_execution=False,
            output_pydantic=CompanyExternalAnalysis
        )

    @task
    def analyze_market_position(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['analyze_market_position'],
            output_file=f'outputs/market_position_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[self.identify_company_external_sources()],
            async_execution=False,
            output_pydantic=CompanyExternalAnalysis
        )

    @task
    def consolidate_external_analysis(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['consolidate_external_analysis'],
            output_file=f'outputs/consolidated_external_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[
                self.analyze_news_and_media(),
                self.analyze_external_financials(),
                self.analyze_market_position()
            ],
            output_pydantic=CompanyExternalAnalysis
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ExternalAnalysisCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

# ===========================
# Integrated Analysis Crew
# ===========================

@CrewBase
class IntegratedAnalysisCrew():
    """Company Integrated Analysis Crew"""

    research_inputs = RESEARCH_INPUTS
    agents_config = 'config/integrated_agents.yaml'
    tasks_config = 'config/integrated_tasks.yaml'
    
    # Input from previous crews
    internal_analysis = None
    external_analysis = None
    
    def __init__(self, internal_analysis, external_analysis):
        self.internal_analysis = internal_analysis
        self.external_analysis = external_analysis
        super().__init__()
    
    @agent
    def business_model_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['business_model_analyst'],
            llm=llm_gpt4o_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True
        )

    @agent
    def competitive_position_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['competitive_position_analyst'],
            llm=llm_gpt4o_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True
        )

    @agent
    def strategic_insight_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['strategic_insight_analyst'],
            llm=llm_gpt4o_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True
        )

    @agent
    def perstel_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['perstel_analyst'],
            llm=llm_gpt4o_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True
        )

    @agent
    def integrated_analysis_director(self) -> Agent:
        return Agent(
            config=self.agents_config['integrated_analysis_director'],
            llm=llm_gpt4o_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True
        )

    @task
    def analyze_business_model(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        # Pass both internal and external analyses to the task
        task = Task(
            config=self.tasks_config['analyze_business_model'],
            output_file=f'outputs/business_model_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=IntegratedCompanyAnalysis
        )
        # Add the analyses from previous crews to the task input
        task.input = {
            "internal_analysis": self.internal_analysis,
            "external_analysis": self.external_analysis
        }
        return task

    @task
    def analyze_competitive_position(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        task = Task(
            config=self.tasks_config['analyze_competitive_position'],
            output_file=f'outputs/competitive_position_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=IntegratedCompanyAnalysis
        )
        task.input = {
            "internal_analysis": self.internal_analysis,
            "external_analysis": self.external_analysis
        }
        return task

    @task
    def generate_strategic_insights(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        task = Task(
            config=self.tasks_config['generate_strategic_insights'],
            output_file=f'outputs/strategic_insights_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=IntegratedCompanyAnalysis
        )
        task.input = {
            "internal_analysis": self.internal_analysis,
            "external_analysis": self.external_analysis
        }
        return task

    @task
    def conduct_perstel_analysis(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        task = Task(
            config=self.tasks_config['conduct_perstel_analysis'],
            output_file=f'outputs/perstel_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=IntegratedCompanyAnalysis
        )
        task.input = {
            "internal_analysis": self.internal_analysis,
            "external_analysis": self.external_analysis
        }
        return task

    @task
    def create_integrated_analysis(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        task = Task(
            config=self.tasks_config['create_integrated_analysis'],
            output_file=f'outputs/integrated_company_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[
                self.analyze_business_model(),
                self.analyze_competitive_position(),
                self.generate_strategic_insights(),
                self.conduct_perstel_analysis()
            ],
            output_pydantic=IntegratedCompanyAnalysis
        )
        task.input = {
            "internal_analysis": self.internal_analysis,
            "external_analysis": self.external_analysis
        }
        return task

    @crew
    def crew(self) -> Crew:
        """Creates the IntegratedAnalysisCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )

# ===========================
# Main Company Analysis Manager
# ===========================

class CompanyAnalysisManager:
    """Manager for running the complete company analysis process"""
    
    def __init__(self, research_inputs):
        self.research_inputs = research_inputs
        
    def run(self):
        # Track start time
        start_time = datetime.datetime.now()
        print(f"Company Analysis for {self.research_inputs.get('company_name')} started at {start_time}")
        
        # Step 1: Run Internal Analysis Crew
        print("Starting Internal Analysis...")
        internal_crew = InternalAnalysisCrew()
        internal_result = internal_crew.crew().run()
        
        # Step 2: Run External Analysis Crew
        print("Starting External Analysis...")
        external_crew = ExternalAnalysisCrew()
        external_result = external_crew.crew().run()
        
        # Step 3: Run Integrated Analysis Crew with results from both previous crews
        print("Starting Integrated Analysis...")
        integrated_crew = IntegratedAnalysisCrew(
            internal_analysis=internal_result,
            external_analysis=external_result
        )
        integrated_result = integrated_crew.crew().run()
        
        # Track end time and calculate duration
        end_time = datetime.datetime.now()
        duration = end_time - start_time
        
        print(f"Company Analysis completed in {duration}")
        print(f"Results saved to: outputs/integrated_company_analysis_{self.research_inputs.get('company_name')}_{end_time.strftime('%Y%m%d_%H%M%S')}.json")
        
        return integrated_result

# Example usage
if __name__ == "__main__":
    # Configure inputs for the analysis
    research_inputs = {
        "company_name": "Apple Inc",
        "ticker_symbol": "AAPL",
        "industry": "Technology",
        "specialisation": "CompanyAnalysis",
        "time_period": "2021-2023",
        "focus_areas": ["Artificial Intelligence", "Services Revenue", "Supply Chain"],
        "competitor_names": ["Microsoft", "Google", "Samsung", "Amazon"]
    }
    
    # Initialize and run the analysis
    manager = CompanyAnalysisManager(research_inputs)
    result = manager.run()
