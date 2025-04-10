from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task


# Ignore warnings
import warnings
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

# Pydantic and model imports
from pydantic import BaseModel
from typing import List

# Import User Inputs from config.py
from scan_sources.config import (
	USER_INPUT_VARIABLES,
	SOURCES_CONSULTING_FIRMS,
	SOURCES_FUTURISTS,
	SOURCES_NEWS_SOURCES,
	SOURCES_GOV_NON_PROFIT,
	SOURCES_PATENTS
)

# Import Pydantic models - old models used by old crew
# from scan_sources.models import (
#     Research_Strategy,
#     Market_Force_Plan,
#     InternetResearch,
#     NewsAnalysis,
#     PatentResearch, 
#     ConsultingInsights,
#     FutureTrends,
#     DocumentAnalysis,
#     ResearchSynthesis
# )

# Import Pydantic models - Used to generate Market Force research and report
from scan_sources.models import (
    RawMarketForce,
	ResearchOutput,
	MarketForceReportSection,
	MarketForceReport,
)

# Import LLMs
from scan_sources.llm_config import (
	llm_gpt4o, 
	llm_gpt4o_mini
)

# Import CrewAI tools
from crewai_tools import SerperDevTool, PDFSearchTool

# Import Custom tools
from scan_sources.tools.file_downloader import FileDownloaderTool

@CrewBase
class ResearchCrew():
	"""ResearchCrew crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def futurist_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['futurist_researcher'],
			llm=llm_gpt4o_mini,
			tools=[SerperDevTool(), FileDownloaderTool()],
			verbose=True
		)

	@agent
	def reporting_analyst(self) -> Agent:
		return Agent(
			config=self.agents_config['reporting_analyst'],
			llm=llm_gpt4o_mini,
			verbose=True
		)

	@agent
	def formatter(self) -> Agent:
		return Agent(
			config=self.agents_config['formatter'],
			llm=llm_gpt4o_mini,
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task

	@task
	def futurist_research(self) -> Task:
		return Task(
			config=self.tasks_config['futurist_research'],
			output_file=f'outputs/futurist_research_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
			output_pydantic=ResearchOutput
		)

	@task
	def reporting_task(self) -> Task:
		return Task(
			config=self.tasks_config['reporting_task'],
			output_file=f'outputs/futurist_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.json',
			output_pydantic=MarketForceReport
		)

	@task
	def formatting_task(self) -> Task:
		return Task(
			config=self.tasks_config['formatting_task'],
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
