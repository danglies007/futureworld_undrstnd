"""Defines the Research Crew for conducting research and generating findings."""

import os
import datetime
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew

# Import Tools
from crewai_tools import SerperDevTool, WebsiteSearchTool, FileReadTool
# from crewai_tools import ScraperTool, DirectoryReadTool, BrowserbaseLoadTool # Optional/Alternative tools

# Import custom tools
from scan_sources.tools.custom_pdf_tool_3 import CustomPDFSearchTool3

# Import Pydantic models
from scan_sources.utilities.models import (
    ResearchPlan, SourceFinding, IdentifiedForce
)

# Load environment variables
load_dotenv()

# Define a base directory for outputs relative to the project root
output_base_dir = Path("outputs")
output_base_dir.mkdir(exist_ok=True)

# Use GPT-4o mini for cost-effective operations
llm_gpt4o_mini = LLM(model="gpt-4o-mini-2024-07-18")  # Fast and cheap $0.15/$0.60


@CrewBase
class ResearchCrew:
    """Research crew for conducting research and generating findings."""
    # Config paths relative to this file
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # Perform any setup here if needed
        pass

    # ------------------ Agent Definitions ------------------ #
    @agent
    def WebSourceAnalyst(self) -> Agent:
        return Agent(
            config=self.agents_config['WebSourceAnalyst'],
            tools=[SerperDevTool(), WebsiteSearchTool()],
            llm=llm_gpt4o_mini,
            verbose=True
        )

    @agent
    def DocumentSourceAnalyst(self) -> Agent:
        return Agent(
            config=self.agents_config['DocumentSourceAnalyst'],
            tools=[CustomPDFSearchTool3(), FileReadTool()],
            llm=llm_gpt4o_mini,
            verbose=True
        )

    @agent
    def DataSynthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['DataSynthesizer'],
            memory=True,
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
    def scan_web_sources(self) -> Task:
        return Task(
            config=self.tasks_config['scan_web_sources'],
            async_execution=True,
            output_pydantic=SourceFinding
        )

    @task
    def scan_document_sources(self) -> Task:
        return Task(
            config=self.tasks_config['scan_document_sources'],
            async_execution=True,
            output_pydantic=SourceFinding,
        )

    @task
    def synthesize_findings(self) -> Task:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"synthesize_findings_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['synthesize_findings'],
            context=[self.scan_web_sources(), self.scan_document_sources()],
            output_pydantic=IdentifiedForce,
            output_file=output_file_path
        )

    @task
    def review_preliminary_findings(self) -> Task:
        return Task(
            config=self.tasks_config['review_preliminary_findings'],
            context=[self.synthesize_findings()],
            human_input=True,
            output_pydantic=IdentifiedForce
        )

    # ------------------ Crew Definition ------------------ #
    @crew
    def crew(self) -> Crew:
        """Creates the Research crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            verbose=True,
            # manager=self.agents['ResearchManager']
        )
