import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

def show_source_scanner():
    st.title("🔍 Source Scanner")
    
    # Initialize session state for form data
    if 'source_form_data' not in st.session_state:
        st.session_state.source_form_data = {
            'research_topic': '',
            'research_objective': '',
            'research_scope': '',
            'research_questions': '',
            'research_constraints': '',
            'sources': []
        }
    
    with st.form(key='source_scanner_form'):
        st.subheader("Research Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            research_topic = st.text_area(
                "Research Topic",
                value=st.session_state.source_form_data['research_topic'],
                help="The main topic or subject of your research"
            )
            
            research_objective = st.text_area(
                "Research Objective",
                value=st.session_state.source_form_data['research_objective'],
                help="What you aim to achieve with this research"
            )
            
            research_scope = st.text_area(
                "Research Scope",
                value=st.session_state.source_form_data['research_scope'],
                help="Boundaries and limitations of the research"
            )
        
        with col2:
            research_questions = st.text_area(
                "Key Research Questions",
                value=st.session_state.source_form_data['research_questions'],
                help="Specific questions the research should answer"
            )
            
            research_constraints = st.text_area(
                "Research Constraints",
                value=st.session_state.source_form_data['research_constraints'],
                help="Any limitations or constraints for the research"
            )
            
            sources = st.multiselect(
                "Source Types",
                options=["Academic Papers", "News Articles", "Industry Reports", "Expert Interviews", "Social Media", "Government Data"],
                default=st.session_state.source_form_data['sources']
            )
        
        submitted = st.form_submit_button("Start Analysis")
        
        if submitted:
            # Save form data to session state
            st.session_state.source_form_data = {
                'research_topic': research_topic,
                'research_objective': research_objective,
                'research_scope': research_scope,
                'research_questions': research_questions,
                'research_constraints': research_constraints,
                'sources': sources
            }
            
            # TODO: Integrate with scan_sources module
            with st.spinner("Analyzing sources... This may take a few minutes."):
                try:
                    # Placeholder for scan_sources integration
                    st.success("Analysis completed successfully!")
                    
                    # Show results
                    st.subheader("Analysis Results")
                    
                    # Placeholder for results
                    st.json({
                        "status": "success",
                        "message": "Analysis completed",
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
    
    # Display saved form data for reference
    if st.checkbox("Show current form data"):
        st.json(st.session_state.source_form_data)

# Run the page
if __name__ == "__main__":
    show_source_scanner()
