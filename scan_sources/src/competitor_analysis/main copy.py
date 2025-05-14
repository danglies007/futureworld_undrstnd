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
from competitor_analysis.crews.internal_analysis_crew.internal_analysis_crew import InternalAnalysisCrew
from competitor_analysis.crews.external_analysis_crew.external_analysis_crew import ExternalAnalysisCrew
from competitor_analysis.crews.integrated_analysis_crew.integrated_analysis_crew import IntegratedAnalysisCrew

from competitor_analysis.config_competitor_analysis import RESEARCH_INPUTS

# Models for source internal analysis crew
from competitor_analysis.competitor_analysis_models import (
    CompanyInternalAnalysis,
    CompanyExternalAnalysis,
    CompanyIntegratedAnalysis
)

class CompetitorAnalysisState(BaseModel):
    research_context: dict = None
    internal_analysis: CompanyInternalAnalysis = None
    external_analysis: CompanyExternalAnalysis = None
    integrated_analysis: CompanyIntegratedAnalysis = None

class CompetitorAnalysisFlow(Flow[CompetitorAnalysisState]):

    research_inputs = RESEARCH_INPUTS


    @start()
    def competitor_analysis_flow(self):
        """Initial method to check for report"""
        print("starting new flow...")
        return "start_flow"

    # @router(competitor_analysis_flow)
    # def entry_router(self):
    #     # Assuming a flow has already run, add some additional user urls against which to extract market forces
    #     url_path = os.path.join("Resume_files", "user_urls.json")
    #     if os.path.exists(url_path):
    #         # Read the file content
    #         with open(url_path, "r") as f:
    #             json_content = f.read()
                
    #         # Convert the JSON string directly to a SourceApprovedResults object
    #         from scan_sources.models import SourceApprovedResults
    #         sources_result = SourceApprovedResults.model_validate_json(json_content)
    #         print(f"Loaded user_urls.json as SourceApprovedResults")
            
    #         self.state.source_approved_results = sources_result
    #         return "user_urls_found"

    #     # If no user urls found, check for a saved report to move directly to formatting
    #     else:
    #         report_path = os.path.join("Resume_files", "saved_report.json")
    #         aggregated_market_forces_path = os.path.join("Resume_files", "aggregated_market_forces.json")
    #         implications_report_path = os.path.join("Resume_files", "implications_report.json")
    #         if os.path.exists(report_path):
    #             with open(report_path, "r") as f:
    #                 report_final_content_dict_saved = json.load(f)
    #             with open(implications_report_path, "r") as f:
    #                 implications_report_dict_saved = json.load(f)
    #             print(report_final_content_dict_saved)          
    #             self.state.saved_report = report_final_content_dict_saved
    #             self.state.saved_implications_report = implications_report_dict_saved
    #             self.state.saved_research_context = self.research_inputs
    #             return "report_found"
    #         elif os.path.exists(aggregated_market_forces_path):
    #             with open(aggregated_market_forces_path, "r") as f:
    #                 aggregated_market_forces_content_dict_saved = json.load(f)
    #                 print(aggregated_market_forces_content_dict_saved)          
    #             self.state.aggregated_market_forces = aggregated_market_forces_content_dict_saved
    #             self.state.saved_research_context = self.research_inputs
    #             return "aggregated_market_forces_found"
    #         else:
    #             return "report_not_found"

    # Start the flow from scratch searching for sources
    @listen("start_flow")
    def internal_analysis(self):
        self.state.research_context = self.research_inputs
        internal_analysis_inputs = self.research_inputs.copy()
        internal_analysis_result = InternalAnalysisCrew().crew().kickoff(internal_analysis_inputs).pydantic
        self.state.internal_analysis = internal_analysis_result
        return internal_analysis_result

    @listen("internal_analysis")
    def external_analysis(self):
        self.state.research_context = self.research_inputs
        external_analysis_inputs = self.research_inputs.copy()
        external_analysis_result = ExternalAnalysisCrew().crew().kickoff(external_analysis_inputs).pydantic
        self.state.external_analysis = external_analysis_result
        return external_analysis_result

    @listen(and_(internal_analysis, external_analysis))
    def integrated_analysis(self):
        self.state.research_context = self.research_inputs
        integrated_analysis_inputs = self.research_inputs.copy()
        integrated_analysis_inputs['internal_analysis'] = self.state.internal_analysis
        integrated_analysis_inputs['external_analysis'] = self.state.external_analysis
        integrated_analysis_result = IntegratedAnalysisCrew().crew().kickoff(integrated_analysis_inputs).pydantic
        self.state.integrated_analysis = integrated_analysis_result
        return integrated_analysis_result

