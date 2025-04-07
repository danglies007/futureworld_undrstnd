"""Main entry point script for the Scan Sources CrewAI project using Flows defined within."""

import argparse
import json
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from crewai import Crew
from crewai.flow import Flow, router, start, listen

# Ensure the src directory is in the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the Crew setups
from scan_sources.crews.requirements_crew.requirements_crew import RequirementsCrew
from scan_sources.crews.research_crew.research_crew import ResearchCrew
from scan_sources.crews.packaging_crew.packaging_crew import PackagingCrew

# Import utility models
from scan_sources.utilities.models import (
    MarketForceInput, ResearchPlan, SourceFinding, 
    IdentifiedForce, MarketForceOutput
)

# Import Streamlit interface utilities
from scan_sources.utilities.streamlit_interface import update_flow_status
from scan_sources.utilities.human_input_handler import handle_human_input_task

# --- State Model --- #

class ScanSourcesState(BaseModel):
    """State model for the Scan Sources flow."""
    # Initial inputs
    initial_inputs: Dict[str, Any] = Field(default_factory=dict)
    
    # Error tracking
    error_message: Optional[str] = None
    
    # Requirements crew outputs
    research_plan: Optional[Dict[str, Any]] = None
    validated_plan: Optional[Dict[str, Any]] = None
    
    # Research crew outputs
    web_findings: List[Any] = Field(default_factory=list)
    document_findings: List[Any] = Field(default_factory=list)
    synthesized_forces: List[Any] = Field(default_factory=list)
    final_forces: List[Any] = Field(default_factory=list)
    
    # Packaging crew outputs
    markdown_report: Optional[str] = None
    markdown_table: Optional[str] = None
    final_output: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True

# --- Flow Definition --- #

