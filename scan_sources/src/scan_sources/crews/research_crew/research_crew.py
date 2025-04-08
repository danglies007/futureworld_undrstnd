"""Defines the Research Crew for conducting research and generating findings."""

import os
import datetime
import json
from pathlib import Path
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process, LLM
from crewai.project import CrewBase, agent, task, crew, before_kickoff, after_kickoff

# Suppress the Pydantic warnings
import warnings
from pydantic import PydanticDeprecatedSince211

# Suppress the specific Pydantic warning
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince211)


# Import Tools
from crewai_tools import SerperDevTool, WebsiteSearchTool, FileReadTool, PDFSearchTool, FileWriterTool
# from crewai_tools import ScraperTool, DirectoryReadTool, BrowserbaseLoadTool # Optional/Alternative tools

# Import custom tools
from scan_sources.tools.custom_pdf_tool_3 import CustomPDFSearchTool3

# Import Pydantic models
from scan_sources.utilities.models import (
    ResearchPlan, ResearchItem, SourceFinding, IdentifiedForce
)

# Load environment variables
load_dotenv()

# Define a base directory for outputs relative to the project root
output_base_dir = Path("outputs")
output_base_dir.mkdir(exist_ok=True)

# Use GPT-4o mini for cost-effective operations
llm_gpt4o_mini = LLM(model="gpt-4o-mini-2024-07-18")  # Fast and cheap $0.15/$0.60
llm_gpt4o = LLM(model="gpt-4o-2024-11-20") # Fast intelligent $2.50/$10


