import os
import json
import sys
import warnings
import traceback
from datetime import datetime
from typing import Dict, Any
from dotenv import load_dotenv
load_dotenv()
# import agentops
# agentops.init()
                
from pydantic import BaseModel
from crewai.flow import Flow, start, router,listen, and_, or_
from scan_sources.crews.source_identification_crew.source_identification_crew import SourceIdentificationCrew
from scan_sources.crews.market_force_extraction_crew.market_force_extraction_crew import MarketForceExtractionCrew
from scan_sources.crews.implications_crew.implications_crew import ImplicationsCrew
from scan_sources.crews.reporting_crew.reporting_crew import ReportingCrew
from scan_sources.crews.formatting_crew.formatting_crew import FormattingCrew
from scan_sources.config import RESEARCH_INPUTS, SOURCES_FUTURISTS, MARKET_FORCE_DEFINITIONS, SOURCES_CONSULTING_FIRMS, SOURCES_NEWS_SOURCES
# Models for source identification crew
from scan_sources.models import (
    SourceDiscoveryResults, 
    SourceEvaluationResults, 
    SourceApprovedResults
)

# Models for market force extraction crew
from scan_sources.models import (
    MarketForceAnalysisReport,
    ResearchOutput,
)

# Models for implications crew
from scan_sources.models import (
    ImplicationAnalysisReport,
)

class ScanState(BaseModel):
    research_context: dict = None
    source_discovery_results: SourceDiscoveryResults = None
    source_evaluation_results: SourceEvaluationResults = None
    source_approved_results: SourceApprovedResults = None
    aggregated_market_forces: list = None
    extraction_results: ResearchOutput = None
    report: MarketForceAnalysisReport = None
    markdown_report: str = None
    markdown_report_from_saved: str = None
    saved_research_context: dict = None
    saved_report: MarketForceAnalysisReport = None
    user_urls: dict = None
    user_urls_research_context: dict = None
    implications_report: ImplicationAnalysisReport = None
    saved_implications_report: ImplicationAnalysisReport = None

