import os
import json
import sys
import warnings
import traceback
from datetime import datetime
from typing import Dict, Any
                
from pydantic import BaseModel, PydanticDeprecatedSince20

# Suppress specific pydantic deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)

from crewai.flow import Flow, listen, start, router
from scan_sources.crews.research_crew.research_crew import ResearchCrew

# Import variables from config.py
from scan_sources.config import USER_INPUT_VARIABLES, ALL_SOURCES_FLATTENED, SOURCES_FUTURISTS

# # Import Pydantic models
# from scan_sources.models import RawMarketForce

# # Define the new input model for the research crew
# class ResearchCrewInput(BaseModel):
#     market_force: RawMarketForce
#     user_variables: Dict[str, Any]

class ScanFlow(Flow):
    def __init__(self):
        super().__init__()
        self.user_input_variables = {
            **USER_INPUT_VARIABLES,
            **ALL_SOURCES_FLATTENED
        }

    # RESEARCH_STRATEGY_FILE = "research_strategy.json"
    # RESEARCH_PLAN_FILE = "research_plan.json"
    # APPROVED_RESEARCH_PLAN_FILE = "approved_research_plan.json"

    @start()
    def run(self):
        """
        Run the crew.
        """
        inputs = {
            'topic': 'Coal Mining',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'sources_futurists': SOURCES_FUTURISTS
        }
        ResearchCrew().crew().kickoff(inputs=inputs).pydantic
        return "Research completed"
    
    # def generate_futureist_content(self):
    #     return ResearchCrew().crew().kickoff(self.user_input_variables)

#     def develop_research_plan(self):
#         """Initial method to check for plan"""
#         if os.path.exists(self.APPROVED_RESEARCH_PLAN_FILE):
#             print("Found approved research plan, resuming...")
#             with open(self.APPROVED_RESEARCH_PLAN_FILE, "r") as f:
#                 plan_data = f.read()
#                 research_plan = Market_Force_Plan.model_validate_json(plan_data)
#             return research_plan
#         elif os.path.exists(self.RESEARCH_PLAN_FILE):
#             print("Found plan waiting for review, resuming review...")
#             return "awaiting_review"
#         print("Creating new research plan...")
#         return "create_new_research_plan"

#     @router(develop_research_plan)
#     def handle_research_plan_flow(self, result):
#         """Route based on initial plan check"""
#         if isinstance(result, Market_Force_Plan):
#             # We have an approved plan, proceed to research
#             return "research_plan_approved"
#         elif result == "awaiting_review":
#             # Plan is waiting for review
#             return "awaiting_review"
#         elif result == "create_new_research_plan":
#             # Need to create a new plan
#             return "create_new_research_plan"
#         return None

#     @listen("create_new_research_plan")
#     def create_new_research_plan(self):
#         """Create a new research plan using the plan crew"""
#         # Create and run the planning crew
#         research_plan = PlanCrew().crew().kickoff(self.user_input_variables).pydantic

#         # Save plan to review file
#         with open(self.RESEARCH_PLAN_FILE, "w") as f:
#             f.write(research_plan.model_dump_json(indent=2))
#         print("Plan saved for review")
#         # Return a string to signal we're awaiting review
#         return "awaiting_review"

#     @listen("awaiting_review")
#     def wait_for_approval(self):
#         """Wait for user approval of the research plan"""
#         if sys.stdin.isatty():
#             print("\nResearch plan ready for review.")
#             print(f"The plan is saved at: {self.RESEARCH_PLAN_FILE}")
#             print("Would you like to approve this plan? (y/n)")
#             approval = input().strip().lower()
#             if approval == 'y':
#                 # Copy the research plan file to the approved file
#                 with open(self.RESEARCH_PLAN_FILE, "r") as f:
#                     plan_data = f.read()
#                 with open(self.APPROVED_RESEARCH_PLAN_FILE, "w") as f:
#                     f.write(plan_data)
#                 print("Plan approved! Continuing with research...")
#                 self.resume_flow_with_approved_plan()
#                 return None
#             else:
#                 print("Plan not approved. Exiting flow.")
#                 return None
#         else:
#             print("Plan ready for review. Waiting for approval via web interface...")
#             return None

#     @listen("research_plan_approved")
#     def research_market_forces(self):
#         """Research each market force of the plan"""
#         # Load the approved plan
#         with open(self.APPROVED_RESEARCH_PLAN_FILE, "r") as f:
#             plan_data = f.read()
#             research_plan = Market_Force_Plan.model_validate_json(plan_data)

#         # Create directory for market force outputs
#         market_force_dir = os.path.join("outputs", "market_forces")
#         os.makedirs(market_force_dir, exist_ok=True)

#         final_content = []
#         for i, market_force in enumerate(research_plan.market_forces, 1):
#             # Ensure market_force is a Market_Force instance if needed
#             if not isinstance(market_force, Market_Force):
#                 market_force = Market_Force.model_validate(market_force)
            
