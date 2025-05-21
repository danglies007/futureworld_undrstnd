import os
import datetime
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff, after_kickoff
import litellm

# Other imports
from pydantic import BaseModel
from typing import List

# Import variables from config.py
from ...config import FLOW_VARIABLES
input_variables = FLOW_VARIABLES
sector = input_variables.get("sector")

# Crewai tools
from crewai_tools import SerperDevTool

# Custom Tools
from ...tools.tavily_search_tool import TavilySearchTool
from ...tools.custom_firecrawl_tool2 import CustomFirecrawlScrapeWebsiteTool

# Import LLMs from the config file
from ...llm_config import llm_gemini_2_5_pro, llm_gpt4o, llm_gpt4o_mini

# Setup Pydantic Models
class Section(BaseModel):
    section_number: int
    subtitle: str
    high_level_goal: str
    why_important: str
    sources: List[str]
    content_outline: List[str]

class Plan(BaseModel):
    sections: List[Section]


@CrewBase
class PlanCrew():
    """PlanCrew for planning foresight research"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @before_kickoff # Optional hook to be executed before the crew starts
    def setup_variables(self, inputs):
        # You can add any pre-processing of inputs here
        print(f"Setting up variables for foresight planning: {sector}")
        return inputs

    @after_kickoff # Optional hook to be executed after the crew has finished
    def log_results(self, output):
        # Check if pydantic model is available
        if hasattr(output, 'pydantic') and output.pydantic is not None:
            print(f"Foresight plan created with {len(output.pydantic.sections)} sections")
            
            # Number the sections if they aren't already numbered
            if output.pydantic and hasattr(output.pydantic, 'sections'):
                for i, section in enumerate(output.pydantic.sections, 1):
                    if not hasattr(section, 'section_number') or not section.section_number:
                        section.section_number = i
        else:
            print("Foresight plan created successfully")
        return output

    @agent
    def research_strategist(self) -> Agent:
        return Agent(
            config=self.agents_config['research_strategist'],
            tools=[SerperDevTool()],
            verbose=True,
            llm=llm_gpt4o_mini

        )

    @agent
    def content_planner(self) -> Agent:
        return Agent(
            config=self.agents_config['content_planner'],
            tools=[SerperDevTool()],
            verbose=True,
            llm=llm_gpt4o_mini
        )

    @task
    def research_strategy_task(self) -> Task:
        return Task(
            config=self.tasks_config['research_strategy_task'],
            output_file=f'outputs/strategy_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        )

    @task
    def content_planning_task(self) -> Task:
        return Task(
            config=self.tasks_config['content_planning_task'],
            output_file=f'outputs/plan_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.md',     
            output_pydantic=Plan
        )

    @crew
    def crew(self) -> Crew:
        """Creates the PlanCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
