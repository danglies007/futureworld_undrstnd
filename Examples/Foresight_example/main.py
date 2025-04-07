#!/usr/bin/env python

import os
import json
import sys
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router
from datetime import datetime
import pytz
import agentops
from .config import FLOW_VARIABLES
from .logging import setup_logging, backup_log_file

# Initialize logging
logger = setup_logging()

# Start agentops with session management
# agentops.init(instrument_llm_calls=True, default_tags=[FLOW_VARIABLES.get("topic")])

# Import Crews
from .crews.plan_crew.plan_crew import PlanCrew, Plan
from .crews.research_crew.research_crew import ResearchCrew

# Import variables from config.py
from .config import FLOW_VARIABLES

class ForesightFlow(Flow):
    input_variables = FLOW_VARIABLES
    sector = input_variables.get("sector")
    PLAN_FILE = "saved_plan.json"
    PLAN_REVIEW_FILE = "plan_for_review.json"
    PLAN_APPROVED_FILE = "plan_approved.json"
    status_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
                               'status.json')

    def _update_status(self, status: str, message: str, agent: str = None, task: str = None, 
                      flow_state: str = None, progress: int = None, subtasks: list = None):
        """Update the status file with current progress"""
        # Get the local timezone
        local_tz = datetime.now().astimezone().tzinfo
        
        status_data = {
            "status": status,
            "message": message,
            "timestamp": datetime.now().astimezone(local_tz).isoformat(),
            "agent": agent,
            "task": task
        }
        
        # Add flow state information if provided
        if flow_state:
            status_data["flow_state"] = flow_state
            
        # Add progress percentage if provided
        if progress is not None:
            status_data["progress"] = progress
            
        # Add subtasks if provided
        if subtasks:
            status_data["subtasks"] = subtasks
        
        try:
            with open(self.status_file, 'w') as f:
                json.dump(status_data, f, indent=2)
            print(f"Status updated: {status} - {message}")
        except Exception as e:
            print(f"Error updating status: {e}")

    @start()
    def develop_plan(self):
        """Initial method to check for plan"""
        self._update_status("initializing", "Setting up Foresight flow", flow_state="develop_plan", progress=5)
        if os.path.exists(self.PLAN_APPROVED_FILE):
            print("Found approved Foresight plan, resuming...")
            with open(self.PLAN_APPROVED_FILE, "r") as f:
                plan_data = f.read()
                plan = Plan.model_validate_json(plan_data)
            return plan
        elif os.path.exists(self.PLAN_REVIEW_FILE):
            print("Found plan waiting for review, resuming review...")
            self._update_status("awaiting_review", "Plan is ready for review", flow_state="awaiting_review", progress=20)
            return "awaiting_review"
        print("Creating new Foresight plan...")
        return "create_new_plan"

    @router(develop_plan)
    def handle_plan_flow(self, result):
        """Route based on initial plan check"""
        if isinstance(result, Plan):
            # We have an approved plan, proceed to research
            self._update_status("plan_approved", "Proceeding with approved plan", flow_state="plan_approved", progress=30)
            return "plan_approved"
        elif result == "awaiting_review":
            # Plan is waiting for review
            return "awaiting_review"
        elif result == "create_new_plan":
            # Need to create a new plan
            return "create_new_plan"
        return None

    @listen("create_new_plan")
    def create_new_plan(self):
        """Create a new plan using the plan crew"""
        # Only update status if we're not already in planning state
        # This prevents repeated status updates that might cause loops
        current_status = {}
        try:
            with open(self.status_file, 'r') as f:
                current_status = json.load(f)
        except Exception:
            pass
            
        if current_status.get('flow_state') != 'create_new_plan':
            self._update_status("planning", "Planning the foresight report structure", "PlanningAgent", "StructurePlanningTask", flow_state="create_new_plan", progress=10)
        
        # Create and run the planning crew
        plan_crew = PlanCrew()
        crew_output = plan_crew.crew().kickoff(self.input_variables)

        # Check if pydantic output is available
        if hasattr(crew_output, 'pydantic') and crew_output.pydantic is not None:
            plan = crew_output.pydantic
        else:
            # Create a basic plan from the raw output if needed
            raw_output = crew_output.raw
            print("Creating plan from raw output")
            # This is a simplified fallback and may need adjustment based on the actual output
            plan = Plan(sections=[
                {
                    "section_number": 1,
                    "subtitle": "Basic Plan Section",
                    "high_level_goal": "Analyze trends based on research",
                    "why_important": "To identify key trends and signals",
                    "sources": ["Research output"],
                    "content_outline": ["Analyze trends", "Develop insights", "Evaluate implications"]
                }
            ])

        # Save plan to review file
        with open(self.PLAN_REVIEW_FILE, "w") as f:
            f.write(plan.model_dump_json(indent=2))
        
        # Create a backup of the log file to preserve planning crew logs
        backup_log_file("plan")
        
        # Update status to indicate plan is ready for review
        self._update_status("awaiting_review", "Plan is ready for review", "PlanningAgent", "StructurePlanningTask", flow_state="awaiting_review", progress=20)
        
        # Save the plan to a markdown file for review
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)

        # Create a timestamped filename for the plan
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_md_file = f"plan_{timestamp}.md"
        plan_md_path = os.path.join(output_dir, plan_md_file)
        
        # Write the plan to a markdown file
        with open(plan_md_path, "w") as f:
            f.write(f"# Strategic Foresight Plan for {self.input_variables.get('sector')}\n\n")
            f.write(f"## Company: {self.input_variables.get('company_name')}\n\n")
            f.write("### Plan Sections\n\n")
            
            for i, section in enumerate(plan.sections, 1):
                section_dict = section
                if not isinstance(section, dict):
                    section_dict = section.model_dump()
                
                f.write(f"#### Section {section_dict.get('section_number', i)}: {section_dict.get('subtitle', 'Untitled')}\n\n")
                f.write(f"**Goal**: {section_dict.get('high_level_goal', 'N/A')}\n\n")
                f.write(f"**Why Important**: {section_dict.get('why_important', 'N/A')}\n\n")
                
                # Write sources if available
                sources = section_dict.get('sources', [])
                if sources:
                    f.write("**Sources**:\n")
                    for source in sources:
                        f.write(f"- {source}\n")
                    f.write("\n")
                
                # Write content outline if available
                content_outline = section_dict.get('content_outline', [])
                if content_outline:
                    f.write("**Content Outline**:\n")
                    for item in content_outline:
                        f.write(f"- {item}\n")
                    f.write("\n")
        
        print(f"Plan saved to {plan_md_path} for review")
        
        # The flow will now transition to awaiting_review
        # We emit the event instead of returning a string to ensure proper transition
        self.emit("awaiting_review")
        return None

    @listen("awaiting_review")
    def wait_for_approval(self):
        """Wait for user approval of the plan"""
        self._update_status("awaiting_review", "Waiting for user to review and approve the plan", flow_state="wait_for_approval", progress=25)
        print("Flow paused: Awaiting plan review from user")
        # This method doesn't return anything, effectively pausing the flow
        # The flow will be resumed by calling resume_flow_with_approved_plan externally
        return None

    @listen("plan_approved")
    def research_sections(self):
        """Research each section of the plan"""
        # Load the approved plan
        with open(self.PLAN_APPROVED_FILE, "r") as f:
            plan_data = f.read()
            plan = Plan.model_validate_json(plan_data)
            
        self._update_status("researching", "Researching for the foresight report", flow_state="research_sections", progress=40)
        print(f"Starting research for {len(plan.sections)} sections")
        
        # Create directory for section outputs
        sections_dir = os.path.join("outputs", "sections")
        os.makedirs(sections_dir, exist_ok=True)

        final_content = []
        for i, section in enumerate(plan.sections, 1):
            # Get section as dictionary if it's not already
            section_dict = section
            if not isinstance(section, dict):
                section_dict = section.model_dump()
            
            # Check if section_number exists, if not, add it using the index
            if 'section_number' not in section_dict or not section_dict['section_number']:
                section_dict['section_number'] = i
                print(f"Assigned section number {i} to section: {section_dict.get('subtitle', 'Untitled')}")
            
            # Get section number and subtitle safely
            section_number = section_dict.get('section_number', i)
            subtitle = section_dict.get('subtitle', f"Section_{i}")
            
            # Create a more robust filename with section number
            section_file = f"{section_number}_{subtitle.replace(' ', '_')}.md"
            section_path = os.path.join(sections_dir, section_file)

            print(f"Processing section {section_number}: {subtitle}")

            # Check if this section has already been processed
            if os.path.exists(section_path):
                print(f"Section {section_number} already processed, loading from file")
                with open(section_path, "r") as f:
                    section_content = f.read()
                    final_content.append(section_content)
                continue

            # Prepare input for the research crew
            writer_inputs = self.input_variables.copy()
            writer_inputs['section'] = section_dict
            
            try:
                print(f"Running research crew for section {section_number}")
                research_crew = ResearchCrew()
                result = research_crew.crew().kickoff(writer_inputs).raw
                
                # Add to final content and save to file
                final_content.append(result)
                with open(section_path, "w") as f:
                    f.write(result)
                    
                print(f"Section {section_number} completed and saved")
            except Exception as e:
                print(f"Error processing section {section_number} ({subtitle}): {e}")
                # Continue with next section instead of returning early
                print(f"Moving to next section...")
                continue

        # Return all processed sections, even if some failed
        print(f"Completed processing {len(final_content)} out of {len(plan.sections)} sections")
        self._update_status("research_complete", "Research completed, generating final report", flow_state="research_complete", progress=80)
        return final_content

    @listen(research_sections)
    def save_to_markdown(self, content):
        """Save the research content to a markdown file"""
        # Update status to indicate we're finalizing the report
        self._update_status(
            "finalizing", 
            "Compiling final report document", 
            "ReportWriter",
            "ReportCompilationTask",
            flow_state="save_to_markdown",
            progress=90
        )
        
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)

        sector = self.input_variables.get("sector")
        file_name = f"Foresight_{sector}.md".replace(" ", "_")

        output_path = os.path.join(output_dir, file_name)

        with open(output_path, "w") as f:
            f.write("# Foresight: Market Forces and Social Dynamics Shaping the Future\n\n")
            f.write(f"## Sector Focus: {sector}\n\n")
            f.write("*A NexusPlus Research Report*\n\n")

            for section in content:
                f.write(section)
                f.write("\n\n")

            f.write("\n\n---\n\n")
            f.write("  NexusPlus - All rights reserved\n")

        # Update status to indicate completion
        self._update_status(
            "complete", 
            "Foresight report generation complete", 
            "ReportWriter",
            "ReportFinalization",
            flow_state="complete",
            progress=100
        )
        
        return output_path

    # External API methods that interact with the flow
    # These methods are called from outside the flow to provide user interaction points
    
    def get_plan_for_review(self):
        """Get the current plan for review
        
        This is an external entry point called from the API to retrieve the plan for user review.
        """
        if os.path.exists(self.PLAN_REVIEW_FILE):
            with open(self.PLAN_REVIEW_FILE, "r") as f:
                return f.read()
        return None

    def update_plan_from_user_edits(self, edited_plan_json):
        """Update the plan with user edits and mark as approved
        
        This is an external entry point called from the API when the user approves the plan.
        After updating the plan, it triggers the flow to continue by returning "plan_approved".
        """
        try:
            # Parse the edited plan
            edited_plan = Plan.model_validate_json(edited_plan_json)
            
            # Save the edited plan to the approved file
            with open(self.PLAN_APPROVED_FILE, "w") as f:
                f.write(edited_plan.model_dump_json(indent=2))
            
            # Also update the review file to match
            with open(self.PLAN_REVIEW_FILE, "w") as f:
                f.write(edited_plan.model_dump_json(indent=2))
                
            # Update status to indicate plan is approved
            self._update_status("plan_approved", "Plan has been reviewed and approved", "User", "PlanReview", flow_state="plan_approved", progress=30)
            
            print("Plan updated with user edits and approved")
            
            # Resume the flow with the approved plan
            self.resume_flow_with_approved_plan()
            return True
        except Exception as e:
            print(f"Error updating plan: {e}")
            return False

    def resume_flow_with_approved_plan(self):
        """Resume the flow with the approved plan
        
        This is an external entry point that resumes the flow after plan approval.
        It emits the "plan_approved" event which triggers the research_sections method.
        """
        self._update_status("plan_approved", "Plan approved, proceeding to research", "SystemAgent", "PlanApproval", flow_state="plan_approved", progress=30)
        
        # Create a new instance of the flow to continue from where we left off
        flow_instance = ForesightFlow()
        
        # Emit the "plan_approved" event to trigger the research_sections method
        # This will continue the flow from the approved plan to research and report generation
        flow_instance.emit("plan_approved")
        
        return "Flow resumed with approved plan"

def kickoff():
    foresight_flow = ForesightFlow()
    foresight_flow.kickoff()

def plot():
    foresight_flow = ForesightFlow()
    foresight_flow.plot()

if __name__ == "__main__":
    kickoff()
