import os
import datetime
import json
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff

# Other imports
from pydantic import BaseModel
from typing import List

# Import variables
from ...config import COMPANY_PROFILES_FLOW_VARIABLES
input_variables = COMPANY_PROFILES_FLOW_VARIABLES
topic = input_variables.get("topic")

# Tracking
# from langtrace_python_sdk import langtrace # Must precede any llm module imports
# langtrace.init(api_key = os.environ.get("LANGTRACE_API_KEY"), session_id=topic)

# langchain tools
# from langchain_community.tools import DuckDuckGoSearchRun

# Crewai tools
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, PDFSearchTool, CodeInterpreterTool

# Custom Tools
from ...tools.tavily_search_tool import TavilySearchTool
from ...tools.file_downloader import FileDownloaderTool
from ...tools.custom_serper_news_tool import CustomSerperNewsTool


# Enable CodeInterpreter - THIS IS RISKY
run_code=CodeInterpreterTool(unsafe_mode=True)

# Define LLMs
llm_gpt4o = LLM(model="chatgpt-4o-latest")
llm_accurate = LLM(model="chatgpt-4o-latest",temperature=0.1, max_completion_tokens=8000, max_tokens=8000)
llm_mini_accurate = LLM(model="gpt-4o-mini",temperature=0.1, max_completion_tokens=8000, max_tokens=8000)
llm_mini_editor = LLM(model="gpt-4o-mini",temperature=0.1, max_completion_tokens=8000, max_tokens=8000)
llm_claude = LLM(model="claude-3-5-sonnet-20241022")
llm_claude_accurate = LLM(model="claude-3-5-sonnet-20241022",temperature=0.1,max_completion_tokens=8000, max_tokens=8000)
llm_claude_editor = LLM(model="claude-3-5-sonnet-20241022",temperature=0.5,max_completion_tokens=8000, max_tokens=8000)
llm_claude_mini_accurate = LLM(model="claude-3-5-haiku-20241022",temperature=0.1,max_completion_tokens=8000, max_tokens=8000)

#Enable Research content to be saved to a database
class SectionOutput(BaseModel):
    subtitle: str
    content: str
    stage: str  # "raw", "edited", or "reviewed"
    timestamp: str

@CrewBase
class ResearchCrew():
	"""ResearchCrew crew"""
	input_variables = COMPANY_PROFILES_FLOW_VARIABLES

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
	def content_writer(self) -> Agent:
		return Agent(
			config=self.agents_config['content_writer'],
			tools=[
				CustomSerperNewsTool(),
				SerperDevTool(),
				ScrapeWebsiteTool(),
				FileDownloaderTool(),
				PDFSearchTool(),
			], # Example of custom tool, loaded on the beginning of file
			llm=llm_mini_accurate, # was llm_mini_accurate
			verbose=True,
			respect_context_window= True
		)

	@agent
	def editor(self) -> Agent:
		return Agent(
			config=self.agents_config['editor'],
			tools=[run_code,TavilySearchTool()], # Example of custom tool, loaded on the beginning of file
			verbose=True,
			# allow_code_execution=True,
			llm=llm_claude_editor, # was llm_claude_accurate
			respect_context_window= True
		)

	@agent
	def quality_reviewer(self) -> Agent:
		return Agent(
			config=self.agents_config['quality_reviewer'],
			tools=[SerperDevTool(),run_code,TavilySearchTool()], # Example of custom tool, loaded on the beginning of file
			verbose=True,
			llm=llm_claude_mini_accurate, # was llm_mini_accurate
			respect_context_window= True
		)

	@task
	def writing_task(self) -> Task:
		topic = self.input_variables.get("topic")
		audience_level = self.input_variables.get("audience_level")
		company_short = self.input_variables.get("company_short")
		file_name = f"1.{company_short}_{topic}_report_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md".replace(" ", "_")
		# file_name = f"1.writeup.md".replace(" ", "_")
		output_file_path = os.path.join('outputs', file_name)

        # # Validate input length
		# input_data = f"{topic} {audience_level} {company_short}"
		# self.validate_input_length(input_data, max_token_limit=32000)

		return Task(
			config=self.tasks_config['writing_task'],
			output_file=output_file_path
		)

	@task
	def editing_task(self) -> Task:
		topic = self.input_variables.get("topic")
		company_short = self.input_variables.get("company_short")
		file_name = f"2.{company_short}_{topic}_edited_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md".replace(" ", "_")
		output_file_path = os.path.join('outputs', file_name)
		
		return Task(
			config=self.tasks_config['editing_task'],
			output_file=output_file_path
		)


	@task
	def quality_review_task(self) -> Task:
		topic = self.input_variables.get("topic")
		company_short = self.input_variables.get("company_short")
		file_name = f"3.{company_short}_{topic}_quality_review_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md".replace(" ", "_")
		# file_name = f"1.quality.md".replace(" ", "_")
		output_file_path = os.path.join('outputs', file_name)

		return Task(
			config=self.tasks_config['quality_review_task'],
			output_file=output_file_path
		)
	
	@crew
	def crew(self) -> Crew:
		"""Creates the ResearchCrew crew"""
		return Crew(
			agents=self.agents, # Automatically created by the @agent decorator
			tasks=self.tasks, # Automatically created by the @task decorator
			process=Process.sequential,
			# memory=True,
			verbose=True,
			# process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
		)