# # Develop the report from the forces
#     @listen(integrated_analysis_result)
#     def develop_report(self):
#         self.state.research_context = self.research_inputs
#         report_final_content = []
#         report_final_content_json = []
#         report_final_content_dict = []
#         reporting_inputs = self.research_inputs.copy()
#         reporting_inputs['raw_market_forces'] = forces_final_content_dict
#         reporting_result = ReportingCrew().crew().kickoff(reporting_inputs).pydantic
#         report_final_content.append(reporting_result)
#         report_final_content_json.append(reporting_result.model_dump_json())
#         report_final_content_dict.append(reporting_result.model_dump())
#         self.state.report = report_final_content
#         return report_final_content_dict

    # Identify market forces from the sources
    # @listen(or_(identify_sources, identify_sources_from_user_urls))
    # def identify_market_forces(self, sources_result):
    #     import json
    #     from datetime import datetime   

    #     self.state.research_context = self.research_inputs
    #     forces_final_content = []
    #     forces_final_content_dict = []

    #     # Loop through the URLs to extract the sources
    #     for source in sources_result.approved_sources:
    #         # forces_inputs = self.state.research_context.copy()
    #         forces_inputs = self.research_inputs.copy()
    #         forces_inputs['url'] = source.url
    #         forces_inputs['source_type'] = source.source_type
    #         forces_inputs['source_date'] = source.source_date

    #         forces_result = MarketForceExtractionCrew().crew().kickoff(forces_inputs).pydantic
    #         forces_final_content.append(forces_result)
    #         forces_final_content_dict.append(forces_result.model_dump())

    #     self.state.extraction_results = forces_final_content
    #     print(forces_final_content) # this also provides a full view of all of the analysis 
        
    #     # Create an aggregated file and Save the already aggregated results to a JSON file
    #     specialisation = self.research_inputs.get("specialisation", "general")
    #     topic_short = self.research_inputs.get("topic_short", "market_forces")
    #     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    #     output_dir = "outputs"
    #     os.makedirs(output_dir, exist_ok=True)
    #     output_filename = os.path.join(
    #         output_dir, 
    #         f'aggregated_market_forces_{specialisation}_{topic_short}_{timestamp}.json'
    #     )
    
    #     with open(output_filename, 'w', encoding='utf-8') as json_file:
    #         json.dump(forces_final_content_dict, json_file, indent=4, ensure_ascii=False)
    
    #     print(f"Aggregated market forces saved to: {output_filename}")
        
    #     return forces_final_content_dict

# # Develop the report from the forces
#     @listen(identify_market_forces)
#     def develop_report(self, forces_final_content_dict):
#         self.state.research_context = self.research_inputs
#         report_final_content = []
#         report_final_content_json = []
#         report_final_content_dict = []
#         reporting_inputs = self.research_inputs.copy()
#         reporting_inputs['raw_market_forces'] = forces_final_content_dict
#         reporting_result = ReportingCrew().crew().kickoff(reporting_inputs).pydantic
#         report_final_content.append(reporting_result)
#         report_final_content_json.append(reporting_result.model_dump_json())
#         report_final_content_dict.append(reporting_result.model_dump())
#         self.state.report = report_final_content
#         return report_final_content_dict

