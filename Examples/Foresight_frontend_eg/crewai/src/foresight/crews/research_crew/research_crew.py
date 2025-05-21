import os
import datetime
import json
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
from crewai_tools import SerperDevTool, ScrapeWebsiteTool, PDFSearchTool, CodeInterpreterTool

# Custom Tools
from ...tools.tavily_search_tool import TavilySearchTool
from ...tools.file_downloader import FileDownloaderTool
from ...tools.custom_serper_news_tool import CustomSerperNewsTool

# Enable CodeInterpreter - THIS IS RISKY but useful for data analysis
run_code = CodeInterpreterTool(unsafe_mode=True)

# Import LLMs from the config file
from ...llm_config import llm_gemini_2_5_pro, llm_gpt4o, llm_gpt4o_mini

# Enable Research content to be saved to a database
class SectionOutput(BaseModel):
    subtitle: str
    content: str
    stage: str  # "research", "analysis", "insight", "exponential", "written", "edited", or "reviewed"
    timestamp: str

@CrewBase
class ResearchCrew():
    """ResearchCrew for executing foresight research"""

    input_variables = FLOW_VARIABLES

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @before_kickoff
    def setup(self, inputs):
        print(f"Starting foresight research for sector: {sector}")
        
        # Check if section data exists
        if 'section' not in inputs:
            print("WARNING: No section data found in inputs!")
            return inputs
            
        try:
            # Get the section data
            section = inputs['section']
            
            print(f"Section data type: {type(section)}")
            
            # Now extract the variables needed by the templates
            if isinstance(section, dict):
                # Extract all known fields directly into inputs
                inputs['section_number'] = section.get('section_number', 0)
                inputs['subtitle'] = section.get('subtitle', 'Unknown Section')
                inputs['high_level_goal'] = section.get('high_level_goal', 'No goal specified')
                inputs['why_important'] = section.get('why_important', 'Importance not specified')
                inputs['sources'] = section.get('sources', [])
                inputs['content_outline'] = section.get('content_outline', [])
                inputs['evaluation_criteria'] = section.get('evaluation_criteria', '')
                
                # Also extract any other fields that might be in the section
                for key, value in section.items():
                    if key not in ['section_number', 'subtitle', 'high_level_goal', 
                                  'why_important', 'sources', 'content_outline', 
                                  'evaluation_criteria']:
                        inputs[key] = value
                
                print(f"Processing section {section.get('section_number', 0)}: {section.get('subtitle', 'unknown')}")
            elif isinstance(section, str):
                # If it's a JSON string, try to parse it
                try:
                    section_dict = json.loads(section)
                    # Extract all known fields
                    inputs['section_number'] = section_dict.get('section_number', 0)
                    inputs['subtitle'] = section_dict.get('subtitle', 'Unknown Section')
                    inputs['high_level_goal'] = section_dict.get('high_level_goal', 'No goal specified')
                    inputs['why_important'] = section_dict.get('why_important', 'Importance not specified')
                    inputs['sources'] = section_dict.get('sources', [])
                    inputs['content_outline'] = section_dict.get('content_outline', [])
                    inputs['evaluation_criteria'] = section_dict.get('evaluation_criteria', '')
                    
                    # Also extract any other fields
                    for key, value in section_dict.items():
                        if key not in ['section_number', 'subtitle', 'high_level_goal', 
                                      'why_important', 'sources', 'content_outline', 
                                      'evaluation_criteria']:
                            inputs[key] = value
                    
                    print(f"Processed section {section_dict.get('section_number', 0)}: {section_dict.get('subtitle', 'unknown')}")
                except json.JSONDecodeError:
                    print("WARNING: Section is a string but not valid JSON!")
                    inputs['section_number'] = 0
                    inputs['subtitle'] = 'Error: Invalid section data'
                    inputs['high_level_goal'] = 'No goal specified'
                    inputs['why_important'] = 'Importance not specified'
                    inputs['sources'] = []
                    inputs['content_outline'] = []
                    inputs['evaluation_criteria'] = ''
            else:
                print(f"WARNING: Section is not a dictionary or JSON string! Type: {type(section)}")
                inputs['section_number'] = 0
                inputs['subtitle'] = 'Error: Invalid section data type'
                inputs['high_level_goal'] = 'No goal specified'
                inputs['why_important'] = 'Importance not specified'
                inputs['sources'] = []
                inputs['content_outline'] = []
                inputs['evaluation_criteria'] = ''
                
            # Keep the original section data too for backward compatibility
            inputs['section_data'] = section
                
        except Exception as e:
            print(f"ERROR in setup: {e}")
            # Set default values if there's an error
            inputs['section_number'] = 0
            inputs['subtitle'] = 'Error Processing Section'
            inputs['high_level_goal'] = 'Unknown'
            inputs['why_important'] = 'Unknown'
            inputs['sources'] = []
            inputs['content_outline'] = ['Error occurred while processing section data']
            inputs['evaluation_criteria'] = ''
            
        return inputs

    @after_kickoff
    def log_results(self, output):
        section_num = self.input_variables.get('section_number', 'unknown')
        subtitle = self.input_variables.get('subtitle', 'unknown')
        print(f"Completed foresight research task for section {section_num}: {subtitle}")
        return output

    @agent
    def Researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['Researcher'],
            tools=[
                # SerperDevTool(),
                # ScrapeWebsiteTool(),
                # FileDownloaderTool(),
                # PDFSearchTool(),
            ],
            # llm=llm_gpto3_mini, #expensive
            llm=llm_gpt4o_mini,
            verbose=True,
            respect_context_window=True
        )

    @agent
    def content_writer(self) -> Agent:
        return Agent(
            config=self.agents_config['content_writer'],
            # tools=[SerperDevTool()],
            verbose=True,
            # llm=llm_claude_3_7_sonnet, #expensive
            llm=llm_gpt4o_mini,
            respect_context_window=True
        )

    @agent
    def content_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['content_editor'],
            # tools=[SerperDevTool()],
            verbose=True,
            # llm=llm_gpt4o_mini,
            llm=llm_gpt4o_mini,
            respect_context_window=True
        )

    @agent
    def quality_reviewer(self) -> Agent:
        return Agent(
            config=self.agents_config['quality_reviewer'],
            # tools=[SerperDevTool()],
            verbose=True,
            # llm=llm_gpt4o_mini,
            llm=llm_gpt4o_mini,
            respect_context_window=True
        )

    @task
    def trend_research_task(self) -> Task:
        sector = self.input_variables.get("sector")
        section_num = self.input_variables.get("section_number", 0)
        subtitle = self.input_variables.get("subtitle", "unknown")
        # Create filename with sanitized subtitle and section number
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"2.{section_num}_analysis_{subtitle.replace(' ', '_')}_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['trend_research_task'],
            output_file=output_file_path
        )

    @task
    def content_writing_task(self) -> Task:
        sector = self.input_variables.get("sector")
        section_num = self.input_variables.get("section_number", 0)
        subtitle = self.input_variables.get("subtitle", "unknown")
        # Create filename with sanitized subtitle and section number
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"5.{section_num}_content_{subtitle.replace(' ', '_')}_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['content_writing_task'],
            output_file=output_file_path
        )

    @task
    def content_editing_task(self) -> Task:
        sector = self.input_variables.get("sector")
        section_num = self.input_variables.get("section_number", 0)
        subtitle = self.input_variables.get("subtitle", "unknown")
        # Create filename with sanitized subtitle and section number
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"6.{section_num}_edited_{subtitle.replace(' ', '_')}_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['content_editing_task'],
            output_file=output_file_path
        )

    @task
    def quality_review_task(self) -> Task:
        sector = self.input_variables.get("sector")
        section_num = self.input_variables.get("section_number", 0)
        subtitle = self.input_variables.get("subtitle", "unknown")
        # Create filename with sanitized subtitle and section number
        timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"7.{section_num}_final_{subtitle.replace(' ', '_')}_{timestamp}.md"
        output_file_path = os.path.join('outputs', file_name)

        return Task(
            config=self.tasks_config['quality_review_task'],
            output_file=output_file_path
        )

    @crew
    def crew(self) -> Crew:
        """Creates the ResearchCrew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
