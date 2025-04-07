"""Defines the Requirements Crew for understanding and presenting requirements to the user."""

import os
import datetime
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew

# Import Pydantic models
from scan_sources.utilities.models import (
    MarketForceInput, SourceConfig, ResearchPlan
)

# Load environment variables
load_dotenv()

# Define a base directory for outputs relative to the project root
output_base_dir = Path("outputs")
output_base_dir.mkdir(exist_ok=True)

# Use GPT-4o mini for cost-effective operations
llm_gpt4o_mini = LLM(model="gpt-4o-mini-2024-07-18")  # Fast and cheap $0.15/$0.60


@CrewBase
class RequirementsCrew:
    """Requirements crew for understanding and presenting requirements to the user."""
    # Config paths relative to this file
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # Perform any setup here if needed
        pass

    # ------------------ Agent Definitions ------------------ #
    @agent
    def ConfigurationSpecialist(self) -> Agent:
        return Agent(
            config=self.agents_config['ConfigurationSpecialist'],
            llm=llm_gpt4o_mini,
            verbose=True
        )

    @agent
    def ResearchManager(self) -> Agent:
        return Agent(
            config=self.agents_config['ResearchManager'],
            llm=llm_gpt4o_mini,
            verbose=True
        )

    # ------------------ Task Definitions ------------------ #
    @task
    def prepare_research_plan(self) -> Task:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"prep_research_plan_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['prepare_research_plan'],
            output_pydantic=ResearchPlan,
            output_file=output_file_path
        )

    @task
    def review_research_plan(self) -> Task:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"review_research_plan_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['review_research_plan'],
            context=[self.prepare_research_plan()],
            human_input=True,
            output_pydantic=ResearchPlan,
            output_file=output_file_path
        )

    # ------------------ Crew Definition ------------------ #
    @crew
    def crew(self) -> Crew:
        """Creates the Requirements crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )
