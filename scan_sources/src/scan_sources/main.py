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

# Suppress the Pydantic warnings
import warnings
from pydantic import PydanticDeprecatedSince211

# Suppress the specific Pydantic warning
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince211)

# Ensure the src directory is in the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import the Crew setups
from scan_sources.crews.requirements_crew.requirements_crew import RequirementsCrew
from scan_sources.crews.research_crew.research_crew import ResearchCrew
from scan_sources.crews.packaging_crew.packaging_crew import PackagingCrew

# Import utility models and config
from scan_sources.utilities.models import (
    MarketForceInput, ResearchPlan, SourceFinding, 
    IdentifiedForce, MarketForceOutput
)
from scan_sources.utilities.flow_config import FLOW_VARIABLES

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
        # Initialize the state with default values
        self._initial_inputs = {}
        # We'll instantiate crews when needed rather than at initialization
        # This helps avoid issues with crew reuse across different steps

    # --- Requirements Crew Flow --- #
    
    @start()
    def prepare_research_plan(self):
        """Starts the flow by preparing the initial research plan using the Requirements Crew."""
        print("--- Flow Step: Preparing Research Plan (Requirements Crew) ---")
        try:
            # Store initial inputs in the state (should already be done in run method)
            if not hasattr(self.state, 'initial_inputs') or not self.state.initial_inputs:
                self.state.initial_inputs = self._initial_inputs.model_dump() if hasattr(self._initial_inputs, 'model_dump') else self._initial_inputs
            
            # Create a fresh requirements crew for this step
            requirements_crew = RequirementsCrew().crew()
            
            # Format the initial inputs as a JSON string for template substitution
            initial_inputs_str = json.dumps(self.state.initial_inputs, indent=2)
            
            # Execute the crew with the proper template variables
            result = requirements_crew.kickoff(
                inputs={"initial_inputs": initial_inputs_str}
            )
            
            # Process the result into a ResearchPlan Pydantic model
            if isinstance(result, str):
                try:
                    # Try to parse as JSON first
                    plan_dict = json.loads(result)
                    research_plan = ResearchPlan(**plan_dict)
                    self.state.research_plan = research_plan.model_dump()
                except (json.JSONDecodeError, TypeError):
                    print(f"Warning: Failed to parse research plan output as JSON: {result}")
                    self.state.research_plan = {"raw_output": result}
            elif isinstance(result, dict):
                try:
                    research_plan = ResearchPlan(**result)
                    self.state.research_plan = research_plan.model_dump()
                except TypeError as e:
                    print(f"Warning: Failed to create ResearchPlan from dict: {e}")
                    self.state.research_plan = result
            elif isinstance(result, ResearchPlan):
                self.state.research_plan = result.model_dump()
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
        try:
            # Create a fresh requirements crew for this step
            requirements_crew = RequirementsCrew().crew()
            
            # Convert research_plan back to a ResearchPlan model if it's a dict
            if isinstance(self.state.research_plan, dict):
                try:
                    research_plan = ResearchPlan(**self.state.research_plan)
                    plan_details_str = json.dumps(research_plan.model_dump(), indent=2)
                except TypeError:
                    plan_details_str = json.dumps(self.state.research_plan, indent=2)
            else:
                plan_details_str = json.dumps(self.state.research_plan, indent=2)
            
            # Format the initial inputs as a JSON string for template substitution
            initial_inputs_str = json.dumps(self.state.initial_inputs, indent=2)
            
            # Execute the crew with the proper template variables
            result = requirements_crew.kickoff(
                inputs={
                    "plan_details": plan_details_str,
                    "initial_inputs": initial_inputs_str
                }
            )
            
            # Process the result into a ResearchPlan Pydantic model
            if isinstance(result, str):
                try:
                    # Try to parse as JSON first
                    plan_dict = json.loads(result)
                    validated_plan = ResearchPlan(**plan_dict)
                    self.state.validated_plan = validated_plan.model_dump()
                except (json.JSONDecodeError, TypeError):
                    print(f"Warning: Failed to parse validated plan output as JSON: {result}")
                    self.state.validated_plan = {"raw_output": result}
            elif isinstance(result, dict):
                try:
                    validated_plan = ResearchPlan(**result)
                    self.state.validated_plan = validated_plan.model_dump()
                except TypeError as e:
                    print(f"Warning: Failed to create ResearchPlan from dict: {e}")
                    self.state.validated_plan = result
            elif isinstance(result, ResearchPlan):
                self.state.validated_plan = result.model_dump()
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
        
        # Scan web sources
        try:
            # Execute the research crew with the validated plan for web sources
            inputs = {
                "validated_plan": self.state.validated_plan,
                "source_type": "web",
                **self.state.model_dump(mode='json')
            }
            
            web_result = ResearchCrew().crew().kickoff(
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
            
            doc_result = ResearchCrew().crew().kickoff(
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
        try:
            # Execute the research crew with the scan results
            inputs = {
                "web_findings": self.state.web_findings,
                "doc_findings": self.state.document_findings,
                **self.state.model_dump(mode='json')
            }
            
            result = ResearchCrew().crew().kickoff(
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
        """Reviews the preliminary findings using the Research Crew."""
        print("--- Flow Step: Reviewing Findings (Research Crew) ---")
        try:
            # Execute the research crew with the synthesized findings
            inputs = {
                "synthesized_data": self.state.synthesized_forces,
                **self.state.model_dump(mode='json')
            }
            
            # Check if we need to handle human input for this task
            print("\n=====")
            print("## HUMAN FEEDBACK: Provide feedback on the Preliminary Findings.")
            print("Please follow these guidelines:")
            print(" - If you are happy with the result, simply hit Enter without typing anything.")
            print(" - Otherwise, provide specific improvement requests.")
            print(" - You can provide multiple rounds of feedback until satisfied.")
            print("=====\n")
            
            # Get human feedback
            human_feedback = input("Your feedback (press Enter to accept): ")
            
            # Add human feedback to inputs if provided
            if human_feedback.strip():
                inputs["human_feedback"] = human_feedback
            
            result = ResearchCrew().crew().kickoff(
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
            self.state.error_message = f"Error reviewing findings: {e}"
            print(self.state.error_message)
            self.state.final_forces = self.state.synthesized_forces  # Fallback
            return "packaging"  # Still proceed to packaging with the fallback data

    # --- Packaging Crew Flow --- #
    
    @listen("packaging")
    def generate_outputs(self):
        """Generates the markdown report and table using the Packaging Crew."""
        print("--- Flow Step: Generating Outputs (Packaging Crew) ---")
        
        # Generate markdown report
        try:
            # Execute the packaging crew with the final forces for report
            inputs = {
                "identified_forces": self.state.final_forces,
                "output_type": "report",
                **self.state.model_dump(mode='json')
            }
            
            report_result = PackagingCrew().crew().kickoff(
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
            
            table_result = PackagingCrew().crew().kickoff(
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
        try:
            # Execute the packaging crew with all outputs
            inputs = {
                "identified_forces": self.state.final_forces,
                "markdown_report": self.state.markdown_report,
                "markdown_table": self.state.markdown_table,
                **self.state.model_dump(mode='json')
            }
            
            result = PackagingCrew().crew().kickoff(
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
        # Convert initial_inputs to MarketForceInput Pydantic model
        try:
            # If initial_inputs is already a MarketForceInput, use it directly
            if isinstance(initial_inputs, MarketForceInput):
                market_force_input = initial_inputs
            else:
                # Otherwise, create a MarketForceInput from the dictionary
                market_force_input = MarketForceInput(
                    target_industry=initial_inputs.get('target_industry'),
                    target_market=initial_inputs.get('target_market', 'Global'),
                    time_horizon=initial_inputs.get('time_horizon', '5+ years'),
                    keywords=initial_inputs.get('keywords', []),
                    sources_config=initial_inputs.get('sources_config', {}),
                    uploaded_files=initial_inputs.get('uploaded_files', [])
                )
            
            # Store the Pydantic model as initial inputs
            self._initial_inputs = market_force_input
            
            # Initialize state with model data (as dict for state compatibility)
            self.state.initial_inputs = market_force_input.model_dump()
            
            # Kickoff the flow
            final_state = self.kickoff()
            
            # Print the final state for debugging
            if final_state:
                print("\n--- Final Flow State ---")
                # Check if final_state is a string or has model_dump
                if isinstance(final_state, str):
                    print(final_state)
                else:
                    try:
                        print(json.dumps(final_state.model_dump(), indent=2))
                    except AttributeError:
                        print(f"Final state type: {type(final_state)}")
                        print(str(final_state))
            
            return final_state
        except Exception as e:
            print(f"Error in flow execution: {e}")
            import traceback
            traceback.print_exc()
            raise

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
        help='Target industry for the market scan (overrides config)'
    )
    parser.add_argument(
        '--market',
        type=str,
        help='Target market for the scan (e.g., Global, US, Europe) (overrides config)'
    )
    parser.add_argument(
        '--time-horizon',
        type=str,
        help='Time horizon for the analysis (overrides config)'
    )
    args = parser.parse_args()

    # Start with the configuration from FLOW_VARIABLES
    config_dict = FLOW_VARIABLES.copy()
    
    # Override with command-line arguments if provided
    if args.industry:
        config_dict['target_industry'] = args.industry
    if args.market:
        config_dict['target_market'] = args.market
    if args.time_horizon:
        config_dict['time_horizon'] = args.time_horizon

    # Prepare source configuration from the config dictionary
    source_config_dict = {}
    if 'specified_sources' in config_dict:
        # Add specified sources to a custom category in source_config
        source_config_dict['custom'] = {'specified': config_dict.pop('specified_sources', [])}
    
    # Create a proper MarketForceInput Pydantic model
    try:
        market_force_input = MarketForceInput(
            target_industry=config_dict.get('target_industry'),
            target_market=config_dict.get('target_market', 'Global'),
            time_horizon=config_dict.get('time_horizon', '5+ years'),
            keywords=config_dict.get('keywords', []),
            sources_config=source_config_dict,
            uploaded_files=config_dict.get('uploaded_files', [])
        )
        
        print(f"\nInitiating flow run with initial inputs:")
        print(json.dumps(market_force_input.model_dump(), indent=2))
        print('-----------------------------------\n')
        
        # Flow Execution
        scan_flow = ScanSourcesFlow()
        final_state = scan_flow.run(initial_inputs=market_force_input)
        
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
            output_dir = config_dict.get('output_directory', 'outputs')
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            table_path = os.path.join(output_dir, f"market_forces_table_{timestamp}.md")
            report_path = os.path.join(output_dir, f"market_forces_report_{timestamp}.md")
            try:
                with open(table_path, "w", encoding='utf-8') as f:
                    f.write(final_state.markdown_table)
                with open(report_path, "w", encoding='utf-8') as f:
                    f.write(final_state.markdown_report)
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
