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
# litellm._turn_on_debug()

# Import LLMs
from competitor_analysis.llm_config import (
    llm_gpt4o, 
    llm_gpt4o_mini,
    llm_gpt4o_mini_accurate,
    llm_gpt4o_accurate,
    llm_claude_3_7_sonnet,
    llm_claude_3_5_sonnet,
    llm_gemini_2_5_pro,
    llm_gemini_2_0_flash,
    llm_gemini_2_5_flash,
    llm_gpt_4_1_mini,
    llm_gpt_4_1_mini_accurate,
    llm_gpt_4_1_accurate,
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
    SeleniumScrapingTool, 
    RagTool,
    CodeInterpreterTool
)

# Import Custom tools
from tools.file_downloader import FileDownloaderTool
# from tools.custom_yahoo_finance_tool import YFinanceStockTool

# Import Research variables to support naming
from config_competitor_analysis import RESEARCH_INPUTS

# Import Pydantic models
from competitor_analysis.competitor_analysis_models import (
    CompanySourceIdentificationResults,
    CompanyExternalAnalysis,
    NewsMediaAnalysisResult,
    ExternalFinancialAnalysisResult,
    MarketPositionAnalysisResult,
)


# Enable CodeInterpreter - THIS IS RISKY but useful for data analysis
run_code = CodeInterpreterTool(unsafe_mode=True)



# ===========================
# External Analysis Crew
# ===========================

@CrewBase
class ExternalAnalysisCrew():
    """Company External Analysis Crew"""

    research_inputs = RESEARCH_INPUTS
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    # @agent
    # def external_source_identifier(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['external_source_identifier'],
    #         llm=llm_gpt_4_1_mini_accurate,
    #         tools=[BraveSearchTool(), ScrapeWebsiteTool()],
    #         verbose=True,
    #         cache=True,
    #         function_calling_llm=llm_gpt_4_1_mini_accurate
    #     )

    @agent
    def news_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['news_analyst'],
            llm=llm_gpt_4_1_accurate,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code],
            verbose=True,
            respect_context_window=True,
            cache=True,
            function_calling_llm=llm_gemini_2_0_flash
        )

    @agent
    def financial_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_analyst'],
            llm=llm_gpt_4_1_accurate,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code],
            verbose=True,
            respect_context_window=True,
            cache=True,
            function_calling_llm=llm_gemini_2_0_flash
        )

    @agent
    def market_position_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['market_position_analyst'],
            llm=llm_gpt_4_1_accurate,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code],
            verbose=True,
            respect_context_window=True,
            cache=True,
            function_calling_llm=llm_gemini_2_0_flash
        )

    @agent
    def external_analysis_consolidator(self) -> Agent:
        return Agent(
            config=self.agents_config['external_analysis_consolidator'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True
        )

    # @task
    # def identify_company_external_sources(self) -> Task:
    #     company_name = self.research_inputs.get("company_name")
    #     return Task(
    #         config=self.tasks_config['identify_company_external_sources'],
    #         output_file=f'outputs/comp_analysis/external_sources_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
    #         async_execution=False,
    #         output_pydantic=CompanySourceIdentificationResults
    #     )

    @task
    def analyze_news_and_media(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            name="Analyze News and Media",
            config=self.tasks_config['analyze_news_and_media'],
            output_file=f'outputs/comp_analysis/news_media_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            # context=[self.identify_company_external_sources()],
            async_execution=False,
            output_pydantic=NewsMediaAnalysisResult
        )

    @task
    def analyze_external_financials(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            name="Analyze External Financials",
            config=self.tasks_config['analyze_external_financials'],
            output_file=f'outputs/comp_analysis/external_financial_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            # context=[self.identify_company_external_sources()],
            async_execution=False,
            output_pydantic=ExternalFinancialAnalysisResult
        )

    @task
    def analyze_market_position(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            name="Analyze Market Position",
            config=self.tasks_config['analyze_market_position'],
            output_file=f'outputs/comp_analysis/market_position_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            # context=[self.identify_company_external_sources()],
            async_execution=False,
            output_pydantic=MarketPositionAnalysisResult
        )

    @task
    def consolidate_external_analysis(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            name="Consolidate External Analysis",
            config=self.tasks_config['consolidate_external_analysis'],
            output_file=f'outputs/comp_analysis/consolidated_external_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
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
            name="External Analysis Crew",
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )