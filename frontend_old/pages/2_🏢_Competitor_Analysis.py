import streamlit as st
import json
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path to import modules
sys.path.append(str(Path(__file__).parent.parent.parent))

def show_competitor_analysis():
    st.title("🏢 Competitor Analysis")
    
    # Initialize session state for form data
    if 'competitor_form_data' not in st.session_state:
        st.session_state.competitor_form_data = {
            'company_name': '',
            'industry': '',
            'competitors': [],
            'analysis_focus': [],
            'timeframe': '1 year',
            'additional_notes': ''
        }
    
    with st.form(key='competitor_analysis_form'):
        st.subheader("Analysis Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input(
                "Company Name",
                value=st.session_state.competitor_form_data['company_name'],
                help="The name of the company to analyze"
            )
            
            industry = st.text_input(
                "Industry",
                value=st.session_state.competitor_form_data['industry'],
                help="The industry of the company"
            )
            
            competitors = st.text_area(
                "Competitors (one per line)",
                value='\n'.join(st.session_state.competitor_form_data['competitors']),
                help="List of competitors to analyze"
            )
        
        with col2:
            analysis_focus = st.multiselect(
                "Analysis Focus Areas",
                options=[
                    "Market Position",
                    "Product Offerings",
                    "Pricing Strategy",
                    "Marketing Strategy",
                    "SWOT Analysis",
                    "Financial Performance",
                    "Customer Base",
                    "Technology Stack"
                ],
                default=st.session_state.competitor_form_data['analysis_focus']
            )
            
            timeframe = st.selectbox(
                "Analysis Timeframe",
                options=["3 months", "6 months", "1 year", "2 years", "5 years"],
                index=["3 months", "6 months", "1 year", "2 years", "5 years"].index(
                    st.session_state.competitor_form_data['timeframe']
                )
            )
            
            additional_notes = st.text_area(
                "Additional Notes",
                value=st.session_state.competitor_form_data['additional_notes'],
                help="Any additional context or specific areas to focus on"
            )
        
        submitted = st.form_submit_button("Start Analysis")
        
        if submitted:
            # Process competitors list
            competitors_list = [c.strip() for c in competitors.split('\n') if c.strip()]
            
            # Save form data to session state
            st.session_state.competitor_form_data = {
                'company_name': company_name,
                'industry': industry,
                'competitors': competitors_list,
                'analysis_focus': analysis_focus,
                'timeframe': timeframe,
                'additional_notes': additional_notes
            }
            
            # TODO: Integrate with competitor_analysis module
            with st.spinner("Analyzing competitors... This may take a few minutes."):
                try:
                    # Placeholder for competitor_analysis integration
                    st.success("Analysis completed successfully!")
                    
                    # Show results
                    st.subheader("Analysis Results")
                    
                    # Placeholder for results
                    st.json({
                        "status": "success",
                        "company": company_name,
                        "competitors_analyzed": competitors_list,
                        "analysis_focus": analysis_focus,
                        "timestamp": datetime.now().isoformat()
                    })
                    
                except Exception as e:
                    st.error(f"An error occurred during analysis: {str(e)}")
    
    # Display saved form data for reference
    if st.checkbox("Show current form data"):
        st.json(st.session_state.competitor_form_data)

# Run the page
if __name__ == "__main__":
    show_competitor_analysis()
