"""Defines the Market Forces Scanning Crew using CrewAI components."""

import os
import datetime 
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew # Using CrewBase for structure

# Import Tools
from crewai_tools import SerperDevTool, WebsiteSearchTool, FileReadTool
# from crewai_tools import ScraperTool, DirectoryReadTool, BrowserbaseLoadTool # Optional/Alternative tools

# Change relative imports to absolute imports
from scan_sources.tools.custom_pdf_tool_3 import CustomPDFSearchTool3


# Change relative imports to absolute imports
from scan_sources.utilities.models import (
    ResearchPlan, SourceFinding, IdentifiedForce, MarketForceOutput
)

# Load environment variables
load_dotenv()

# Define a base directory for outputs relative to the project root (assuming main.py is there)
# Adjust path if main.py location is different
output_base_dir = Path("outputs")
output_base_dir.mkdir(exist_ok=True)

llm_gpt4o_mini = LLM(model="gpt-4o-mini-2024-07-18") # Fast and cheap $0.15/$0.60


@CrewBase
class ScanSourcesCrew:
    """ScanSources crew for identifying market forces and trends."""
    # Adjust config paths to be relative to this file (scanner_crew.py)
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

    @agent
    def WebSourceAnalyst(self) -> Agent:
        return Agent(
            config=self.agents_config['WebSourceAnalyst'],
            # tools=[SerperDevTool()], # Example: Assign dynamic tools if needed
            llm=llm_gpt4o_mini,
            verbose=True
        )

    @agent
    def DocumentSourceAnalyst(self) -> Agent:
        return Agent(
            config=self.agents_config['DocumentSourceAnalyst'],
            tools=[CustomPDFSearchTool3()], # Pass the property
            llm=llm_gpt4o_mini,
            verbose=True
        )

    @agent
    def DataSynthesizer(self) -> Agent:
        return Agent(
            config=self.agents_config['DataSynthesizer'],
            memory=True, # Ensure memory is enabled as per config
            llm=llm_gpt4o_mini,
            verbose=True
        )

    @agent
    def ReportWriter(self) -> Agent:
        return Agent(
            config=self.agents_config['ReportWriter'],
            memory=True, # Ensure memory enabled as per config
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

    @task
    def scan_web_sources(self) -> Task:
        return Task(
            config=self.tasks_config['scan_web_sources'],
            context=[self.review_research_plan()],
            async_execution=True,
            output_pydantic=SourceFinding
        )

    @task
    def scan_document_sources(self) -> Task:
        return Task(
            config=self.tasks_config['scan_document_sources'],
            context=[self.review_research_plan()],
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

    @task
    def generate_outputs(self) -> Task:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"generate_outputs_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['generate_outputs'],
            context=[self.review_preliminary_findings()],
            output_pydantic=MarketForceOutput,
            output_file=output_file_path
        )

    # ------------------ Crew Definition ------------------ #
    @crew
    def crew(self) -> Crew:
        """Creates the Scan Sources crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True, # Enable memory for the crew
            verbose=True
        )