@CrewBase
class ResearchCrew:
    """Research crew for conducting research and generating findings."""
    # Config paths relative to this file
    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    def __init__(self):
        # Perform any setup here if needed
        self.all_web_findings = []
        self.all_document_findings = []
        self.all_synthesized_forces = []

    @before_kickoff
    def setup(self, inputs):
        """Prepare inputs for the research crew execution."""
        print(f"Starting research crew execution")
        
        # Check if validated_plan exists in inputs
        if 'validated_plan' not in inputs:
            print("WARNING: No validated plan found in inputs!")
            return inputs
            
        try:
            # Get the validated plan data
            validated_plan = inputs['validated_plan']
            
            # Convert to dictionary if it's not already
            if not isinstance(validated_plan, dict):
                try:
                    validated_plan = json.loads(validated_plan) if isinstance(validated_plan, str) else validated_plan.model_dump()
                except (json.JSONDecodeError, AttributeError):
                    print(f"Warning: Failed to convert validated_plan to dict: {validated_plan}")
            
            # Extract research items from the plan
            research_items = validated_plan.get('research_items', [])
            
            if not research_items:
                print("WARNING: No research items found in validated plan!")
                return inputs
            
            # Store the full list of research items
            inputs['all_research_items'] = research_items
            
            # If current_item_index is not set, initialize it to 0
            if 'current_item_index' not in inputs:
                inputs['current_item_index'] = 0
            
            # Get the current research item to process
            current_index = inputs['current_item_index']
            if current_index < len(research_items):
                current_item = research_items[current_index]
                inputs['current_research_item'] = current_item
                print(f"Processing research item {current_index + 1}/{len(research_items)}: {current_item.get('topic', 'Unknown')}")
            else:
                print(f"All research items have been processed.")
                inputs['current_research_item'] = None
                
            # Store previous findings if they exist
            if 'all_web_findings' in inputs:
                self.all_web_findings = inputs['all_web_findings']
            if 'all_document_findings' in inputs:
                self.all_document_findings = inputs['all_document_findings']
                
            # Create output directories for this run
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            self.output_dir = output_base_dir / f"research_run_{timestamp}"
            self.output_dir.mkdir(exist_ok=True)
            
            # Create output paths for each task
            self.web_findings_path = self.output_dir / "web_findings.json"
            self.doc_findings_path = self.output_dir / "doc_findings.json"
            self.synthesized_forces_path = self.output_dir / "synthesized_forces.json"
            self.final_forces_path = self.output_dir / "final_forces.json"
            
            # Add output paths to inputs
            inputs['web_findings_path'] = str(self.web_findings_path)
            inputs['doc_findings_path'] = str(self.doc_findings_path)
            inputs['synthesized_forces_path'] = str(self.synthesized_forces_path)
            inputs['final_forces_path'] = str(self.final_forces_path)
            
            # Add web and document findings to inputs
            inputs['web_findings'] = self.all_web_findings
            inputs['doc_findings'] = self.all_document_findings
            
        except Exception as e:
            print(f"Error in setup: {e}")
            
        return inputs

    @after_kickoff
    def process_results(self, result):
        """Process the results of the research crew execution."""
        print(f"Completed research crew execution")
        
        # Initialize the output dictionary
        output = {}
        
        try:
            # Process the result based on the source type
            if 'source_type' in self.inputs:
                source_type = self.inputs['source_type']
                
                if source_type == 'web':
                    # Extract web findings
                    if isinstance(result, dict) and 'web_findings' in result:
                        web_findings = result['web_findings']
                        self.all_web_findings.extend(web_findings)
                        print(f"Added {len(web_findings)} web findings to all_web_findings (total: {len(self.all_web_findings)})")
                        
                        # Save web findings to file
                        with open(self.web_findings_path, 'w') as f:
                            json.dump(self.all_web_findings, f, indent=2)
                            
                        # Add to output
                        output['web_findings'] = web_findings
                        output['all_web_findings'] = self.all_web_findings
                        
                elif source_type == 'document':
                    # Extract document findings
                    if isinstance(result, dict) and 'document_findings' in result:
                        doc_findings = result['document_findings']
                        self.all_document_findings.extend(doc_findings)
                        print(f"Added {len(doc_findings)} document findings to all_document_findings (total: {len(self.all_document_findings)})")
                        
                        # Save document findings to file
                        with open(self.doc_findings_path, 'w') as f:
                            json.dump(self.all_document_findings, f, indent=2)
                            
                        # Add to output
                        output['document_findings'] = doc_findings
                        output['all_document_findings'] = self.all_document_findings
            else:
                # Handle synthesis and review results
                if isinstance(result, dict):
                    # Extract synthesized forces
                    if 'synthesized_forces' in result:
                        synthesized_forces = result['synthesized_forces']
                        self.all_synthesized_forces = synthesized_forces
                        print(f"Processed {len(synthesized_forces)} synthesized forces")
                        
                        # Save synthesized forces to file
                        with open(self.synthesized_forces_path, 'w') as f:
                            json.dump(synthesized_forces, f, indent=2)
                            
                        # Add to output
                        output['synthesized_forces'] = synthesized_forces
                        
                    # Extract final forces
                    if 'final_forces' in result:
                        final_forces = result['final_forces']
                        print(f"Processed {len(final_forces)} final forces")
                        
                        # Save final forces to file
                        with open(self.final_forces_path, 'w') as f:
                            json.dump(final_forces, f, indent=2)
                            
                        # Add to output
                        output['final_forces'] = final_forces
                
        except Exception as e:
            print(f"Error processing results: {e}")
            
        return output

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
            tools=[PDFSearchTool(), FileReadTool()],
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
            llm=llm_gpt4o,
            verbose=True
        )

    # ------------------ Task Definitions ------------------ #
    @task
    def scan_web_sources(self) -> Task:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"web_findings_{timestamp}.json"
        output_file_path = os.path.join('outputs', file_name)
        
        return Task(
            config=self.tasks_config['scan_web_sources'],
            async_execution=False,
            output_pydantic=SourceFinding,
            output_file=output_file_path
        )

    @task
    def scan_document_sources(self) -> Task:
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"document_findings_{timestamp}.json"
        output_file_path = os.path.join('outputs', file_name)
        
        return Task(
            config=self.tasks_config['scan_document_sources'],
            async_execution=False,
            output_pydantic=SourceFinding,
            output_file=output_file_path
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
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"reviewed_findings_{timestamp}.json"
        output_file_path = os.path.join('outputs', file_name)
        
        return Task(
            config=self.tasks_config['review_preliminary_findings'],
            context=[self.synthesize_findings()],
            human_input=True,
            output_pydantic=IdentifiedForce,
            output_file=output_file_path
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
