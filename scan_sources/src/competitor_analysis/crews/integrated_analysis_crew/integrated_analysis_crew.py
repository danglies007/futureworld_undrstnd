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
    CodeInterpreterTool,
    RagTool
)

# Import Custom tools
from tools.file_downloader import FileDownloaderTool

# Import Research variables to support naming
from config_competitor_analysis import RESEARCH_INPUTS

# Import Pydantic models
from competitor_analysis.competitor_analysis_models import (
    CompanyIntegratedAnalysis,
    BusinessModelAnalysis,
    CompetitivePositionAnalysis,
    StrategicInsightsAnalysis,
    PERSTELAnalysis,
)

# Enable CodeInterpreter - THIS IS RISKY but useful for data analysis
run_code = CodeInterpreterTool(unsafe_mode=True)



# ===========================
# Integrated Analysis Crew
# ===========================

@CrewBase
class IntegratedAnalysisCrew():
    """Company Integrated Analysis Crew"""

    research_inputs = RESEARCH_INPUTS
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    # # Input from previous crews
    # internal_analysis = None
    # external_analysis = None
    
    # def __init__(self, internal_analysis, external_analysis):
    #     self.internal_analysis = internal_analysis
    #     self.external_analysis = external_analysis
    #     super().__init__()
    
    @agent
    def business_model_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['business_model_analyst'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            function_calling_llm=llm_gemini_2_0_flash,
            cache=True,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code]
        )

    @agent
    def competitive_position_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['competitive_position_analyst'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            function_calling_llm=llm_gemini_2_0_flash,
            cache=True,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code]
        )

    @agent
    def strategic_insight_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['strategic_insight_analyst'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            function_calling_llm=llm_gemini_2_0_flash,
            cache=True,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code]
        )

    @agent
    def perstel_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['perstel_analyst'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            function_calling_llm=llm_gemini_2_0_flash,
            cache=True,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code]
        )

    @agent
    def integrated_analysis_director(self) -> Agent:
        return Agent(
            config=self.agents_config['integrated_analysis_director'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            function_calling_llm=llm_gemini_2_0_flash,
            cache=True,
            tools=[BraveSearchTool(), ScrapeWebsiteTool(), FileDownloaderTool(), RagTool(), run_code]
        )

    @task
    def analyze_business_model(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        # Pass both internal and external analyses to the task
        task = Task(
            name="Analyze Business Model",
            config=self.tasks_config['analyze_business_model'],
            output_file=f'outputs/comp_analysis/business_model_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=BusinessModelAnalysis
        )
        # # Add the analyses from previous crews to the task input
        # task.input = {
        #     "internal_analysis": self.internal_analysis,
        #     "external_analysis": self.external_analysis
        # }
        return task

    @task
    def analyze_competitive_position(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        task = Task(
            name="Analyze Competitive Position",
            config=self.tasks_config['analyze_competitive_position'],
            output_file=f'outputs/comp_analysis/competitive_position_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=CompetitivePositionAnalysis
        )
        # task.input = {
        #     "internal_analysis": self.internal_analysis,
        #     "external_analysis": self.external_analysis
        # }
        return task

    @task
    def generate_strategic_insights(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        task = Task(
            name="Generate Strategic Insights",
            config=self.tasks_config['generate_strategic_insights'],
            output_file=f'outputs/comp_analysis/strategic_insights_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=StrategicInsightsAnalysis
        )
        # task.input = {
        #     "internal_analysis": self.internal_analysis,
        #     "external_analysis": self.external_analysis
        # }
        return task

    @task
    def conduct_perstel_analysis(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        task = Task(
            name="Conduct PERSTEL Analysis",
            config=self.tasks_config['conduct_perstel_analysis'],
            output_file=f'outputs/comp_analysis/perstel_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            async_execution=False,
            output_pydantic=PERSTELAnalysis
        )
        # task.input = {
        #     "internal_analysis": self.internal_analysis,
        #     "external_analysis": self.external_analysis
        # }
        return task

    @task
    def create_integrated_analysis(self) -> Task:
        company_name = self.research_inputs.get("company_name")
        task = Task(
            name="Create Integrated Analysis",
            config=self.tasks_config['create_integrated_analysis'],
            output_file=f'outputs/comp_analysis/integrated_company_analysis_{company_name}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[
                self.analyze_business_model(),
                self.analyze_competitive_position(),
                self.generate_strategic_insights(),
                self.conduct_perstel_analysis()
            ],
            output_pydantic=CompanyIntegratedAnalysis
        )
        # task.input = {
        #     "internal_analysis": self.internal_analysis,
        #     "external_analysis": self.external_analysis
        # }
        return task

    @crew
    def crew(self) -> Crew:
        """Creates the IntegratedAnalysisCrew"""
        return Crew(
            name="IntegratedAnalysisCrew",
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
