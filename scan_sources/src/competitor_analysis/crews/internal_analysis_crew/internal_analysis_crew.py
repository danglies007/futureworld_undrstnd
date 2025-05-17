from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
load_dotenv()

# Agentops
import agentops
agentops.init()

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
    llm_gpt_4_1_mini_accurate_0,
    llm_gpt_4_1_accurate,
    llm_gpt_4_1
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
    CodeInterpreterTool,
    RagTool
)

# Import Custom tools
from tools.file_downloader import FileDownloaderTool


# Import Research variables to support naming
from config_competitor_analysis import RESEARCH_INPUTS

# Import Pydantic models
from competitor_analysis.competitor_analysis_models import (
    CompanySourceIdentificationResults,
    CompanyInternalAnalysis,
    AnnualReportAnalysisResult,
    FinancialAnalysisResult,
    StrategyAnalysisResult,
)

# Enable CodeInterpreter - THIS IS RISKY but useful for data analysis
run_code = CodeInterpreterTool(unsafe_mode=True)


# ===========================
# Internal Analysis Crew
# ===========================

@CrewBase
class InternalAnalysisCrew():
    """Company Internal Analysis Crew"""

    research_inputs = RESEARCH_INPUTS
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    # @agent
    # def company_source_identifier(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['company_source_identifier'],
    #         llm=llm_gpt_4_1_accurate,
    #         tools=[SerperDevTool(), ScrapeWebsiteTool()],
    #         verbose=True,
    #         cache=True,
    #         function_calling_llm=llm_gpt_4_1_accurate
    #     )

    @agent
    def annual_report_analyzer(self) -> Agent:
        return Agent(
            config=self.agents_config['annual_report_analyzer'],
            llm=llm_gpt_4_1_accurate,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code],
            verbose=True,
            respect_context_window=True,
            cache=True,
            max_iter=25,
            function_calling_llm=llm_gemini_2_0_flash
        )

    @agent
    def financial_statement_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['financial_statement_analyst'],
            llm=llm_gpt_4_1_accurate,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code],
            verbose=True,
            respect_context_window=True,
            cache=True,
            max_iter=25,
            function_calling_llm=llm_gemini_2_0_flash
        )

    @agent
    def strategy_document_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['strategy_document_analyst'],
            llm=llm_gpt_4_1_accurate,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code],
            verbose=True,
            respect_context_window=True,
            cache=True,
            max_iter=25,
            function_calling_llm=llm_gemini_2_0_flash
        )

    @agent
    def internal_analysis_consolidator(self) -> Agent:
        return Agent(
            config=self.agents_config['internal_analysis_consolidator'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True
        )

    # @task
    # def identify_company_internal_sources(self) -> Task:
    #     company_name = self.research_inputs.get("company_name")
    #     return Task(
    #         config=self.tasks_config['identify_company_internal_sources'],
    #         output_file=f'outputs/comp_analysis/internal_sources_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
    #         async_execution=False,
    #         output_pydantic=CompanySourceIdentificationResults
    #     )

    @task
    def analyze_annual_reports(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['analyze_annual_reports'],
            output_file=f'outputs/comp_analysis/annual_report_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            # context=[self.identify_company_internal_sources()],
            async_execution=False,
            output_pydantic=AnnualReportAnalysisResult
        )

    @task
    def analyze_financial_statements(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['analyze_financial_statements'],
            output_file=f'outputs/comp_analysis/financial_statement_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            # context=[self.identify_company_internal_sources()],
            async_execution=False,
            output_pydantic=FinancialAnalysisResult
        )

    @task
    def analyze_strategy_documents(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['analyze_strategy_documents'],
            output_file=f'outputs/comp_analysis/strategy_document_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            # context=[self.identify_company_internal_sources()],
            async_execution=False,
            output_pydantic=StrategyAnalysisResult
        )

    @task
    def consolidate_internal_analysis(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['consolidate_internal_analysis'],
            output_file=f'outputs/comp_analysis/consolidated_internal_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[
                self.analyze_annual_reports(),
                self.analyze_financial_statements(),
                self.analyze_strategy_documents()
            ],
            output_pydantic=CompanyInternalAnalysis
        )

    # def manager(self) -> Agent:
    #     return Agent(
    #         config=self.agents_config['manager'],
    #         llm=llm_gpt_4_1,
    #         verbose=True,
    #         respect_context_window=True,
    #         cache=True
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the InternalAnalysisCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            # process=Process.hierarchical,
            verbose=True,
            # manager_agent=self.manager(),
            planning=True
        )
