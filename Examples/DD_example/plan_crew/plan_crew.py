import os
import datetime
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

# Other imports
from pydantic import BaseModel
from typing import List

# Import variables
from ...config import COMPANY_PROFILES_FLOW_VARIABLES
input_variables = COMPANY_PROFILES_FLOW_VARIABLES
topic = input_variables.get("topic")


# Crewai tools
from crewai_tools import SerperDevTool

# Custom Tools
from ...tools.tavily_search_tool import TavilySearchTool
from ...tools.custom_firecrawl_tool2 import CustomFirecrawlScrapeWebsiteTool

# Define LLMs
llm_gpt4o = LLM(model="chatgpt-4o-latest")
llm_claude = LLM(model="claude-3-5-sonnet-20241022")

# Setup Pydantic Models
class Section(BaseModel):
    subtitle: str
    high_level_goal: str
    why_important: str
    sources: List[str]
    content_outline: List[str]

class CompanyProfilePlan(BaseModel):
    sections: List[Section]


@CrewBase
class PlanCrew():
	"""PlanCrew crew"""

	agents_config = 'config/agents.yaml'
	tasks_config = 'config/tasks.yaml'

	@before_kickoff # Optional hook to be executed before the crew starts
	def pull_data_example(self, inputs):
		# Example of pulling data from an external API, dynamically changing the inputs
		inputs['extra_data'] = "This is extra data"
		return inputs

	@after_kickoff # Optional hook to be executed after the crew has finished
	def log_results(self, output):
		# Example of logging results, dynamically changing the output
		print(f"Results: {output}")
		return output

	@agent
	def researcher(self) -> Agent:
		return Agent(
			config=self.agents_config['researcher'],
			tools=[SerperDevTool()], # Example of custom tool, loaded on the beginning of file
			verbose=True
		)

	@agent
	def planner(self) -> Agent:
		return Agent(
			config=self.agents_config['planner'],
			verbose=True,
			llm=llm_gpt4o # Example of custom LLM, loaded on the beginning of file
		)

	@task
	def research_task(self) -> Task:
		return Task(
			config=self.tasks_config['research_task'],
		)

	@task
	def planning_task(self) -> Task:
		return Task(
			config=self.tasks_config['planning_task'],
			output_file= f'outputs/0.plan_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',     
			output_pydantic=CompanyProfilePlan
		)

	@crew
	def crew(self) -> Crew:
		"""Creates the PlanCrew crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