class ScanFlow(Flow[ScanState]):

    research_inputs = RESEARCH_INPUTS

    # I dont think this is needed anymore
    REPORT_FILE = "saved_report.json"
    REPORT_PATH = "Resume_files/saved_report.json"


    @start()
    def market_forces_flow(self):
        """Initial method to check for report"""
        print("starting new flow...")
        return "start_flow"

    @router(market_forces_flow)
    def entry_router(self):
        # Assuming a flow has already run, add some additional user urls against which to extract market forces
        url_path = os.path.join("Resume_files", "user_urls.json")
        if os.path.exists(url_path):
            # Read the file content
            with open(url_path, "r") as f:
                json_content = f.read()
                
            # Convert the JSON string directly to a SourceApprovedResults object
            from scan_sources.models import SourceApprovedResults
            sources_result = SourceApprovedResults.model_validate_json(json_content)
            print(f"Loaded user_urls.json as SourceApprovedResults")
            
            self.state.source_approved_results = sources_result
            return "user_urls_found"

    # def entry_router(self):
    #     # Assuming a flow has already run, add some additional user urls against which to extract market forces
    #     url_path = os.path.join("Resume_files", "user_urls.json")
    #     if os.path.exists(url_path):
    #         with open(url_path, "r") as f:
    #             user_urls = json.load(f)
    #             print(f"Loaded user_urls.json: {user_urls}")
        
    #         # Convert the dictionary to a SourceIdentificationResults object
    #         from scan_sources.models import SourceIdentificationResults
    #         sources_result = SourceIdentificationResults.model_validate(user_urls_dict)
            
    #         self.state.source_results = sources_result
    #         return "user_urls_found"


        # If no user urls found, check for a saved report to move directly to formatting
        else:
            report_path = os.path.join("Resume_files", "saved_report.json")
            aggregated_market_forces_path = os.path.join("Resume_files", "aggregated_market_forces.json")
            implications_report_path = os.path.join("Resume_files", "implications_report.json")
            if os.path.exists(report_path):
                with open(report_path, "r") as f:
                    report_final_content_dict_saved = json.load(f)
                with open(implications_report_path, "r") as f:
                    implications_report_dict_saved = json.load(f)
                print(report_final_content_dict_saved)          
                self.state.saved_report = report_final_content_dict_saved
                self.state.saved_implications_report = implications_report_dict_saved
                self.state.saved_research_context = self.research_inputs
                return "report_found"
            elif os.path.exists(aggregated_market_forces_path):
                with open(aggregated_market_forces_path, "r") as f:
                    aggregated_market_forces_content_dict_saved = json.load(f)
                    print(aggregated_market_forces_content_dict_saved)          
                self.state.aggregated_market_forces = aggregated_market_forces_content_dict_saved
                self.state.saved_research_context = self.research_inputs
                return "aggregated_market_forces_found"
            else:
                return "report_not_found"

    # Start the flow from scratch searching for sources
    @listen("report_not_found")
    # generate the list of URLs to Search
    def identify_sources(self):
        self.state.research_context = self.research_inputs
        sources_inputs = self.research_inputs.copy()
        # Add a placeholder for potential_sources if the crew expects to generate this internally
        # sources_inputs['potential_sources'] = [] # Passes the variable to the crew as a empty list
        # sources_inputs['approved_sources'] = []
        sources_result = SourceIdentificationCrew().crew().kickoff(sources_inputs).pydantic
        self.state.source_approved_results = sources_result
        return sources_result


    # Generate sources from the user urls
    # @listen("user_urls_found")
    # def identify_sources_from_user_urls(self):
    #     # self.state.user_urls_research_context = self.research_inputs
    #     sources_result = self.state.source_results
    #     # sources_user_inputs = self.research_inputs.copy()
    #     sources_result = self.state.user_urls
    #     # sources_result = SourceIdentificationCrew().crew().kickoff(sources_user_inputs).pydantic
    #     # sources_result = self.state.user_urls
    #     return sources_result

    @listen("user_urls_found")
    def identify_sources_from_user_urls(self):
        print("Using pre-formatted SourceIdentificationResults from user URLs file.")
        # The SourceIdentificationResults model instance is already loaded and validated in entry_router
        # and stored in self.state.source_results.
        # We just need to return it.
        sources_results = self.state.source_approved_results
        # self.state.source_results = sources_results

        # print(f"Loaded {sources_results.total_sources_found} sources from user file.")

        # Return the Pydantic model instance to pass to the next task
        return sources_results


    # # Generate sources from the user urls
    # @listen("user_urls_found")
    # def identify_sources_from_user_urls(self):
    #     self.state.user_urls_research_context = self.research_inputs
    #     sources_user_inputs = self.research_inputs.copy()
    #     sources_user_inputs.update(self.state.user_urls)
    #     sources_result = SourceIdentificationCrew().crew().kickoff(sources_user_inputs).pydantic
    #     self.state.source_results = sources_result
    #     return sources_result

    # # TEMP Format the report into markdown from a saved report # Delete one above is working
    # @listen("report_found")
    # def format_saved_report(self):
    #     self.state.saved_research_context = self.research_inputs
    #     formatting_inputs_from_saved = self.research_inputs.copy()
    #     formatting_inputs_from_saved['report_final_content'] = [self.state.saved_report]
    #     formatting_result_from_saved = FormattingCrew().crew().kickoff(inputs=formatting_inputs_from_saved).raw
    #     self.state.markdown_report_from_saved = formatting_result_from_saved
    #     print("Final Markdown Report:\n")
    #     print(formatting_result_from_saved)
    #     return formatting_result_from_saved


    # Identify market forces from the sources
    @listen(or_(identify_sources, identify_sources_from_user_urls))
    def identify_market_forces(self, sources_result):
        import json
        from datetime import datetime   

        self.state.research_context = self.research_inputs
        forces_final_content = []
        forces_final_content_dict = []

        # Loop through the URLs to extract the sources
        for source in sources_result.approved_sources:
            # forces_inputs = self.state.research_context.copy()
            forces_inputs = self.research_inputs.copy()
            forces_inputs['url'] = source.url
            forces_inputs['source_type'] = source.source_type
            forces_inputs['source_date'] = source.source_date

            forces_result = MarketForceExtractionCrew().crew().kickoff(forces_inputs).pydantic
            forces_final_content.append(forces_result)
            forces_final_content_dict.append(forces_result.model_dump())

        self.state.extraction_results = forces_final_content
        print(forces_final_content) # this also provides a full view of all of the analysis 
        
        # Create an aggregated file and Save the already aggregated results to a JSON file
        specialisation = self.research_inputs.get("specialisation", "general")
        topic_short = self.research_inputs.get("topic_short", "market_forces")
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        output_filename = os.path.join(
            output_dir, 
            f'aggregated_market_forces_{specialisation}_{topic_short}_{timestamp}.json'
        )
    
        with open(output_filename, 'w', encoding='utf-8') as json_file:
            json.dump(forces_final_content_dict, json_file, indent=4, ensure_ascii=False)
    
        print(f"Aggregated market forces saved to: {output_filename}")
        
        return forces_final_content_dict

