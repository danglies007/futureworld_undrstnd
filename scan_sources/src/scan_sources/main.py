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
from crewai.flow import Flow, start, router,listen, and_, or_
from scan_sources.crews.source_identification_crew.source_identification_crew import SourceIdentificationCrew
from scan_sources.crews.market_force_extraction_crew.market_force_extraction_crew import MarketForceExtractionCrew
from scan_sources.crews.reporting_crew.reporting_crew import ReportingCrew
from scan_sources.crews.formatting_crew.formatting_crew import FormattingCrew
from scan_sources.config import SOURCES_FUTURISTS, MARKET_FORCE_DEFINITIONS
from scan_sources.models import (
    MarketForceAnalysisReport, RawMarketForce, SourceIdentificationResultsURLonly, SourceURL,
    ResearchOutput, ExtractorOutput, MarketForceReport, SourceIdentificationResults
)

class ScanState(BaseModel):
    research_context: dict = None
    source_results: SourceIdentificationResults = None
    extraction_results: ResearchOutput = None
    report: MarketForceAnalysisReport = None
    markdown_report: str = None
    markdown_report_from_saved: str = None
    saved_research_context: dict = None
    saved_report: MarketForceAnalysisReport = None

class ScanFlow(Flow[ScanState]):
    
    research_inputs = {
        'specialisation': 'Futurist & Foresight',
        'topic': 'Generative AI',
        'market': 'Financial Services',
        'business': '',
        'audience': 'Expert',
        'specific_points_of_interest': [],
        'research_sources': SOURCES_FUTURISTS,
        'minimum_number_of_sources': 20,
        'maximum_number_of_sources': 30,
        'minimum_number_of_forces': 0,
        'date': datetime.now().strftime('%Y-%m-%d'),
        'market_force_definition': MARKET_FORCE_DEFINITIONS
    }

    REPORT_FILE = "saved_report.json"
    REPORT_PATH = "Resume_files/saved_report.json"


    @start()
    def market_forces_flow(self):
        """Initial method to check for report"""
        # if os.path.exists(self.REPORT_PATH):
        #     print("Found existing report, resuming...")
        #     return "resume"
        print("starting new flow...")
        return "start_flow"

    @router(market_forces_flow)
    def entry_router(self):
        report_path = os.path.join("Resume_files", "saved_report.json")
        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                report_final_content_dict_saved = json.load(f)
                print(report_final_content_dict_saved)          
            self.state.saved_report = report_final_content_dict_saved
            self.state.saved_research_context = self.research_inputs
            return "report_found"
        else:
            return "report_not_found"

    @listen("report_not_found")
    # generate the list of URLs to Search
    # def identify_sources(self) -> SourceIdentificationResultsURLonly:
    def identify_sources(self):
        self.state.research_context = self.research_inputs
        sources_result = SourceIdentificationCrew().crew().kickoff(self.research_inputs).pydantic
        self.state.source_results = sources_result
        return sources_result

    @listen(identify_sources)
    def identify_market_forces(self, sources_result):
        self.state.research_context = self.research_inputs
        forces_final_content = []
        forces_final_content_dict = []
        for url in sources_result.urls:
            # forces_inputs = self.state.research_context.copy()
            forces_inputs = self.research_inputs.copy()
            forces_inputs['url'] = url.model_dump_json()
            forces_result = MarketForceExtractionCrew().crew().kickoff(forces_inputs).pydantic
            forces_final_content.append(forces_result)
            forces_final_content_dict.append(forces_result.model_dump())
        self.state.extraction_results = forces_final_content
        # print("Extraction Results:", self.state.extraction_results) # this provides a full view of all of the analysis 
        print(forces_final_content) # this also provides a full view of all of the analysis 
        return forces_final_content_dict


