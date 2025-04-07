"""Defines the Packaging Crew for formatting and presenting outputs."""

import os
import datetime
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew

# Import Pydantic models
from scan_sources.utilities.models import (
    IdentifiedForce, MarketForceOutput
)

# Load environment variables
load_dotenv()

# Define a base directory for outputs relative to the project root
output_base_dir = Path("outputs")
output_base_dir.mkdir(exist_ok=True)

# Use GPT-4o mini for cost-effective operations
llm_gpt4o_mini = LLM(model="gpt-4o-mini-2024-07-18")  # Fast and cheap $0.15/$0.60


@CrewBase
class PackagingCrew:
    """Packaging crew for formatting and presenting outputs."""
    # Config paths relative to this file
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # Perform any setup here if needed
        pass

    # ------------------ Agent Definitions ------------------ #
    @agent
    def ReportWriter(self) -> Agent:
        return Agent(
            config=self.agents_config['ReportWriter'],
            memory=True,
            llm=llm_gpt4o_mini,
            verbose=True
        )
        
    @agent
    def TableFormatter(self) -> Agent:
        return Agent(
            config=self.agents_config['TableFormatter'],
            memory=True,
            llm=llm_gpt4o_mini,
            verbose=True
        )

    # ------------------ Task Definitions ------------------ #
    @task
    def generate_markdown_report(self) -> Task:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"markdown_report_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['generate_markdown_report'],
            output_file=output_file_path
        )

    @task
    def generate_markdown_table(self) -> Task:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"markdown_table_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['generate_markdown_table'],
            output_file=output_file_path
        )
        
    @task
    def package_outputs(self) -> Task:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"package_outputs_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['package_outputs'],
            context=[self.generate_markdown_report(), self.generate_markdown_table()],
            output_pydantic=MarketForceOutput,
            output_file=output_file_path
        )

    # ------------------ Crew Definition ------------------ #
    @crew
    def crew(self) -> Crew:
        """Creates the Packaging crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            verbose=True
        )
