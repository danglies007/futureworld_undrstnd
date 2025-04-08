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
            
            # Handle CrewOutput object specifically
            if hasattr(result, 'raw_output'):
                result = result.raw_output
            
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
            
            # Handle CrewOutput object specifically
            if hasattr(result, 'raw_output'):
                result = result.raw_output
            
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
        
        # Get the research plan
        validated_plan = self.state.validated_plan
        if not validated_plan:
            self.state.error_message = "No validated research plan found."
            return "error"
        
        # Parse the validated plan using the ResearchPlan model
        from scan_sources.utilities.models import ResearchPlan
        
        try:
            # Convert the validated plan to a ResearchPlan object
            research_plan = ResearchPlan.from_crew_output(validated_plan)
            
            # Get the research items
            research_items = research_plan.research_items
            
            if not research_items:
                self.state.error_message = "No research items found in the validated plan."
                return "error"
            
            print(f"Processing {len(research_items)} research items from the plan")
            
            # Initialize findings lists if they don't exist
            if not hasattr(self.state, 'web_findings') or not self.state.web_findings:
                self.state.web_findings = []
            if not hasattr(self.state, 'document_findings') or not self.state.document_findings:
                self.state.document_findings = []
            
            # Process each research item one by one
            all_web_findings = []
            all_document_findings = []
            
            for index, item in enumerate(research_items):
                print(f"\nProcessing research item {index + 1}/{len(research_items)}: {item.topic}")
                
                # Scan web sources for this item
                try:
                    # Execute the research crew with the validated plan for web sources
                    inputs = {
                        "validated_plan": research_plan.model_dump(),
                        "source_type": "web",
                        "current_item_index": index,
                        "all_research_items": [item.model_dump() for item in research_items],
                        "current_research_item": item.model_dump(),
                        "all_web_findings": all_web_findings,
                        "all_document_findings": all_document_findings,
                        **self.state.model_dump(mode='json')
                    }
                    
                    # Create a new research crew for each item to avoid state conflicts
                    from scan_sources.crews.research_crew.research_crew import ResearchCrew
                    web_crew = ResearchCrew()
                    web_result = web_crew.crew().kickoff(inputs=inputs)
                    
                    # Extract web findings from the result
                    if web_result and isinstance(web_result, dict) and 'web_findings' in web_result:
                        web_findings = web_result['web_findings']
                        all_web_findings.extend(web_findings)
                        print(f"Found {len(web_findings)} web findings for item {index + 1}")
                    else:
                        print(f"No web findings for item {index + 1}")
                    
                    # Scan document sources for this item
                    inputs = {
                        "validated_plan": research_plan.model_dump(),
                        "source_type": "document",
                        "current_item_index": index,
                        "all_research_items": [item.model_dump() for item in research_items],
                        "current_research_item": item.model_dump(),
                        "all_web_findings": all_web_findings,
                        "all_document_findings": all_document_findings,
                        **self.state.model_dump(mode='json')
                    }
                    
                    # Create a new research crew for document scanning
                    doc_crew = ResearchCrew()
                    doc_result = doc_crew.crew().kickoff(inputs=inputs)
                    
                    # Extract document findings from the result
                    if doc_result and isinstance(doc_result, dict) and 'document_findings' in doc_result:
                        doc_findings = doc_result['document_findings']
                        all_document_findings.extend(doc_findings)
                        print(f"Found {len(doc_findings)} document findings for item {index + 1}")
                    else:
                        print(f"No document findings for item {index + 1}")
                    
                except Exception as e:
                    print(f"Error processing research item {index + 1}: {e}")
                    # Continue with the next item
            
            # Store all findings in the state
            self.state.web_findings = all_web_findings
            self.state.document_findings = all_document_findings
            
            # Synthesize findings
            try:
                # Execute the research crew for synthesis
                inputs = {
                    "validated_plan": research_plan.model_dump(),
                    "web_findings": all_web_findings,
                    "doc_findings": all_document_findings,
                    **self.state.model_dump(mode='json')
                }
                
                # Create a new research crew for synthesis
                synthesis_crew = ResearchCrew()
                synthesis_result = synthesis_crew.crew().kickoff(inputs=inputs)
                
                # Extract synthesized forces from the result
                if synthesis_result and isinstance(synthesis_result, dict) and 'synthesized_forces' in synthesis_result:
                    self.state.synthesized_forces = synthesis_result['synthesized_forces']
                    print(f"Synthesized {len(self.state.synthesized_forces)} forces")
                else:
                    print("No synthesized forces found")
                
                # Review findings with human input if configured
                inputs = {
                    "validated_plan": research_plan.model_dump(),
                    "synthesized_forces": self.state.synthesized_forces,
                    **self.state.model_dump(mode='json')
                }
                
                # Create a new research crew for review
                review_crew = ResearchCrew()
                review_result = review_crew.crew().kickoff(inputs=inputs)
                
                # Extract final forces from the result
                if review_result and isinstance(review_result, dict) and 'final_forces' in review_result:
                    self.state.final_forces = review_result['final_forces']
                    print(f"Finalized {len(self.state.final_forces)} forces after review")
                else:
                    # If no final forces, use the synthesized forces
                    self.state.final_forces = self.state.synthesized_forces
                    print("Using synthesized forces as final forces (no review changes)")
                
            except Exception as e:
                print(f"Error in synthesis or review: {e}")
                # Continue with the flow
            
            return "success"
            
        except Exception as e:
            print(f"Error processing validated plan: {e}")
            self.state.error_message = f"Error processing validated plan: {e}"
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
            
            # Handle CrewOutput object specifically
            if hasattr(result, 'raw_output'):
                result = result.raw_output
            
            if isinstance(result, str):
                try:
                    self.state.synthesized_forces = json.loads(result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse synthesized forces as JSON: {result}")
                    self.state.synthesized_forces = [{"raw_output": result}]
            elif isinstance(result, list):
                self.state.synthesized_forces = result
            else:
                print(f"Warning: Unexpected synthesized forces output type: {type(result)}")
                self.state.synthesized_forces = [{"raw_output": str(result)}]
            
            print(f"Synthesized {len(self.state.synthesized_forces)} market forces.")
            
            # Return the crew name to route to the next step
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
            
            # Handle CrewOutput object specifically
            if hasattr(result, 'raw_output'):
                result = result.raw_output
            
            if isinstance(result, str):
                try:
                    self.state.final_forces = json.loads(result)
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse final forces as JSON: {result}")
                    self.state.final_forces = [{"raw_output": result}]
            elif isinstance(result, list):
                self.state.final_forces = result
            else:
                print(f"Warning: Unexpected final forces output type: {type(result)}")
                self.state.final_forces = [{"raw_output": str(result)}]
            
            print(f"Final Forces Count: {len(self.state.final_forces)}")
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
        try:
            # Execute the packaging crew with the final forces
            inputs = {
                "final_forces": self.state.final_forces,
                **self.state.model_dump(mode='json')
            }
            
            result = PackagingCrew().crew().kickoff(
                inputs=inputs
            )
            
            # Handle CrewOutput object specifically
            if hasattr(result, 'raw_output'):
                result = result.raw_output
            
            if isinstance(result, str):
                try:
                    output_dict = json.loads(result)
                    self.state.markdown_report = output_dict.get('report', '')
                    self.state.markdown_table = output_dict.get('table', '')
                    self.state.final_output = output_dict
                except json.JSONDecodeError:
                    print(f"Warning: Failed to parse packaging output as JSON: {result}")
                    self.state.markdown_report = result
                    self.state.final_output = {"raw_output": result}
            elif isinstance(result, dict):
                self.state.markdown_report = result.get('report', '')
                self.state.markdown_table = result.get('table', '')
                self.state.final_output = result
            else:
                print(f"Warning: Unexpected packaging output type: {type(result)}")
                self.state.markdown_report = str(result)
                self.state.final_output = {"raw_output": str(result)}
            
            # Write the report to a file
            try:
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                report_file = f"market_forces_report_{timestamp}.md"
                report_path = os.path.join('outputs', report_file)
                
                # Ensure the outputs directory exists
                os.makedirs('outputs', exist_ok=True)
                
                with open(report_path, 'w') as f:
                    f.write(self.state.markdown_report)
                
                print(f"Report saved to: {report_path}")
            except Exception as e:
                print(f"Error saving report: {e}")
            
            return "complete"
        except Exception as e:
            self.state.error_message = f"Error generating outputs: {e}"
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
            final_result = self.kickoff()
            
            # Print the final state for debugging
            print("\n--- Final Flow State ---")
            if isinstance(final_result, str):
                print(final_result)
                # Return the actual state object, not the string
                return self.state
            else:
                try:
                    print(json.dumps(final_result.model_dump(), indent=2))
                except AttributeError:
                    print(f"Final state type: {type(final_result)}")
                    print(str(final_result))
            
            return final_result if not isinstance(final_result, str) else self.state
        except Exception as e:
            print(f"Error in flow execution: {e}")
            import traceback
            traceback.print_exc()
            # Return the state even if there's an error
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
        if isinstance(final_state, str):
            print(f"Flow returned a string value: {final_state}")
            # Try to access the flow's state directly since final_state is just a string
            flow_state = scan_flow.state
            if hasattr(flow_state, 'error_message') and flow_state.error_message:
                print(f"Flow finished with an error: {flow_state.error_message}")
            elif hasattr(flow_state, 'final_output') and flow_state.final_output:
                print("Final Result (from Flow State):")
                print(flow_state.final_output)
                
                # Save outputs if they exist
                if hasattr(flow_state, 'markdown_table') and hasattr(flow_state, 'markdown_report'):
                    output_dir = config_dict.get('output_directory', 'outputs')
                    os.makedirs(output_dir, exist_ok=True)
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    table_path = os.path.join(output_dir, f"market_forces_table_{timestamp}.md")
                    report_path = os.path.join(output_dir, f"market_forces_report_{timestamp}.md")
                    try:
                        with open(table_path, "w", encoding='utf-8') as f:
                            f.write(flow_state.markdown_table)
                        with open(report_path, "w", encoding='utf-8') as f:
                            f.write(flow_state.markdown_report)
                        print(f"\nMarkdown table and report saved to '{output_dir}' directory.")
                    except Exception as e:
                        print(f"\nError saving output files: {e}")
            else:
                print("Flow completed, but no final output was generated in the state.")
        elif hasattr(final_state, 'error_message') and final_state.error_message:
            print(f"Flow finished with an error: {final_state.error_message}")
        elif hasattr(final_state, 'final_output') and final_state.final_output:
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