#             # Get market_force id and short description directly from the model
#             market_force_id = market_force.market_force_id or i
#             subtitle = market_force.market_force_short_description or f"Market_Force_{i}"
            
#             # Create a more robust filename with market_force id
#             market_force_file = f"{market_force_id}_{subtitle.replace(' ', '_')}.md"
#             market_force_path = os.path.join(market_force_dir, market_force_file)

#             print(f"Processing market force {market_force_id}: {subtitle}")

#             # Check if this market force has already been processed
#             if os.path.exists(market_force_path):
#                 print(f"Market force {market_force_id} already processed, loading from file")
#                 with open(market_force_path, "r") as f:
#                     market_force_content = f.read()
#                     final_content.append(market_force_content)
#                 continue

#             try:
#                 # Debugging prints
#                 print(f"Debug - user_input_variables type: {type(self.user_input_variables)}")
#                 print(f"Debug - user_input_variables keys: {list(self.user_input_variables.keys())}")
                
#                 print(f"Running research crew for market force {market_force_id}")
#                 # Create a flat dictionary with both user variables and market force attributes
#                 flat_inputs = {}
#                 flat_inputs.update(self.user_input_variables)  # Add the user inputs
#                 flat_inputs.update(market_force.model_dump())  # Add all market force attributes at top level
#                 # flat_inputs.update(internet_research.model_dump())  # Add internet research
#                 # flat_inputs.update(research_finding.model_dump())  # Add research finding
#                 # flat_inputs.update(base_research_output.model_dump())  # Add base research output


#                 # Use the new approach to kickoff the research crew with flat_inputs
#                 result = ResearchCrew().crew().kickoff(flat_inputs).pydantic
#                 # Add to final content and save to file
#                 final_content.append(result)
#                 with open(market_force_path, "w") as f:
#                     f.write(result)
                    
#                 print(f"Market force {market_force_id} completed and saved")
#             except Exception as e:
#                 print(f"Error processing market force {market_force_id} ({subtitle}): {e}")
#                 # Print the full stack trace to find where exactly the error occurs
#                 traceback.print_exc()
#                 print("Moving to next market force...")
#                 continue

#         print(f"Completed processing {len(final_content)} out of {len(research_plan.market_forces)} market forces")
#         return final_content

#     @listen(research_market_forces)
#     def save_to_markdown(self, content):
#         """Save the research content to a markdown file"""
#         output_dir = "outputs"
#         os.makedirs(output_dir, exist_ok=True)

#         industry = self.user_input_variables.get("industry")
#         file_name = f"Market_Force_{industry}.md".replace(" ", "_")
#         output_path = os.path.join(output_dir, file_name)

#         with open(output_path, "w") as f:
#             f.write("# Market Forces and Tsunamis of Change\n\n")
#             f.write(f"## Industry Focus: {industry}\n\n")
#             f.write("*A Futureworld & NexusPlus Research Report*\n\n")

#             for market_force in content:
#                 f.write(market_force)
#                 f.write("\n\n")

#             f.write("\n\n---\n\n")
#             f.write("  Futureworld & NexusPlus - All rights reserved\n")
    
#         return output_path

#     def get_research_plan_for_review(self):
#         """Get the current research plan for review
        
#         This is an external entry point called from the API to retrieve the research plan for user review.
#         """
#         if os.path.exists(self.RESEARCH_PLAN_FILE):
#             with open(self.RESEARCH_PLAN_FILE, "r") as f:
#                 return f.read()
#         return None

#     def update_research_plan_from_user_edits(self, edited_plan_json):
#         """Update the research plan with user edits and mark as approved
        
#         This is an external entry point called from the API when the user approves the research plan.
#         After updating the plan, it triggers the flow to continue by returning "research_plan_approved".
#         """
#         try:
#             # Parse the edited plan
#             edited_plan = Market_Force_Plan.model_validate_json(edited_plan_json)
            
#             # Save the edited plan to the approved file
#             with open(self.APPROVED_RESEARCH_PLAN_FILE, "w") as f:
#                 f.write(edited_plan.model_dump_json(indent=2))
#             print("Plan updated with user edits and approved")
            
#             # Resume the flow with the approved plan
#             self.resume_flow_with_approved_plan()
#             return True
#         except Exception as e:
#             print(f"Error updating research plan: {e}")
#             return False

#     def resume_flow_with_approved_plan(self):
#         """Resume the flow with the approved plan
        
#         This is an external entry point that resumes the flow after plan approval.
#         It emits the "research_plan_approved" event which triggers the research_sections method.
#         """
#         # Create a new instance of the flow to continue from where we left off
#         flow_instance = ScanFlow()
#         # Emit the "research_plan_approved" event to trigger further flow actions
#         flow_instance.emit("research_plan_approved")
#         return "Flow resumed with approved plan"

# External functions to kickoff and plot the flow
def kickoff():
    scan_flow = ScanFlow()
    scan_flow.kickoff()


def plot():
    scan_flow = ScanFlow()
    scan_flow.plot()


if __name__ == "__main__":
    kickoff()