# This report crew cycles through the report and does not generate the full view of the marekt research
    # @listen(identify_market_forces)
    # def develop_report(self, forces_final_content):
    #     self.state.research_context = self.research_inputs
    #     report_final_content = []
    #     report_final_content_json = []
    #     report_final_content_dict = []
    #     for raw_market_forces in forces_final_content:
    #         reporting_inputs = self.research_inputs.copy()
    #         reporting_inputs['raw_market_forces'] = raw_market_forces.model_dump_json()
    #         reporting_result = ReportingCrew().crew().kickoff(reporting_inputs).pydantic
    #         report_final_content.append(reporting_result)
    #         report_final_content_json.append(reporting_result.model_dump_json())
    #         report_final_content_dict.append(reporting_result.model_dump())
    #     self.state.report = report_final_content
    #     return report_final_content_dict

    @listen(identify_market_forces)
    def develop_report(self, forces_final_content_dict):
        self.state.research_context = self.research_inputs
        report_final_content = []
        report_final_content_json = []
        report_final_content_dict = []
        reporting_inputs = self.research_inputs.copy()
        reporting_inputs['raw_market_forces'] = forces_final_content_dict
        reporting_result = ReportingCrew().crew().kickoff(reporting_inputs).pydantic
        report_final_content.append(reporting_result)
        report_final_content_json.append(reporting_result.model_dump_json())
        report_final_content_dict.append(reporting_result.model_dump())
        self.state.report = report_final_content
        return report_final_content_dict

    @listen(and_(develop_report, identify_market_forces, identify_sources))
    def print_outputs(self):
        print("=== Sources Result ===\n", self.state.source_results, "\n")
        print("=== Forces Final Content ===\n", self.state.extraction_results, "\n")
        print("=== Reporting Result ===\n", self.state.report, "\n")

    @listen(develop_report)
    def format_report(self, report_final_content_dict):
        self.state.research_context = self.research_inputs
        formatting_inputs = self.research_inputs.copy()
        formatting_inputs['report_final_content'] = report_final_content_dict
        formatting_result = FormattingCrew().crew().kickoff(inputs=formatting_inputs).raw
        self.state.markdown_report = formatting_result
        print("Final Markdown Report:\n")
        print(formatting_result)
        return formatting_result

    @listen("report_found")
    def format_saved_report(self):
        self.state.saved_research_context = self.research_inputs
        formatting_inputs_from_saved = self.research_inputs.copy()
        formatting_inputs_from_saved['report_final_content'] = [self.state.saved_report]
        formatting_result_from_saved = FormattingCrew().crew().kickoff(inputs=formatting_inputs_from_saved).raw
        self.state.markdown_report_from_saved = formatting_result_from_saved
        print("Final Markdown Report:\n")
        print(formatting_result_from_saved)
        return formatting_result_from_saved

    # @listen(develop_report)
    # def format_report(self, report_final_content_json):
    #     self.state.research_context = self.research_inputs
    #     report_final_content = report_final_content_json
    #     formatting_result = FormattingCrew().crew().kickoff(report_final_content).raw
    #     self.state.markdown_report = formatting_result
    #     print("Final Markdown Report:\n")
    #     print(formatting_result)
    #     return formatting_result

    # @listen(develop_report)
    # def format_report(self, report_final_content):
    #     self.state.research_context = self.research_inputs
    #     # Convert list of dicts to JSON string
    #     if isinstance(report_final_content, list):
    #         formatting_input = json.dumps(report_final_content)
    #     else:
    #         formatting_input = report_final_content.model_dump_json()
    #     formatting_result = FormattingCrew().crew().kickoff(formatting_input).raw
    #     self.state.markdown_report = formatting_result
    #     print("Final Markdown Report:\n")
    #     print(formatting_result)
    #     return formatting_result




    # @listen(develop_report)
    # def format_report(self, report_final_content):
    #     self.state.research_context = self.research_inputs
    #     report_final_content = report_final_content.model_dump()
    #     formatting_result = FormattingCrew().crew().kickoff(report_final_content).raw
    #     self.state.markdown_report = formatting_result
    #     print("Final Markdown Report:\n")
    #     print(formatting_result)
    #     return formatting_result


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
