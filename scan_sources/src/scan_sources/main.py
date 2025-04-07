"""Main entry point script for the Scan Sources CrewAI project using Flows defined within."""

import argparse
import json
import os
import sys
from typing import Dict, Any, List, Optional
from datetime import datetime

from pydantic import BaseModel, Field
from crewai import Crew, Task
from crewai.flow import Flow, router, start, listen

# Ensure the src directory is in the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the Crew setup and utility models
from scan_sources.crews.scanner_crew.scanner_crew import ScanSourcesCrew
from scan_sources.utilities.models import SourceFinding, IdentifiedForce, MarketForceOutput

# --- State Model (moved from flow.py) --- #

class ScanSourcesState(BaseModel):
    """State model for the Scan Sources flow."""
    # Initial inputs
    initial_inputs: Dict[str, Any] = Field(default_factory=dict)
    
    # Error tracking
    error_message: Optional[str] = None
    
    # Research plan and review
    research_plan: Optional[Dict[str, Any]] = None
    plan_review: Optional[str] = None
    confirmed_plan: Optional[Dict[str, Any]] = None
    
    # Scan results
    web_findings: List[Any] = Field(default_factory=list)
    document_findings: List[Any] = Field(default_factory=list)
    
    # Synthesized findings
    synthesized_forces: List[Any] = Field(default_factory=list)
    final_forces: List[Any] = Field(default_factory=list)
    
    # Final output
    final_output: Optional[Dict[str, Any]] = None
    
    class Config:
        arbitrary_types_allowed = True

# --- Flow Definition (moved from flow.py) --- #