class ScanSourcesFlow(Flow[ScanSourcesState]):
    """Manages the execution flow for the Scan Sources crews."""

    def __init__(self):
        super().__init__(state_class=ScanSourcesState)
        # Instantiate the crews
        try:
            self.requirements_crew: Crew = RequirementsCrew().crew()
            self.research_crew: Crew = ResearchCrew().crew()
            self.packaging_crew: Crew = PackagingCrew().crew()
            # Initialize the state with default values
            self._initial_inputs = {}
            # Initialize flow status for Streamlit interface
            update_flow_status(status="initialized", message="Flow initialized and ready to start")
        except Exception as e:
            print(f"Error initializing crews: {e}")
            raise

    # --- Requirements Crew Flow --- #
    
    @start()
    def prepare_research_plan(self):
        """Starts the flow by preparing the initial research plan using the Requirements Crew."""
        print("--- Flow Step: Preparing Research Plan (Requirements Crew) ---")
        # Update flow status for Streamlit interface
        update_flow_status(
            status="running", 
            message="Preparing initial research plan", 
            current_step="prepare_research_plan"
        )
        try:
            # Store initial inputs in the state
            self.state.initial_inputs = self._initial_inputs
            
            # Execute the requirements crew with the initial inputs
            result = self.requirements_crew.kickoff(
                inputs=self._initial_inputs
            )
            
            if isinstance(result, str):
                try:
                    self.state.research_plan = json.loads(result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse research plan output as JSON: {result}")
                    self.state.research_plan = {"raw_output": result}
            elif isinstance(result, dict):
                self.state.research_plan = result
            else:
                print(f"Warning: Unexpected research plan output type: {type(result)}")
                self.state.research_plan = {"raw_output": str(result)}
            print(f"Prepared Plan: {self.state.research_plan}")
            
            # Return the crew name to route to the next step
            return "requirements"
        except Exception as e:
            self.state.error_message = f"Error preparing research plan: {e}"
            print(self.state.error_message)
            return "error"

    @router(prepare_research_plan)
    def review_research_plan(self, result):
        """Reviews the research plan created in the previous step using the Requirements Crew."""
        print("--- Flow Step: Reviewing Research Plan (Requirements Crew) ---")
        # Update flow status for Streamlit interface
        update_flow_status(
            status="running", 
            message="Reviewing research plan", 
            current_step="review_research_plan"
        )
        try:
            # Execute the requirements crew with the research plan from state
            inputs = {
                "plan_details": self.state.research_plan,
                **self.state.model_dump(mode='json')
            }
            
            result = self.requirements_crew.kickoff(
                inputs=inputs
            )
            
            if isinstance(result, str):
                try:
                    self.state.validated_plan = json.loads(result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse validated plan output as JSON: {result}")
                    self.state.validated_plan = {"raw_output": result}
            elif isinstance(result, dict):
                self.state.validated_plan = result
            else:
                print(f"Warning: Unexpected validated plan output type: {type(result)}")
                self.state.validated_plan = {"raw_output": str(result)}
            
            print(f"Validated Plan: {self.state.validated_plan}")
            return "research"
        except Exception as e:
            self.state.error_message = f"Error reviewing research plan: {e}"
            print(self.state.error_message)
            return "error"

    # --- Research Crew Flow --- #
    
    @listen("research")
    def scan_sources(self):
        """Scans web and document sources based on the validated plan using the Research Crew."""
        print("--- Flow Step: Scanning Sources (Research Crew) ---")
        # Update flow status for Streamlit interface
        update_flow_status(
            status="running", 
            message="Scanning web and document sources", 
            current_step="scan_sources"
        )
        
        # Scan web sources
        try:
            # Execute the research crew with the validated plan for web sources
            inputs = {
                "validated_plan": self.state.validated_plan,
                "source_type": "web",
                **self.state.model_dump(mode='json')
            }
            
            web_result = self.research_crew.kickoff(
                inputs=inputs
            )
            
            if isinstance(web_result, str):
                try:
                    self.state.web_findings = json.loads(web_result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse web findings as JSON: {web_result}")
                    self.state.web_findings = {"raw_output": web_result}
            else:
                self.state.web_findings = web_result
                
            print(f"Web Findings Count: {len(self.state.web_findings) if isinstance(self.state.web_findings, list) else 'N/A'}")
        except Exception as e:
            print(f"Error scanning web sources: {e}")
            self.state.error_message = f"Error during web scan: {e}"
        
        # Scan document sources
        try:
            # Execute the research crew with the validated plan for document sources
            inputs = {
                "validated_plan": self.state.validated_plan,
                "source_type": "document",
                **self.state.model_dump(mode='json')
            }
            
            doc_result = self.research_crew.kickoff(
                inputs=inputs
            )
            
            if isinstance(doc_result, str):
                try:
                    self.state.document_findings = json.loads(doc_result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse document findings as JSON: {doc_result}")
                    self.state.document_findings = {"raw_output": doc_result}
            else:
                self.state.document_findings = doc_result
                
            print(f"Document Findings Count: {len(self.state.document_findings) if isinstance(self.state.document_findings, list) else 'N/A'}")
        except Exception as e:
            print(f"Error scanning document sources: {e}")
            self.state.error_message = f"Error during document scan: {e}"
        
        # Continue to synthesis if we have findings
        if self.state.web_findings or self.state.document_findings:
            return "synthesize"
        else:
            self.state.error_message = "No findings from either web or document sources."
            return "error"

    @listen("synthesize")
    def synthesize_findings(self):
        """Synthesizes the findings from the scans using the Research Crew."""
        print("--- Flow Step: Synthesizing Findings (Research Crew) ---")
        # Update flow status for Streamlit interface
        update_flow_status(
            status="running", 
            message="Synthesizing data from sources", 
            current_step="synthesize_findings"
        )
        try:
            # Execute the research crew with the scan results
            inputs = {
                "web_findings": self.state.web_findings,
                "doc_findings": self.state.document_findings,
                **self.state.model_dump(mode='json')
            }
            
            result = self.research_crew.kickoff(
                inputs=inputs
            )
            
            if isinstance(result, str):
                try:
                    self.state.synthesized_forces = json.loads(result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse synthesized forces as JSON: {result}")
                    self.state.synthesized_forces = {"raw_output": result}
            else:
                self.state.synthesized_forces = result
                
            print(f"Synthesized Forces Count: {len(self.state.synthesized_forces) if isinstance(self.state.synthesized_forces, list) else 'N/A'}")
            return "review"
        except Exception as e:
            self.state.error_message = f"Error synthesizing findings: {e}"
            print(self.state.error_message)
            return "error"

    @listen("review")
    def review_findings(self):
        """Reviews the preliminary findings with human input using the Research Crew."""
        print("--- Flow Step: Reviewing Findings (Research Crew) ---")
        # Update flow status for Streamlit interface
        update_flow_status(
            status="running", 
            message="Preparing to review findings with human input", 
            current_step="review_findings"
        )
        
        try:
            # Get the synthesized findings from the state
            synthesized_forces = self.state.synthesized_forces
            
            # Prepare inputs for the research crew
            inputs = {
                "synthesized_forces": synthesized_forces,
                **self.state.model_dump(mode='json')
            }
            
            # Check if we need to handle human input
            task_description = "Review the preliminary findings and provide feedback on the identified market forces."
            
            # Use the human input handler to get feedback through Streamlit
            human_feedback = handle_human_input_task(
                task_id="review_preliminary_findings",
                task_description=task_description,
                data_to_review=synthesized_forces
            )
            
            # Add human feedback to the inputs
            inputs["human_feedback"] = human_feedback
            
            # Execute the research crew with the inputs including human feedback
            result = self.research_crew.kickoff(
                inputs=inputs
            )
            
            if isinstance(result, str):
                try:
                    self.state.final_forces = json.loads(result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse final forces as JSON: {result}")
                    self.state.final_forces = {"raw_output": result}
            else:
                self.state.final_forces = result
                
            print(f"Final Forces Count: {len(self.state.final_forces) if isinstance(self.state.final_forces, list) else 'N/A'}")
            return "packaging"
        except Exception as e:
            self.state.error_message = f"Error during findings review: {e}"
            print(self.state.error_message)
            return "error"

    # --- Packaging Crew Flow --- #
    
    @listen("packaging")
    def generate_outputs(self):
        """Generates the markdown report and table using the Packaging Crew."""
        print("--- Flow Step: Generating Outputs (Packaging Crew) ---")
        # Update flow status for Streamlit interface
        update_flow_status(
            status="running", 
            message="Generating final report and table", 
            current_step="generate_outputs"
        )
        
        # Generate markdown report
        try:
            # Execute the packaging crew with the final forces for report
            inputs = {
                "identified_forces": self.state.final_forces,
                "output_type": "report",
                **self.state.model_dump(mode='json')
            }
            
            report_result = self.packaging_crew.kickoff(
                inputs=inputs
            )
            
            self.state.markdown_report = report_result
            print(f"Markdown Report Generated: {len(self.state.markdown_report) if isinstance(self.state.markdown_report, str) else 'N/A'} characters")
        except Exception as e:
            self.state.error_message = f"Error generating markdown report: {e}"
            print(self.state.error_message)
        
        # Generate markdown table
        try:
            # Execute the packaging crew with the final forces for table
            inputs = {
                "identified_forces": self.state.final_forces,
                "output_type": "table",
                **self.state.model_dump(mode='json')
            }
            
            table_result = self.packaging_crew.kickoff(
                inputs=inputs
            )
            
            self.state.markdown_table = table_result
            print(f"Markdown Table Generated: {len(self.state.markdown_table) if isinstance(self.state.markdown_table, str) else 'N/A'} characters")
        except Exception as e:
            self.state.error_message = f"Error generating markdown table: {e}"
            print(self.state.error_message)
        
        # Continue to final packaging if we have outputs
        if self.state.markdown_report or self.state.markdown_table:
            return "finalize"
        else:
            self.state.error_message = "No report or table generated."
            return "error"

    @listen("finalize")
    def package_outputs(self):
        """Packages all outputs into a final MarketForceOutput using the Packaging Crew."""
        print("--- Flow Step: Packaging Outputs (Packaging Crew) ---")
        # Update flow status for Streamlit interface
        update_flow_status(
            status="running", 
            message="Packaging final output", 
            current_step="package_outputs"
        )
        try:
            # Execute the packaging crew with all outputs
            inputs = {
                "identified_forces": self.state.final_forces,
                "markdown_report": self.state.markdown_report,
                "markdown_table": self.state.markdown_table,
                **self.state.model_dump(mode='json')
            }
            
            result = self.packaging_crew.kickoff(
                inputs=inputs
            )
            
            if isinstance(result, str):
                try:
                    self.state.final_output = json.loads(result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse final output as JSON: {result}")
                    self.state.final_output = {"raw_output": result}
            elif isinstance(result, dict):
                self.state.final_output = result
            else:
                print(f"Warning: Unexpected final output type: {type(result)}")
                self.state.final_output = {"raw_output": str(result)}
                
            # Save the report to a file
            try:
                report_path = os.path.join(
                    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                    "outputs", 
                    f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )
                os.makedirs(os.path.dirname(report_path), exist_ok=True)
                with open(report_path, 'w') as f:
                    json.dump(self.state.final_output, f, indent=2)
                print(f"Report saved to: {report_path}")
            except Exception as e:
                print(f"Warning: Failed to save report to file: {e}")
            
            return "complete"
        except Exception as e:
            self.state.error_message = f"Error packaging outputs: {e}"
            print(self.state.error_message)
            return "error"

    @listen("complete")
    def finish_success(self):
        """Finishes the flow execution with success."""
        print("--- Flow Step: Finished Successfully ---")
        print("Flow completed successfully!")
        return self.state

    @listen("error")
    def finish_error(self):
        """Finishes the flow execution with error."""
        print("--- Flow Step: Finished With Error ---")
        print(f"Flow completed with error: {self.state.error_message}")
        return self.state

    def run(self, initial_inputs: Dict[str, Any]):
        """Convenience method to kickoff the flow with initial state."""
        # Store initial inputs for use in prepare_plan
        self._initial_inputs = initial_inputs
        
        # Initialize state with initial inputs
        self.state.initial_inputs = initial_inputs
        
        # Kickoff the flow
        try:
            final_state = self.kickoff()
            
            # Print the final state for debugging
            if final_state:
                print("\n--- Final Flow State ---")
                print(json.dumps(final_state.model_dump(mode='json', exclude_none=True), indent=2))
            else:
                print("\n--- Warning: No final state returned from flow ---")
                
            return final_state
        except Exception as e:
            print(f"Error during flow execution: {e}")
            # Return the current state if there was an error
            return self.state

# --- Main Execution Logic --- #

def main():
    """Main function to run the Scan Sources flow."""
    parser = argparse.ArgumentParser(description="Run the Scan Sources CrewAI flow")
    parser.add_argument("--input", type=str, help="Path to input JSON file")
    args = parser.parse_args()
    
    # Initialize the flow
    flow = ScanSourcesFlow()
    
    try:
        # Load input data if provided
        if args.input and os.path.exists(args.input):
            with open(args.input, 'r') as f:
                input_data = json.load(f)
                flow._initial_inputs = input_data
        
        # Print startup message about Streamlit interface
        print("\n=== CrewAI Scan Sources Flow ===")
        print("A Streamlit interface is available for human interactions.")
        print("To use it, run the following command in a separate terminal:")
        print("streamlit run scan_sources/src/scan_sources/streamlit_app.py\n")
        
        # Run the flow
        result = flow.kickoff()
        
        # Update flow status to completed
        update_flow_status(
            status="completed", 
            message="Flow completed successfully", 
            current_step="completed"
        )
        
        # Save the result to a file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_file = f"scan_sources_result_{timestamp}.json"
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        
        print(f"\nFlow completed successfully. Results saved to {output_file}")
        return result
    
    except Exception as e:
        # Update flow status to error
        update_flow_status(
            status="error", 
            message=f"Flow failed with error: {str(e)}", 
            current_step="error"
        )
        
        print(f"Error running flow: {e}")
        raise

if __name__ == "__main__":
    main()
