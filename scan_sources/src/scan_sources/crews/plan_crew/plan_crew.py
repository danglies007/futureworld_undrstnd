from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task

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
from scan_sources.config import USER_INPUT_VARIABLES

# Import Pydantic models
from scan_sources.models import (
	Research_Strategy,
	Market_Force_Plan
)

# Import sources from config.py
from scan_sources.config import (
	SOURCES_CONSULTING_FIRMS, 
	SOURCES_FUTURISTS, 
	SOURCES_NEWS_SOURCES, 
	SOURCES_GOV_NON_PROFIT, 
	SOURCES_PATENTS
)

# Import LLMs
from scan_sources.llm_config import (
	llm_gpt4o, 
	llm_gpt4o_mini
)

# Import CrewAI tools
from crewai_tools import SerperDevTool

# Import Custom tools
from scan_sources.tools.file_downloader import FileDownloaderTool

@CrewBase
class PlanCrew():
	"""PlanCrew crew"""

	# Learn more about YAML configuration files here:
	# Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
	# Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	# If you would like to add tools to your agents, you can learn more about it here:
	# https://docs.crewai.com/concepts/agents#agent-tools
	@agent
	def interpreter_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['interpreter_agent'],
			tools=[SerperDevTool()],
			llm=llm_gpt4o_mini,
			verbose=True
		)

	@agent
	def planning_agent(self) -> Agent:
		return Agent(
			config=self.agents_config['planning_agent'],
			tools=[],
			llm=llm_gpt4o,
			verbose=True
		)

	# To learn more about structured task outputs, 
	# task dependencies, and task callbacks, check out the documentation:
	# https://docs.crewai.com/concepts/tasks#overview-of-a-task
	@task
	def interpret_research_requirements(self) -> Task:
		return Task(
			config=self.tasks_config['interpret_research_requirements'],
            output_file=f'outputs/research_strategy_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',     
			output_pydantic=Research_Strategy
		)

	@task
	def create_research_plan(self) -> Task:
		return Task(
			config=self.tasks_config['create_research_plan'],
			# context=["interpret_research_requirements"],
            output_file=f'outputs/plan_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',     
			output_pydantic=Market_Force_Plan
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the PlanCrew crew"""
		# To learn how to add knowledge sources to your crew, check out the documentation:
		# https://docs.crewai.com/concepts/knowledge#what-is-knowledge

		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)