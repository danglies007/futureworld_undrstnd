import os

from datetime import datetime
from pydantic import BaseModel

# Ignore warnings
import warnings
from pydantic import PydanticDeprecatedSince20

# Suppress specific pydantic deprecation warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
warnings.filterwarnings("ignore", category=PydanticDeprecatedSince20)


from crewai.flow import Flow, listen, start, router 

from scan_sources.crews.plan_crew.plan_crew import PlanCrew
from scan_sources.crews.research_crew.research_crew import ResearchCrew

# Import variables from config.py
from scan_sources.config import USER_INPUT_VARIABLES, ALL_SOURCES_FLATTENED

# Import Pydantic models
from scan_sources.models import (
    Market_Force,
    Market_Force_Plan
)

class ScanFlow(Flow):
    def __init__(self):
        super().__init__()
        self.user_input_variables = {
            **USER_INPUT_VARIABLES,
            **ALL_SOURCES_FLATTENED
        }

    RESEARCH_STRATEGY_FILE = "research_strategy.json"
    RESEARCH_PLAN_FILE = "research_plan.json"
    APPROVED_RESEARCH_PLAN_FILE = "approved_research_plan.json"

    @start()
    def develop_research_plan(self):
        """Initial method to check for plan"""
        if os.path.exists(self.APPROVED_RESEARCH_PLAN_FILE):
            print("Found approved research plan, resuming...")
            with open(self.APPROVED_RESEARCH_PLAN_FILE, "r") as f:
                plan_data = f.read()
                plan = Market_Force_Plan.model_validate_json(plan_data)
            return plan
        elif os.path.exists(self.RESEARCH_PLAN_FILE):
            print("Found plan waiting for review, resuming review...")
            return "awaiting_review"
        print("Creating new research plan...")
        return "create_new_research_plan"

    @router(develop_research_plan)
    def handle_research_plan_flow(self, result):
        """Route based on initial plan check"""
        if isinstance(result, Market_Force_Plan):
            # We have an approved plan, proceed to research
            return "research_plan_approved"
        elif result == "awaiting_review":
            # Plan is waiting for review
            return "awaiting_review"
        elif result == "create_new_research_plan":
            # Need to create a new plan
            return "create_new_research_plan"
        return None

    @listen("create_new_research_plan")
    def create_new_research_plan(self):
        """Create a new research plan using the plan crew"""
        
        # Create and run the planning crew
        plan_crew = PlanCrew()
        crew_output = plan_crew.crew().kickoff(self.user_input_variables)

        # Check if pydantic output is available
        if hasattr(crew_output, 'pydantic') and crew_output.pydantic is not None:
            plan = crew_output.pydantic
        else:
            # Create a basic plan from the raw output if needed
            raw_output = crew_output.raw
            print("Creating plan from raw output")
            # This is a simplified fallback and may need adjustment based on the actual output
            plan = Market_Force_Plan(market_forces=[
                {
                    "market_force_id": 1,
                    "market_force_short_description": "Market force short description",
                    "market_force_long_description": "Market force long description",
                    "research_objectives": ["Basic research requirement"],
                    "content_examples": ["Suggested search terms"],
                    "minimum_sources": ["Sources which must be searched and or scrapped"],
                    "source_priority": ["Priortities sources and rationale"],
                    "quality_criteria": ["criteria against which sources and insights are evaluated"],
                    "integration_approach": ["Approach for integrating sources and insights"]
                }
            ])

        # Save plan to review file
        with open(self.RESEARCH_PLAN_FILE, "w") as f:
            f.write(plan.model_dump_json(indent=2))

        # Save the plan to a markdown file for review
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)

        # Create a timestamped filename for the plan
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        research_plan_md_file = f"research_plan_{timestamp}.md"
        research_plan_md_path = os.path.join(output_dir, research_plan_md_file)
        
        # Write the plan to a markdown file
        with open(research_plan_md_path, "w") as f:
            f.write(f"# Research Plan for {self.user_input_variables.get('industry')}\n\n")
            f.write(f"## Company: {self.user_input_variables.get('company_short')}\n\n")
            f.write("### Plan Market Forces\n\n")
            
            for i, market_force in enumerate(plan.market_forces, 1):
                market_force_dict = market_force
                if not isinstance(market_force, dict):
                    market_force_dict = market_force.model_dump()
                
                f.write(f"#### Market Force {market_force_dict.get('market_force_id', i)}: {market_force_dict.get('market_force_short_description', 'Untitled') }\n\n")
                f.write(f"**Research Objectives**: {market_force_dict.get('research_objectives', 'N/A')}\n\n")
                
                # Write sources if available
                sources = market_force_dict.get('minimum_sources', [])
                if sources:
                    f.write("**Sources**:\n")
                    for source in sources:
                        f.write(f"- {source}\n")
                    f.write("\n")
                
                # Write content outline if available
                content_examples = market_force_dict.get('content_examples', [])
                if content_examples:
                    f.write("**Content Examples**:\n")
                    for item in content_examples:
                        f.write(f"- {item}\n")
                    f.write("\n")
        
        print(f"Plan saved to {research_plan_md_path} for review")
        
        # The flow will now transition to awaiting_review
        # We emit the event instead of returning a string to ensure proper transition
        self.emit("awaiting_review")
        return None

    @listen("awaiting_review")
    def wait_for_approval(self):
        """Wait for user approval of the researchplan"""
        return None

    @listen("research_plan_approved")
    def research_market_forces(self):
        """Research each market force of the plan"""
        # Load the approved plan
        with open(self.APPROVED_RESEARCH_PLAN_FILE, "r") as f:
            plan_data = f.read()
            plan = Market_Force_Plan.model_validate_json(plan_data)

        # Create directory for section outputs
        market_force_dir = os.path.join("outputs", "market_forces")
        os.makedirs(market_force_dir, exist_ok=True)

        final_content = []
        for i, market_force in enumerate(plan.market_forces, 1):
            # Get market_force as dictionary if it's not already
            market_force_dict = market_force
            if not isinstance(market_force, dict):
                market_force_dict = market_force.model_dump()
            
            # Check if market_force_id exists, if not, add it using the index
            if 'market_force_id' not in market_force_dict or not market_force_dict['market_force_id']:
                market_force_dict['market_force_id'] = i
                print(f"Assigned market_force id {i} to market_force: {market_force_dict.get('market_force_short_description', 'Untitled')}")
            
            # Get market_force id and short description safely
            market_force_id = market_force_dict.get('market_force_id', i)
            subtitle = market_force_dict.get('market_force_short_description', f"Market_Force_{i}")
            
            # Create a more robust filename with market_force id
            market_force_file = f"{market_force_id}_{subtitle.replace(' ', '_')}.md"
            market_force_path = os.path.join(market_force_dir, market_force_file)

            print(f"Processing section {market_force_id}: {subtitle}")

            # Check if this section has already been processed
            if os.path.exists(market_force_path):
                print(f"Section {market_force_id} already processed, loading from file")
                with open(market_force_path, "r") as f:
                    market_force_content = f.read()
                    final_content.append(market_force_content)
                continue

            # Prepare input for the research crew
            writer_inputs = self.user_input_variables.copy()
            writer_inputs['market_force'] = market_force_dict
            
            try:
                print(f"Running research crew for section {market_force_id}")
                research_crew = ResearchCrew()
                result = research_crew.crew().kickoff(writer_inputs).raw
                
                # Add to final content and save to file
                final_content.append(result)
                with open(market_force_path, "w") as f:
                    f.write(result)
                    
                print(f"Section {market_force_id} completed and saved")
            except Exception as e:
                print(f"Error processing section {market_force_id} ({subtitle}): {e}")
                # Continue with next section instead of returning early
                print(f"Moving to next section...")
                continue

        # Return all processed sections, even if some failed
        print(f"Completed processing {len(final_content)} out of {len(plan.market_forces)} market forces")
        return final_content

    @listen(research_market_forces)
    def save_to_markdown(self, content):
        """Save the research content to a markdown file"""

        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)

        industry = self.user_input_variables.get("industry")
        file_name = f"Market_Force_{industry}.md".replace(" ", "_")

        output_path = os.path.join(output_dir, file_name)

        with open(output_path, "w") as f:
            f.write("# Market Forces and Tsunamis of Change\n\n")
            f.write(f"## Industry Focus: {sector}\n\n")
            f.write("*A Futureworld & NexusPlus Research Report*\n\n")

            for market_force in content:
                f.write(market_force)
                f.write("\n\n")

            f.write("\n\n---\n\n")
            f.write("  Futureworld & NexusPlus - All rights reserved\n")
    
        return output_path

    def get_research_plan_for_review(self):
        """Get the current research plan for review
        
        This is an external entry point called from the API to retrieve the research plan for user review.
        """
        if os.path.exists(self.RESEARCH_PLAN_FILE):
            with open(self.RESEARCH_PLAN_FILE, "r") as f:
                return f.read()
        return None

    def update_research_plan_from_user_edits(self, edited_plan_json):
        """Update the research plan with user edits and mark as approved
        
        This is an external entry point called from the API when the user approves the research plan.
        After updating the plan, it triggers the flow to continue by returning "research_plan_approved".
        """
        try:
            # Parse the edited plan
            edited_plan = Market_Force_Plan.model_validate_json(edited_plan_json)
            
            # Save the edited plan to the approved file
            with open(self.APPROVED_RESEARCH_PLAN_FILE, "w") as f:
                f.write(edited_plan.model_dump_json(indent=2))
            print("Plan updated with user edits and approved")
            
            # Resume the flow with the approved plan
            self.resume_flow_with_approved_plan()
            return True
        except Exception as e:
            print(f"Error updating research plan: {e}")
            return False

    def resume_flow_with_approved_plan(self):
        """Resume the flow with the approved plan
        
        This is an external entry point that resumes the flow after plan approval.
        It emits the "research_plan_approved" event which triggers the research_sections method.
        """
        
        # Create a new instance of the flow to continue from where we left off
        flow_instance = ScanFlow()
        
        # Emit the "research_plan_approved" event to trigger the research_sections method
        # This will continue the flow from the approved plan to research and report generation
        flow_instance.emit("research_plan_approved")
        
        return "Flow resumed with approved plan"

    # External API methods that interact with the flow
    # These methods are called from outside the flow to provide user interaction points

def kickoff():
    scan_flow = ScanFlow()
    scan_flow.kickoff()


def plot():
    scan_flow = ScanFlow()
    scan_flow.plot()


if __name__ == "__main__":
    kickoff()