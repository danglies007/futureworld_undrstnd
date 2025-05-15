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
    CodeInterpreterTool
)

# Import Custom tools
from tools.file_downloader import FileDownloaderTool
from tools.custom_serper_dev_tool import (
    CompanyInternalSearchTool,
    CompanyFinancialDocumentTool,
    CompanyAnnualReportTool,
    CompanyESGReportTool
)

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
# Formatting Crew
# ===========================

@CrewBase
class FormattingCrew():
    """FormattingCrew crew"""

    research_inputs = RESEARCH_INPUTS

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def markdown_formatter(self) -> Agent:
        return Agent(
            config=self.agents_config['markdown_formatter'],
            llm=llm_gpt_4_1,
            respect_context_window=True,
            tools=[run_code],
            cache=True,
            verbose=True
        )

    @task
    def markdown_formatting_task(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        return Task(
            config=self.tasks_config['markdown_formatting_task'],
            output_file=f'outputs/comp_analysis/markdown_report_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
        )


    @crew
    def crew(self) -> Crew:
        """Creates the FormattingCrew crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