# Develop the report from the forces
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

# Develop Implications Report from the forces
    @listen(identify_market_forces)
    def develop_implications_report(self, forces_final_content_dict):
        self.state.research_context = self.research_inputs
        implications_report_final_content = []
        implications_report_final_content_json = []
        implications_report_final_content_dict = []

        implications_inputs = self.research_inputs.copy()
        implications_inputs['raw_market_forces'] = forces_final_content_dict
        implications_result = ImplicationsCrew().crew().kickoff(implications_inputs).pydantic

        implications_report_final_content.append(implications_result)
        implications_report_final_content_json.append(implications_result.model_dump_json())
        implications_report_final_content_dict.append(implications_result.model_dump())
        self.state.implications_report = implications_result
        return implications_report_final_content_dict

# developing content from saved files
# Develop the report from a saved market forces file
    @listen("aggregated_market_forces_found")
    def develop_saved_report(self):
        self.state.research_context = self.research_inputs
        report_final_content = []
        report_final_content_json = []
        report_final_content_dict = []

        reporting_inputs = self.research_inputs.copy()
        reporting_inputs['raw_market_forces'] = self.state.aggregated_market_forces
        reporting_result = ReportingCrew().crew().kickoff(reporting_inputs).pydantic

        report_final_content.append(reporting_result)
        report_final_content_json.append(reporting_result.model_dump_json())
        report_final_content_dict.append(reporting_result.model_dump())
        self.state.report = report_final_content
        return report_final_content_dict

# Develop the implications report from a saved market forces file
    @listen("aggregated_market_forces_found")
    def develop_saved_implications_report(self):
        implications_report_final_content = []
        implications_report_final_content_json = []
        implications_report_final_content_dict = []

        implications_inputs = self.research_inputs.copy()
        implications_inputs['raw_market_forces'] = self.state.aggregated_market_forces
        implications_result = ImplicationsCrew().crew().kickoff(implications_inputs).pydantic

        implications_report_final_content.append(implications_result)
        implications_report_final_content_json.append(implications_result.model_dump_json())
        implications_report_final_content_dict.append(implications_result.model_dump())
        self.state.implications_report = implications_report_final_content
        return implications_report_final_content_dict

    # Format the report into markdown from a saved report
    @listen("report_found")
    def format_saved_report(self):
        self.state.saved_research_context = self.research_inputs
        formatting_inputs_from_saved = self.research_inputs.copy()
        formatting_inputs_from_saved['report_final_content'] = [self.state.saved_report]
        formatting_inputs_from_saved['implications_report_content'] = [self.state.saved_implications_report]
        formatting_result_from_saved = FormattingCrew().crew().kickoff(inputs=formatting_inputs_from_saved).raw
        self.state.markdown_report_from_saved = formatting_result_from_saved
        print("Final Markdown Report:\n")
        print(formatting_result_from_saved)
        return formatting_result_from_saved

# Format the reports into markdown from within the normal flow
    @listen(or_(develop_report, develop_saved_report))
    def format_report(self, report_final_content_dict, implications_report_final_content_dict):
        self.state.research_context = self.research_inputs
        formatting_inputs = self.research_inputs.copy()
        formatting_inputs['report_final_content'] = report_final_content_dict
        formatting_inputs['implications_report_content'] = implications_report_final_content_dict
        formatting_result = FormattingCrew().crew().kickoff(inputs=formatting_inputs).raw
        self.state.markdown_report = formatting_result
        print("Final Markdown Report:\n")
        print(formatting_result)
        return formatting_result

    @listen(and_(develop_report, develop_implications_report, identify_market_forces, identify_sources))
    def print_outputs(self):
        print("=== Sources Result ===\n", self.state.source_approved_results, "\n")
        print("=== Forces Final Content ===\n", self.state.extraction_results, "\n")
        print("=== Reporting Result ===\n", self.state.report, "\n")
        print("=== Implications Reporting Result ===\n", self.state.implications_report, "\n")



def kickoff():
    scan_flow = ScanFlow()
    scan_flow.kickoff()

def plot():
    scan_flow = ScanFlow()
    scan_flow.plot()

if __name__ == "__main__":
    kickoff()
