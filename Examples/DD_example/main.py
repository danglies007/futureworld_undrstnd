#!/usr/bin/env python

import os
from pydantic import BaseModel
from crewai.flow.flow import Flow, listen, start, router

# Import Crews
from .crews.plan_crew.plan_crew import PlanCrew, CompanyProfilePlan 
from .crews.company_overview_crew.company_overview_crew import CompanyOverviewCrew
from .crews.business_strategy_crew.business_strategy_crew import BusinessStrategyCrew
from .crews.competitor_analysis_crew.competitor_analysis_crew import CompetitorAnalysisCrew
from .crews.financial_analysis_crew.financial_analysis_crew import FinancialAnalysisCrew
from .crews.management_analysis_crew.management_analysis_crew import ManagementAnalysisCrew
from .crews.manda_analysis_crew.manda_analysis_crew import MandaAnalysisCrew
from .crews.final_report_crew.final_report_crew import FinalReportCrew
from .crews.research_crew.research_crew import ResearchCrew
from .crews.product_expansion_crew.product_expansion import ProductExpansionCrew


# Importing Pydantic Plan Model
from .crews.plan_crew.plan_crew import CompanyProfilePlan

# Import variables from config.py
from .config import COMPANY_PROFILES_FLOW_VARIABLES

class CompanyProfilesFlow(Flow):
    input_variables = COMPANY_PROFILES_FLOW_VARIABLES
    topic = input_variables.get("topic")
    PLAN_FILE = "saved_plan.json"

    @start()
    def develop_content_plan(self):
        """Initial method to check for plan"""
        if os.path.exists(self.PLAN_FILE):
            print("Found existing plan, resuming...")
            return "resume"
        print("Creating new plan...")
        return "create"

    @router(develop_content_plan)
    def handle_plan(self):
        """Route based on plan existence"""
        if os.path.exists(self.PLAN_FILE):
            with open(self.PLAN_FILE, "r") as f:
                return CompanyProfilePlan.model_validate_json(f.read())
        
        plan = PlanCrew().crew().kickoff(self.input_variables).pydantic
        with open(self.PLAN_FILE, "w") as f:
            f.write(plan.model_dump_json())
        return plan

    @listen(handle_plan)
    def research_company_overview_content(self, plan):
        final_content = []
        section_dir = "outputs/sections"
        os.makedirs(section_dir, exist_ok=True)

        for section in plan.sections:
            section_file = f"{section.subtitle.replace(' ', '_')}.md"
            section_path = os.path.join(section_dir, section_file)
            
            if os.path.exists(section_path):
                with open(section_path, "r") as f:
                    final_content.append(f.read())
                continue

            writer_inputs = self.input_variables.copy()
            writer_inputs['section'] = section.model_dump_json()
            try:
                result = ResearchCrew().crew().kickoff(writer_inputs).raw
                final_content.append(result)
                with open(section_path, "w") as f:
                    f.write(result)
            except Exception as e:
                print(f"Error processing section {section.subtitle}: {e}")
                return final_content

        if len(final_content) == len(plan.sections):
            try:
                os.remove(self.PLAN_FILE)
            except Exception as e:
                print(f"Warning: Could not remove plan file: {e}")

        return final_content

    @listen(research_company_overview_content)
    def save_to_markdown(self, content):
        output_dir = "outputs"
        os.makedirs(output_dir, exist_ok=True)
        
        topic = self.input_variables.get("topic")
        audience_level = self.input_variables.get("audience_level")
        company_short = self.input_variables.get("company_short")
        file_name = f"{company_short}_{topic}.md".replace(" ", "_")
        
        output_path = os.path.join(output_dir, file_name)
        
        with open(output_path, "w") as f:
            for section in content:
                f.write(section)
                f.write("\n\n")

def kickoff():
    company_profiles_flow = CompanyProfilesFlow()
    company_profiles_flow.kickoff()

def plot():
    company_profiles_flow = CompanyProfilesFlow()
    company_profiles_flow.plot()

if __name__ == "__main__":
    kickoff()