from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from dotenv import load_dotenv
load_dotenv()

# Custom Perplexity patch - using crew_perplexity.py
from scan_sources.crew_perplexity import PerplexityLLM  # Import our custom LLM
# Custom Perplexity patch - using litellm_patch.py

# Ignore warnings
import warnings
from crewai_tools.tools.firecrawl_crawl_website_tool.firecrawl_crawl_website_tool import FirecrawlCrawlWebsiteToolSchema
from pydantic import PydanticDeprecatedSince20

# Suppress specific pydantic deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

# File management imports
import os
import datetime

# Debugging imports
import litellm
litellm._turn_on_debug()

# Pydantic and model imports
from pydantic import BaseModel
from typing import List

# Import Pydantic models - Used to generate Market Force research and report
from scan_sources.models import (
    SourceDiscoveryResults,
    SourceEvaluationResults,
    SourceApprovedResults,
    PotentialSourcesURLOnly,
    PotentialSources,
    EvaluatedSources,
    NotApprovedSources,
    ApprovedSources,
    SourceIdentificationResults
)

# Import LLMs
from scan_sources.llm_config import (
	llm_gpt4o, 
	llm_gpt4o_mini,
	llm_gpt4o_mini_accurate,
	llm_gpt4o_accurate,
    llm_claude_3_7_sonnet,
	llm_perplexity_via_openai,
	llm_perplexity_custom_patch,
	llm_gemini_2_5_pro,
	llm_gemini_2_0_flash,
	llm_gemini_2_5_flash,
	llm_gpt_4_1_mini,
    llm_gpt_4_1_accurate,
    llm_gpt_4_1_mini_accurate,
    llm_gpt_4_1
)
llm_perplexity_custom_crew_patch = PerplexityLLM()

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
    CodeInterpreterTool,
    SeleniumScrapingTool
)

# Import Custom tools
from scan_sources.tools.file_downloader import FileDownloaderTool
from scan_sources.tools.exa_search_tool import Exa_search_tool
from scan_sources.tools.exa_crawl_tool import Exa_crawl_scrape_tool
from scan_sources.tools.custom_web_scrape_market_forces import MarketForcesScrapeWebsiteTool
from scan_sources.tools.url_counter_tools import URLCounterTool
# from scan_sources.tools.enhanced_selenium_scraper import EnhancedSeleniumScrapeTool

# firecrawl_crawl_tool = FirecrawlCrawlWebsiteTool(api_key=os.getenv("FIRECRAWL_API_KEY"))
# firecrawl_search_tool = FirecrawlSearchTool(api_key=os.getenv("FIRECRAWL_API_KEY"))
# firecrawl_scrape_tool = FirecrawlScrapeWebsiteTool(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Import Research variables to support naming
from scan_sources.config import RESEARCH_INPUTS

# Enable CodeInterpreter - THIS IS RISKY but useful for data analysis
run_code = CodeInterpreterTool(unsafe_mode=True)

@CrewBase
class SourceIdentificationCrew():
    """SourceIdentificationCrew crew"""

    research_inputs = RESEARCH_INPUTS

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def source_scout(self) -> Agent:
        return Agent(
            config=self.agents_config['source_scout'],
            llm=llm_gpt_4_1_accurate,
            tools=[SerperDevTool()],
            respect_context_window=True,
            cache=True,
            max_iter=50,
            verbose=True
        )
    
    @agent
    def source_evaluator(self) -> Agent:
        """
        Seems to work with SeleniumScrapingTool, but serperdev did not work well
        """
        return Agent(
            config=self.agents_config['source_evaluator'],
            llm=llm_gpt_4_1_mini_accurate,
            tools=[run_code, SeleniumScrapingTool()],
            respect_context_window=True,
            cache=True,
            max_iter=50,
            max_retry_limit=50,
            verbose=True
        )

    @agent
    def source_classifier(self) -> Agent:
        return Agent(
            config=self.agents_config['source_classifier'],
            llm=llm_gpt_4_1_mini_accurate,
            tools=[URLCounterTool(), run_code],
            respect_context_window=True,
            cache=True,
            delegate=True,
            max_iter=50,
            max_retry_limit=50,
            verbose=True
        )

    @agent
    def metadata_extractor(self) -> Agent:
        return Agent(
            config=self.agents_config['metadata_extractor'],
            llm=llm_gpt_4_1_accurate,
            tools=[SeleniumScrapingTool(), run_code],
            respect_context_window=True,
            cache=True,
            max_iter=50,
            max_retry_limit=50,
            verbose=True
        )    

    @task
    def source_discovery(self) -> Task:
        specialisation = self.research_inputs.get("specialisation")
        topic_short = self.research_inputs.get("topic_short")
        return Task(
            config=self.tasks_config['source_discovery'],
            output_file=f'outputs/potential_sources_{specialisation}_{topic_short}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            output_pydantic=PotentialSourcesURLOnly   
        )

    @task
    def source_evaluation(self) -> Task:
        specialisation = self.research_inputs.get("specialisation")
        topic_short = self.research_inputs.get("topic_short")
        return Task(
            config=self.tasks_config['source_evaluation'],
            context=[self.source_discovery()],
            output_file=f'outputs/evaluated_sources_{specialisation}_{topic_short}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            output_pydantic=EvaluatedSources
        )

    # @task
    # def not_approved_sources_classification(self) -> Task:
    #     specialisation = self.research_inputs.get("specialisation")
    #     topic_short = self.research_inputs.get("topic_short")
    #     return Task(
    #         config=self.tasks_config['not_approved_sources_classification'],
    #         context=[self.source_evaluation()],
    #         async_execution=True,
    #         output_file=f'outputs/not_approved_sources_{specialisation}_{topic_short}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
    #         output_pydantic=NotApprovedSources
    #     )

    # @task
    # def approved_sources_classification(self) -> Task:
    #     specialisation = self.research_inputs.get("specialisation")
    #     topic_short = self.research_inputs.get("topic_short")
    #     return Task(
    #         config=self.tasks_config['approved_sources_classification'],
    #         context=[self.source_evaluation()],
    #         async_execution=True,
    #         output_file=f'outputs/approved_sources_{specialisation}_{topic_short}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
    #         output_pydantic=ApprovedSources
    #     )

    @task
    def metadata_extraction(self) -> Task:
        specialisation = self.research_inputs.get("specialisation")
        topic_short = self.research_inputs.get("topic_short")
        return Task(
            config=self.tasks_config['metadata_extraction'],
            context=[self.source_evaluation()],
            output_file=f'outputs/final_sources_{specialisation}_{topic_short}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            output_pydantic=SourceIdentificationResults
        )

    # Old from the previous crew with a single agent & Task
    # @task
    # def source_identification(self) -> Task:
    #     specialisation = self.research_inputs.get("specialisation")
    #     topic_short = self.research_inputs.get("topic_short")
    #     return Task(
    #         config=self.tasks_config['source_identification'],
    #         output_file=f'outputs/sources_{specialisation}_{topic_short}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
    #         output_pydantic=SourceIdentificationResults
    #     )

    @crew
    def crew(self) -> Crew:
        """Creates the SourceIdentificationCrew crew"""

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
