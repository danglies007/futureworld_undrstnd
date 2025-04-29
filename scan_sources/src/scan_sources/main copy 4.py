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
    RawMarketForce, SourceIdentificationResultsURLonly, SourceURL,
    ResearchOutput, ExtractorOutput, MarketForceReport,
)

class ScanState(BaseModel):
    research_context: dict = None
    source_results: SourceIdentificationResultsURLonly = None
    extraction_results: ResearchOutput = None
    report: MarketForceReport = None
    markdown_report: str = None

class ScanFlow(Flow[ScanState]):
    research_inputs = {
        'topic': 'Generative AI in Financial Services',
        'specialisation': 'Futurist & Foresight',
        'research_sources': SOURCES_FUTURISTS,
        'minimum_number_of_sources': 3,
        'minimum_number_of_forces': 3,
        'specific_points_of_interest': [],
        'date': datetime.now().strftime('%Y-%m-%d')
    }
    
    @start()
    # generate the list of URLs to Search
    # def identify_sources(self) -> SourceIdentificationResultsURLonly:
    def identify_sources(self):
        self.state.research_context = self.research_inputs
        # Crew is configured to output SourceIdentificationResultsURLonly
        sources_result = SourceIdentificationCrew().crew().kickoff(self.research_inputs).pydantic
        # if not isinstance(result, SourceIdentificationResultsURLonly):
        #     raise TypeError(f"Expected SourceIdentificationResultsURLonly, got {type(result)}: {result}")
        self.state.source_results = sources_result
        return sources_result

    @listen(identify_sources)
    def identify_market_forces(self, sources_result):
        self.state.research_context = self.research_inputs
        final_content = []
        for url in sources_result.urls:
            # forces_inputs = self.state.research_context.copy()
            forces_inputs = self.research_inputs.copy()
            forces_inputs['url'] = url.model_dump_json()
            forces_result = MarketForceExtractionCrew().crew().kickoff(forces_inputs).pydantic
            final_content.append(forces_result)
        self.state.extraction_results = final_content
        # print("Extraction Results:", self.state.extraction_results) # this provides a full view of all of the analysis 
        print(final_content) # this also provides a full view of all of the analysis 
        return final_content

    # @listen(identify_sources)
    # def identify_market_forces(self, sources_result) -> ResearchOutput:
    #     self.state.research_context = self.research_inputs
    #     # Prep forces inputs
    #     forces_inputs = self.state.research_context.copy()
    #     forces_inputs['urls'] = sources_result.urls
        
    #     forces_result = MarketForceExtractionCrew().crew().kickoff(forces_inputs).pydantic
    #     # if not isinstance(result, ResearchOutput):
    #     #     raise TypeError(f"Expected ResearchOutput, got {type(result)}: {result}")
    #     self.state.extraction_results = forces_result
    #     return forces_result


    # @listen(identify_market_forces)
    # def develop_report(self, extraction_results: ResearchOutput) -> MarketForceReport:
    #     report_inputs = {**self.state.research_context, 'market_forces': extraction_results.raw_market_forces}
    #     reporting_result = ReportingCrew().crew().kickoff(inputs=report_inputs).pydantic
    #     # if not isinstance(result, MarketForceReport):
    #     #     raise TypeError(f"Expected MarketForceReport, got {type(result)}: {result}")
    #     self.state.report = reporting_result
    #     return reporting_result

    # @listen(develop_report)
    # def format_report(self, report: MarketForceReport) -> str:
    #     format_inputs = {**self.state.research_context, 'report': report.model_dump()}
    #     formatting_result = FormattingCrew().crew().kickoff(inputs=format_inputs).raw
    #     if not isinstance(formatting_result, str):
    #         # If the formatting crew returns an object with a 'raw' attribute, use it
    #         if hasattr(formatting_result, 'raw'):
    #             formatting_result = formatting_result.raw
    #         else:
    #             raise TypeError(f"Expected str or object with 'raw', got {type(result)}: {result}")
    #     self.state.markdown_report = formatting_result
    #     print("Final Markdown Report:\n")
    #     print(formatting_result)
    #     return formatting_result

def kickoff():
    scan_flow = ScanFlow()
    scan_flow.kickoff()

def plot():
    scan_flow = ScanFlow()
    scan_flow.plot()

if __name__ == "__main__":
    kickoff()