class ScanSourcesFlow(Flow[ScanSourcesState]):
    """Manages the execution flow for the Scan Sources crew."""

    def __init__(self):
        super().__init__(state_class=ScanSourcesState)
        # Instantiate the underlying crew defined in crew.py
        # This gives access to the configured agents and tasks
        try:
            self.crew_instance: Crew = ScanSourcesCrew().crew()
            # Initialize the state with default values
            self._initial_inputs = {}
        except Exception as e:
            print(f"Error initializing ScanSourcesCrew: {e}")
            # Handle initialization error appropriately
            raise

    @start()
    def prepare_plan(self):
        """Starts the flow by preparing the initial research plan."""
        print("--- Flow Step: Preparing Research Plan ---")
        try:
            # Store initial inputs in the state
            self.state.initial_inputs = self._initial_inputs
            
            # Execute the crew with the initial inputs
            # CrewAI will handle task selection based on the process defined in the crew
            result = self.crew_instance.kickoff(inputs=self._initial_inputs)
            
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
        except Exception as e:
            self.state.error_message = f"Error preparing research plan: {e}"
            print(self.state.error_message)

    @listen(prepare_plan)
    def review_plan(self):
        """Reviews the research plan created in the previous step."""
        print("--- Flow Step: Reviewing Research Plan ---")
        try:
            # Execute the crew with the research plan from state
            inputs = {
                "plan_details": self.state.research_plan,
                **self.state.model_dump(mode='json')
            }
            
            result = self.crew_instance.kickoff(inputs=inputs)
            
            self.state.plan_review = result
            print(f"Plan Review: {self.state.plan_review}")
        except Exception as e:
            self.state.error_message = f"Error reviewing research plan: {e}"
            print(self.state.error_message)

    @listen(review_plan)
    def execute_scans(self):
        """Executes the web and document scans in parallel."""
        print("--- Flow Step: Executing Scans ---")
        
        try:
            # Execute web scan using crew.kickoff()
            inputs = {
                "confirmed_plan": self.state.plan_review,
                **self.state.model_dump(mode='json')
            }
            
            web_result = self.crew_instance.kickoff(inputs=inputs)
            
            # Process web scan results
            if isinstance(web_result, str):
                try:
                    self.state.web_findings = json.loads(web_result)
                except json.JSONDecodeError:
                    self.state.web_findings = {"raw_output": web_result}
            else:
                self.state.web_findings = web_result
                
            print(f"Web Findings Count: {len(self.state.web_findings)}")
        except Exception as e:
            print(f"Error executing web scan: {e}")
            self.state.error_message = f"Error during web scan: {e}"
            
        try:
            # Execute document scan using crew.kickoff()
            inputs = {
                "confirmed_plan": self.state.plan_review,
                **self.state.model_dump(mode='json')
            }
            
            doc_result = self.crew_instance.kickoff(inputs=inputs)
            
            # Process document scan results
            if isinstance(doc_result, str):
                try:
                    self.state.document_findings = json.loads(doc_result)
                except json.JSONDecodeError:
                    self.state.document_findings = {"raw_output": doc_result}
            else:
                self.state.document_findings = doc_result
                
            print(f"Document Findings Count: {len(self.state.document_findings)}")
        except Exception as e:
            print(f"Error executing document scan: {e}")
            self.state.error_message = f"Error during document scan: {e}"

    @listen(execute_scans)
    def synthesize(self):
        """Synthesizes the findings from the scans."""
        print("--- Flow Step: Synthesizing Findings ---")
        try:
            # Execute the crew with the scan results from state
            inputs = {
                "web_findings": self.state.web_findings,
                "doc_findings": self.state.document_findings,
                **self.state.model_dump(mode='json')
            }
            
            result = self.crew_instance.kickoff(inputs=inputs)
            
            if isinstance(result, str):
                try:
                    self.state.synthesized_forces = json.loads(result)
                except json.JSONDecodeError:
                    self.state.synthesized_forces = {"raw_output": result}
            else:
                self.state.synthesized_forces = result
                
            print(f"Synthesized Forces Count: {len(self.state.synthesized_forces)}")
        except Exception as e:
            self.state.error_message = f"Error synthesizing findings: {e}"
            print(self.state.error_message)

    @listen(synthesize)
    def review_findings(self):
        """Reviews the preliminary findings."""
        print("--- Flow Step: Reviewing Findings ---")
        try:
            # Execute the crew with the synthesized findings from state
            inputs = {
                "synthesized_data": self.state.synthesized_forces,
                **self.state.model_dump(mode='json')
            }
            
            result = self.crew_instance.kickoff(inputs=inputs)
            
            if isinstance(result, str):
                try:
                    self.state.final_forces = json.loads(result)
                except json.JSONDecodeError:
                    self.state.final_forces = {"raw_output": result}
            else:
                self.state.final_forces = result
                
            print(f"Final Forces Count: {len(self.state.final_forces)}")
        except Exception as e:
            self.state.error_message = f"Error reviewing findings: {e}"
            print(self.state.error_message)
            self.state.final_forces = self.state.synthesized_forces # Fallback

    @listen(review_findings)
    def generate_report(self):
        """Generates the final report."""
        print("--- Flow Step: Generating Report ---")
        try:
            # Execute the crew with all the state data
            inputs = {
                "reviewed_data": self.state.final_forces,
                **self.state.model_dump(mode='json', exclude_none=True)
            }
            
            result = self.crew_instance.kickoff(inputs=inputs)
            
            if isinstance(result, str):
                try:
                    self.state.final_output = json.loads(result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse final output as JSON: {result}")
                    self.state.final_output = {"raw_output": result}
            elif isinstance(result, dict):
                self.state.final_output = result
            else:
                print(f"Warning: Unexpected final_output type: {type(result)}")
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
        except Exception as e:
            self.state.error_message = f"Error generating report: {e}"
            print(self.state.error_message)

    @listen(generate_report)
    def finish(self):
        """Finishes the flow execution."""
        print("--- Flow Step: Finished ---")
        if hasattr(self.state, 'error_message') and self.state.error_message:
            print(f"Flow completed with error: {self.state.error_message}")
        else:
            print("Flow completed successfully!")
            
        # Return the final state
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
    print("## Welcome to the Scan Sources Crew (Flow Execution)")
    print('-----------------------------------')

    # Input Gathering
    parser = argparse.ArgumentParser(description='Run the Scan Sources Crew Flow.')
    parser.add_argument(
        '--industry',
        type=str,
        default='Banking',
        help='Target industry for the market scan.'
    )
    args = parser.parse_args()

    initial_inputs = {
        'target_industry': args.industry,
        # Add other inputs here as needed
    }

    print(f"\nInitiating flow run with initial inputs:")
    print(json.dumps(initial_inputs, indent=2))
    print('-----------------------------------\n')

    # Flow Execution
    try:
        scan_flow = ScanSourcesFlow()
        final_state = scan_flow.run(initial_inputs=initial_inputs)

        print("\n\n########################")
        print("## Flow Run Completed.")
        print("########################\n")

        # Access results from the final state
        if final_state.error_message:
            print(f"Flow finished with an error: {final_state.error_message}")
        elif final_state.final_output:
            print("Final Result (from Flow State):")
            print(final_state.final_output)

            # Save outputs
            output_dir = "outputs"
            os.makedirs(output_dir, exist_ok=True)
            table_path = os.path.join(output_dir, "market_forces_table.md")
            report_path = os.path.join(output_dir, "market_forces_report.md")
            try:
                with open(table_path, "w", encoding='utf-8') as f:
                    f.write(final_state.final_output.markdown_table)
                with open(report_path, "w", encoding='utf-8') as f:
                    f.write(final_state.final_output.markdown_report)
                print(f"\nMarkdown table and report saved to '{output_dir}' directory.")
            except Exception as e:
                print(f"\nError saving output files: {e}")
        else:
            print("Flow completed, but no final output was generated in the state.")

    except Exception as e:
        print(f"\nAn unexpected error occurred running the flow: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
