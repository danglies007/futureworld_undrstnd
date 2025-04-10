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

# Import Pydantic models
from scan_sources.models import (
    Research_Strategy,
    Market_Force_Plan,
    InternetResearch,
    NewsAnalysis,
    PatentResearch, 
    ConsultingInsights,
    FutureTrends,
    DocumentAnalysis,
    ResearchSynthesis
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
	def internet_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['internet_researcher'],
			llm=llm_gpt4o_mini,
			tools=[SerperDevTool(), FileDownloaderTool()],
			verbose=True
		)

	@agent
	def general_news_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['general_news_researcher'],
			llm=llm_gpt4o_mini,
			tools=[SerperDevTool(), FileDownloaderTool()],
			verbose=True
		)

	@agent
	def patent_filings_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['patent_filings_researcher'],
			llm=llm_gpt4o_mini,
			tools=[SerperDevTool(), FileDownloaderTool()],
			verbose=True
		)

	@agent
	def specialist_consultant_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['specialist_consultant_researcher'],
			llm=llm_gpt4o_mini,
			tools=[SerperDevTool(), FileDownloaderTool()],
			verbose=True
		)

	@agent
	def specialist_trend_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['specialist_trend_researcher'],
			llm=llm_gpt4o_mini,
			tools=[SerperDevTool(), FileDownloaderTool()],
			verbose=True
		)

	@agent
	def document_researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['document_researcher'],
			llm=llm_gpt4o_mini,
			tools=[SerperDevTool(), FileDownloaderTool(), PDFSearchTool()],
			verbose=True
		)

	@agent
	def quality_assurance_reviewer(self) -> Agent:
		return Agent(
			config=self.agents_config['quality_assurance_reviewer'],
			llm=llm_gpt4o_mini,
			tools=[SerperDevTool(), FileDownloaderTool()],
			verbose=True
		)

	@agent
	def research_synthesizer(self) -> Agent:
		return Agent(
			config=self.agents_config['research_synthesizer'],
			llm=llm_gpt4o_mini,
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def conduct_internet_research(self) -> Task:
		return Task(
			config=self.tasks_config['conduct_internet_research'],
			output_file=f'outputs/internet_research_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
			output_pydantic=InternetResearch
		)

	# @task
	# def analyze_news_coverage(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['analyze_news_coverage'],
	# 		output_file=f'outputs/news_analysis_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
	# 		output_pydantic=NewsAnalysis
	# 	)

	# @task
	# def research_patent_filings(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['research_patent_filings'],
	# 		output_file=f'outputs/patent_research_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
	# 		output_pydantic=PatentResearch
	# 	)

	# @task
	# def analyze_consulting_insights(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['analyze_consulting_insights'],
	# 		output_file=f'outputs/consulting_insights_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
	# 		output_pydantic=ConsultingInsights
	# 	)

	# @task
	# def research_future_trends(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['research_future_trends'],
	# 		output_file=f'outputs/future_trends_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
	# 		output_pydantic=FutureTrends
	# 	)

	# @task
	# def analyze_documents(self) -> Task:
	# 	return Task(
	# 		config=self.tasks_config['analyze_documents'],
	# 		output_file=f'outputs/document_analysis_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
	# 		output_pydantic=DocumentAnalysis
	# 	)

	@task
	def quality_check_research(self) -> Task:
		return Task(
			config=self.tasks_config['quality_check_research'],
			output_file=f'outputs/quality_check_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
		)

	@task
	def synthesize_research_findings(self) -> Task:
		return Task(
			config=self.tasks_config['synthesize_research_findings'],
			output_file=f'outputs/research_synthesis_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',
			output_pydantic=ResearchSynthesis
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
