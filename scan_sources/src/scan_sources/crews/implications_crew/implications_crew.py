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
	ResearchOutput,
    ImplicationAnalysisReport,
    Implication,
    FirstOrderImplication,
    SecondOrderImplication,
    ThirdOrderImplication,
    
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
)

# Import Custom tools
from scan_sources.tools.file_downloader import FileDownloaderTool
from scan_sources.tools.exa_search_tool import Exa_search_tool
from scan_sources.tools.exa_crawl_tool import Exa_crawl_scrape_tool
from scan_sources.tools.custom_web_scrape_market_forces import MarketForcesScrapeWebsiteTool

# firecrawl_crawl_tool = FirecrawlCrawlWebsiteTool(api_key=os.getenv("FIRECRAWL_API_KEY"))
# firecrawl_search_tool = FirecrawlSearchTool(api_key=os.getenv("FIRECRAWL_API_KEY"))
# firecrawl_scrape_tool = FirecrawlScrapeWebsiteTool(api_key=os.getenv("FIRECRAWL_API_KEY"))

# Import Research variables to support naming
from scan_sources.config import RESEARCH_INPUTS

@CrewBase
class ImplicationsCrew():
    """ImplicationsCrew for generating 2nd and 3rd order implications"""

    research_inputs = RESEARCH_INPUTS

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def first_order_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['first_order_analyst'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True,
        )

    @agent
    def second_order_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['second_order_analyst'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True,
        )

    @agent
    def third_order_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['third_order_analyst'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True,
        )

    @agent
    def implications_integrator(self) -> Agent:
        return Agent(
            config=self.agents_config['implications_integrator'],
            llm=llm_gpt_4_1_accurate,
            verbose=True,
            respect_context_window=True,
            cache=True,
        )

    @task
    def analyse_first_order_implications(self) -> Task:
        specialisation = self.research_inputs.get("specialisation")
        topic_short = self.research_inputs.get("topic_short")
        business = self.research_inputs.get("business", "general")
        return Task(
            config=self.tasks_config['analyse_first_order_implications'],
            output_file=f'outputs/first_order_implications_{specialisation}_{topic_short}_{business}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            output_pydantic=FirstOrderImplication
        )

    @task
    def analyse_second_order_implications(self) -> Task:
        specialisation = self.research_inputs.get("specialisation")
        topic_short = self.research_inputs.get("topic_short")
        business = self.research_inputs.get("business", "general")
        return Task(
            config=self.tasks_config['analyse_second_order_implications'],
            output_file=f'outputs/second_order_implications_{specialisation}_{topic_short}_{business}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[self.analyse_first_order_implications()],
            output_pydantic=SecondOrderImplication
        )

    @task
    def analyse_third_order_implications(self) -> Task:
        specialisation = self.research_inputs.get("specialisation")
        topic_short = self.research_inputs.get("topic_short")
        business = self.research_inputs.get("business", "general")
        return Task(
            config=self.tasks_config['analyse_third_order_implications'],
            output_file=f'outputs/third_order_implications_{specialisation}_{topic_short}_{business}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[self.analyse_second_order_implications()],
            output_pydantic=ThirdOrderImplication
        )

    @task
    def integrate_all_implications(self) -> Task:
        specialisation = self.research_inputs.get("specialisation")
        topic_short = self.research_inputs.get("topic_short")
        business = self.research_inputs.get("business", "general")
        return Task(
            config=self.tasks_config['integrate_all_implications'],
            output_file=f'outputs/implications_analysis_report_{specialisation}_{topic_short}_{business}_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
            context=[
                self.analyse_first_order_implications(),
                self.analyse_second_order_implications(),
                self.analyse_third_order_implications()
            ],
            output_pydantic=ImplicationAnalysisReport
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ImplicationsCrew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
