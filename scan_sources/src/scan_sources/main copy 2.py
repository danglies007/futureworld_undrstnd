import os
import json
import sys
import warnings
import traceback
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()
                
from pydantic import BaseModel
from crewai.flow import Flow, start, listen
from scan_sources.crews.source_identification_crew.source_identification_crew import SourceIdentificationCrew
from scan_sources.crews.market_force_extraction_crew.market_force_extraction_crew import MarketForceExtractionCrew
from scan_sources.crews.reporting_crew.reporting_crew import ReportingCrew
from scan_sources.crews.formatting_crew.formatting_crew import FormattingCrew
from scan_sources.config import SOURCES_FUTURISTS
from scan_sources.models import (
    SourceIdentificationResultsURLonly, SourceURL,
    ResearchOutput, ExtractorOutput, MarketForceReport,
)

class ScanState(BaseModel):
    research_context: dict = None
    source_results: SourceIdentificationResultsURLonly = None
    extraction_results: ResearchOutput = None
    report: MarketForceReport = None
    markdown_report: str = None

class ScanFlow(Flow[ScanState]):
    @start()
    def identify_sources(self) -> SourceIdentificationResultsURLonly:
        research_inputs = {
            'topic': 'Generative AI in Financial Services',
            'specialisation': 'Futurist & Foresight',
            'research_sources': SOURCES_FUTURISTS,
            'minimum_number_of_sources': 5,
            'minimum_number_of_forces': 3,
            'specific_points_of_interest': [],
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        # Crew is configured to output SourceIdentificationResultsURLonly
        sources_result = SourceIdentificationCrew().crew().kickoff(inputs=research_inputs).pydantic
        return final_result

    @listen(identify_sources)
    def identify_market_forces(self, sources_result):
        research_inputs = {
            'topic': 'Generative AI in Financial Services',
            'specialisation': 'Futurist & Foresight',
            'research_sources': SOURCES_FUTURISTS,
            'minimum_number_of_sources': 5,
            'minimum_number_of_forces': 3,
            'specific_points_of_interest': [],
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        # url_list = [src.url for src in sources.sources]
        # prep inputs for market force extraction crew
        forces_inputs = research_inputs.copy()
        forces_inputs['sources'] = sources_result.sources
        forces_result = MarketForceExtractionCrew().crew().kickoff(forces_inputs).pydantic
        # if not isinstance(result, ResearchOutput):
        #     raise TypeError(f"Expected ResearchOutput, got {type(result)}: {result}")
        # result = forces_result.pydantic_object

        # self.state.extraction_results = result
        return forces_result

    @listen(identify_market_forces)
    def develop_report(self, forces_result):
        report_inputs = {**self.state.research_context, 'market_forces': forces_result.market_forces}
        result = ReportingCrew().crew().kickoff(inputs=report_inputs)
        # if not isinstance(result, MarketForceReport):
        #     raise TypeError(f"Expected MarketForceReport, got {type(result)}: {result}")
        self.state.report = result
        return result

    @listen(develop_report)
    def format_report(self, report: MarketForceReport) -> str:
        format_inputs = {**self.state.research_context, 'report': report.model_dump()}
        result = FormattingCrew().crew().kickoff(inputs=format_inputs)
        if not isinstance(result, str):
            # If the formatting crew returns an object with a 'raw' attribute, use it
            if hasattr(result, 'raw'):
                result = result.raw
            else:
                raise TypeError(f"Expected str or object with 'raw', got {type(result)}: {result}")
        self.state.markdown_report = result
        print("Final Markdown Report:\n")
        print(result)
        return result

def kickoff():
    scan_flow = ScanFlow()
    scan_flow.kickoff()

def plot():
    scan_flow = ScanFlow()
    scan_flow.plot()

if __name__ == "__main__":
    kickoff()