#     @listen("aggregated_market_forces_found")
#     def develop_saved_report(self):
#         self.state.research_context = self.research_inputs
#         report_final_content = []
#         report_final_content_json = []
#         report_final_content_dict = []
#         reporting_inputs = self.research_inputs.copy()
#         reporting_inputs['raw_market_forces'] = self.state.aggregated_market_forces
#         reporting_result = ReportingCrew().crew().kickoff(reporting_inputs).pydantic
#         report_final_content.append(reporting_result)
#         report_final_content_json.append(reporting_result.model_dump_json())
#         report_final_content_dict.append(reporting_result.model_dump())
#         self.state.report = report_final_content
#         return report_final_content_dict

# # Develop Implications Report
#     @listen(identify_market_forces)
#     def develop_implications_report(self, forces_final_content_dict):
#         implications_inputs = self.research_inputs.copy()
#         implications_inputs['raw_market_forces'] = forces_final_content_dict
#         implications_result = ImplicationsCrew().crew().kickoff(implications_inputs).pydantic
#         self.state.implications_report = implications_result
#         return implications_result

#     @listen("aggregated_market_forces_found")
#     def develop_saved_implications_report(self):
#         implications_inputs = self.research_inputs.copy()
#         implications_inputs['raw_market_forces'] = self.state.aggregated_market_forces
#         implications_result = ImplicationsCrew().crew().kickoff(implications_inputs).pydantic
#         self.state.implications_report = implications_result
#         return implications_result

#     @listen(and_(develop_report, identify_market_forces, identify_sources))
#     def print_outputs(self):
#         print("=== Sources Result ===\n", self.state.source_approved_results, "\n")
#         print("=== Forces Final Content ===\n", self.state.extraction_results, "\n")
#         print("=== Reporting Result ===\n", self.state.report, "\n")

#     # Format the report into markdown from within the normal flow
#     @listen(or_(develop_report, develop_saved_report))
#     def format_report(self, report_final_content_dict):
#         self.state.research_context = self.research_inputs
#         formatting_inputs = self.research_inputs.copy()
#         formatting_inputs['report_final_content'] = report_final_content_dict
#         formatting_inputs['implications_report_content'] = self.state.implications_report
#         formatting_result = FormattingCrew().crew().kickoff(inputs=formatting_inputs).raw
#         self.state.markdown_report = formatting_result
#         print("Final Markdown Report:\n")
#         print(formatting_result)
#         return formatting_result

#     # Format the report into markdown from a saved report
#     @listen("report_found")
#     def format_saved_report(self):
#         self.state.saved_research_context = self.research_inputs
#         formatting_inputs_from_saved = self.research_inputs.copy()
#         formatting_inputs_from_saved['report_final_content'] = [self.state.saved_report]
#         formatting_inputs_from_saved['implications_report_content'] = [self.state.saved_implications_report]
#         formatting_result_from_saved = FormattingCrew().crew().kickoff(inputs=formatting_inputs_from_saved).raw
#         self.state.markdown_report_from_saved = formatting_result_from_saved
#         print("Final Markdown Report:\n")
#         print(formatting_result_from_saved)
#         return formatting_result_from_saved

# def kickoff_comp():
#     competitor_analysis_flow = CompetitorAnalysisFlow()
#     competitor_analysis_flow.kickoff_comp()

# def plot_comp():
#     competitor_analysis_flow = CompetitorAnalysisFlow()
#     competitor_analysis_flow.plot_comp()

# if __name__ == "__main__":
#     kickoff_comp()

def kickoff():
    competitor_analysis_flow = CompetitorAnalysisFlow()
    competitor_analysis_flow.kickoff()

def plot():
    competitor_analysis_flow = CompetitorAnalysisFlow()
    competitor_analysis_flow.plot()

if __name__ == "__main__":
    kickoff()
