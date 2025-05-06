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

# If you want to run a snippet of code before or after the crew starts, 
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

# File management imports
import os
import datetime

# Debugging imports
import litellm
litellm._turn_on_debug()

# Pydantic and model imports
from pydantic import BaseModel
from typing import List

# # Import User Inputs from config.py
# from scan_sources.config import (
# 	USER_INPUT_VARIABLES,
# 	SOURCES_CONSULTING_FIRMS,
# 	SOURCES_FUTURISTS,
# 	SOURCES_NEWS_SOURCES,
# 	SOURCES_GOV_NON_PROFIT,
# 	SOURCES_PATENTS
# )

# Import Pydantic models - Used to generate Market Force research and report
from scan_sources.models import (
    ListStructuredMarketForce,
    RawMarketForce,
	ResearchOutput,
	MarketForceReportSection,
	MarketForceReport,
    SourceIdentificationResults,
    SourceLink,
	StructuredMarketForce,
	ListStructuredMarketForce,
	SourceIdentificationResultsURLonly
)

# Import LLMs
from scan_sources.llm_config import (
	llm_gpt4o, 
	llm_gpt4o_mini,
	llm_gpt4o_mini_accurate,
	llm_gpt4o_accurate,
	llm_perplexity_via_openai,
	llm_perplexity_custom_patch,
	llm_gemini_2_5_pro,
	llm_gemini_2_0_flash,
	llm_gemini_2_5_flash,
	llm_gpt_4_1_mini
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

@CrewBase
class FuturistResearchCrew():
	"""Futurist ResearchCrew crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# --- ADD __init__ to store topic and analysis LLM config ---
	# def __init__(self, topic: str):
	# 	self.topic = "Generative AI in Financial Services"
	# 	self.analysis_llm = llm_gemini_2_5_flash # Choose LLM for the tool's internal use
	# # --- End of __init__ ---

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def futurist_source_identifier(self) -> Agent:
		return Agent(
			config=self.agents_config['futurist_source_identifier'],
			llm=llm_gemini_2_5_flash,
			tools=[SerperDevTool()],
			verbose=True
		)

	@agent
	def futurist_content_extractor(self) -> Agent:
		# --- Instantiate the custom tool HERE, inside the agent method ---
		scrape_market_forces_tool = MarketForcesScrapeWebsiteTool(
			llm=llm_gemini_2_5_flash, # Pass the chosen LLM config from __init__
			topic="Generative AI in Financial Services"      # Pass the research topic from __init__
		)
		# --- End of tool instantiation ---
		return Agent(
			config=self.agents_config['futurist_content_extractor'],
			llm=llm_gemini_2_5_flash,
			tools=[scrape_market_forces_tool, FileDownloaderTool(), PDFSearchTool()],
			verbose=True,
			respect_context_window=True,
			cache=True,
			function_calling_llm=llm_gemini_2_5_flash,
			max_retry_limit=3
		)

	@agent
	def futurist_reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['futurist_reporting_analyst'],
			llm=llm_gemini_2_5_flash,
			tools=[ScrapeWebsiteTool()],
			verbose=True
		)

	@agent
	def futurist_formatter(self) -> Agent:
		return Agent(
			config=self.agents_config['futurist_formatter'],
			llm=llm_gemini_2_5_flash,
			verbose=True
		)

	@agent
	def futurist_market_force_extractor(self) -> Agent:
		return Agent(
			config=self.agents_config['futurist_market_force_extractor'],
			llm=llm_gpt4o_mini,
			verbose=True
		)


	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task

	@task
	def futurist_source_identification(self) -> Task:
		return Task(
			config=self.tasks_config['futurist_source_identification'],
			output_file=f'outputs/futurist_source_identification_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
			output_pydantic=SourceIdentificationResultsURLonly
		)

	@task
	def futurist_market_force_extraction(self) -> Task:
		return Task(
			config=self.tasks_config['futurist_market_force_extraction'],
			output_file=f'outputs/futurist_market_force_extraction_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
			context=[self.futurist_source_identification()],
			output_pydantic=ResearchOutput
		)

	@task
	def futurist_structure_market_forces(self) -> Task:
		return Task(
			config=self.tasks_config['futurist_structure_market_forces'],
			output_file=f'outputs/futurist_structured_market_forces_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
			# context=[self.futurist_market_force_extraction()],
			output_pydantic=ListStructuredMarketForce
		)

	@task
	def futurist_reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['futurist_reporting_task'],
			output_file=f'outputs/futurist_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
			# context=[self.futurist_structure_market_forces(), self.futurist_source_identification()],
			output_pydantic=MarketForceReport
		)

	@task
	def futurist_formatting_task(self) -> Task:
		return Task(
			config=self.tasks_config['futurist_formatting_task'],
			output_file=f'outputs/research_synthesis_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the ResearchCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
