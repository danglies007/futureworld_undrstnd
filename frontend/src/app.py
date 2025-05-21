import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
import streamlit as st
from utils.process_runner import run_process_with_realtime_output, check_output_files, format_markdown_for_display

# Define project paths
project_root = Path(__file__).parent.parent.parent

# Add the project root to the Python path
sys.path.append(str(project_root))

# Also add the scan_sources directory to the Python path
scan_sources_dir = os.path.join(project_root, "scan_sources")
sys.path.append(str(scan_sources_dir))

# Add the src directory to the Python path
src_dir = os.path.join(scan_sources_dir, "src")
sys.path.append(str(src_dir))

# Find the Python interpreter from the scan_sources virtual environment
venv_python = os.path.join(scan_sources_dir, ".venv", "bin", "python")
if not os.path.exists(venv_python):
    # Fall back to the system Python
    venv_python = shutil.which("python3") or shutil.which("python")
wrapper_dir = Path(__file__).parent
scan_sources_wrapper = os.path.join(wrapper_dir, "run_scan_sources.py")
competitor_analysis_wrapper = os.path.join(wrapper_dir, "run_competitor_analysis.py")

# Function to check if required files exist
def check_required_files():
    missing_files = []
    
    if not os.path.exists(scan_sources_wrapper):
        missing_files.append(f"Scan Sources wrapper script: {scan_sources_wrapper}")
    
    if not os.path.exists(competitor_analysis_wrapper):
        missing_files.append(f"Competitor Analysis wrapper script: {competitor_analysis_wrapper}")
    
    return missing_files

# Set page configuration
st.set_page_config(
    page_title="Undrstnd AI Research Platform",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    .info-box {
        background-color: #f0f2f6;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 4rem;
        white-space: pre-wrap;
        background-color: #f0f2f6;
        border-radius: 0.5rem 0.5rem 0 0;
        padding: 1rem 2rem;
        font-weight: 600;
    }
    .stTabs [aria-selected="true"] {
        background-color: #e0e2e6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">Undrstnd AI Research Platform</h1>', unsafe_allow_html=True)
    
    # Check if required files exist
    missing_files = check_required_files()
    if missing_files:
        st.error("Missing required files:")
        for file in missing_files:
            st.error(f"- {file}")
        st.info("Please check that the project structure is correct.")
        return
    
    # Create tabs for different research tools
    tab1, tab2 = st.tabs(["Market Forces Scanner", "Competitor Analysis"])
    
    with tab1:
        market_forces_scanner()
    
    with tab2:
        competitor_analysis()

def market_forces_scanner():
    st.markdown('<h2 class="sub-header">Market Forces Scanner</h2>', unsafe_allow_html=True)
    
    # Add a column layout for the info box and debug toggle
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        This tool scans various sources to identify market forces affecting your industry.
        It analyzes the sources, extracts relevant market forces, and generates a comprehensive report.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        show_debug_logs = st.toggle("Show Debug Logs", value=False, help="Toggle to show or hide LiteLLM debug logs", key="market_forces_debug_toggle")
    
    # Load default config
    try:
        # Try different import paths
        try:
            from scan_sources.src.scan_sources.config import RESEARCH_INPUTS, SOURCES_FAVOURITE, SOURCES_CONSULTING_FIRMS, SOURCES_NEWS_SOURCES
        except ImportError:
            try:
                from src.scan_sources.config import RESEARCH_INPUTS, SOURCES_FAVOURITE, SOURCES_CONSULTING_FIRMS, SOURCES_NEWS_SOURCES
            except ImportError:
                from scan_sources.config import RESEARCH_INPUTS, SOURCES_FAVOURITE, SOURCES_CONSULTING_FIRMS, SOURCES_NEWS_SOURCES
        
        default_config = RESEARCH_INPUTS.copy()
    except ImportError as e:
        st.error(f"Could not import scan_sources configuration: {e}. Please check your installation.")
        default_config = {
            'specialisation': 'Various',
            'topic': 'Global Market Forces',
            'topic_short': 'market_forces',
            'market': '',
            'business': '',
            'audience': 'Expert',
            'specific_points_of_interest': [''],
            'minimum_number_of_sources': 1,
            'maximum_number_of_sources': 20,
            'minimum_number_of_forces': 0,
            'source_score_threshold': 0,
        }
    
    with st.form("market_forces_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            topic = st.text_input("Research Topic", value=default_config.get('topic', ''))
            topic_short = st.text_input("Topic Short Name (for file naming)", value=default_config.get('topic_short', ''))
            market = st.text_input("Target Market", value=default_config.get('market', ''))
            business = st.text_input("Business Name", value=default_config.get('business', ''))
        
        with col2:
            audience = st.selectbox("Target Audience", 
                                  options=["Beginner", "Intermediate", "Expert"], 
                                  index=2 if default_config.get('audience') == 'Expert' else 0)
            
            min_sources = st.number_input("Minimum Number of Sources", 
                                        min_value=1, 
                                        max_value=20, 
                                        value=default_config.get('minimum_number_of_sources', 1))
            
            max_sources = st.number_input("Maximum Number of Sources", 
                                        min_value=1, 
                                        max_value=30, 
                                        value=default_config.get('maximum_number_of_sources', 10))
            
            min_forces = st.number_input("Minimum Number of Forces", 
                                       min_value=0, 
                                       max_value=20, 
                                       value=default_config.get('minimum_number_of_forces', 0))
        
        st.markdown("### Points of Interest")
        points_of_interest = st.text_area("Specific Points of Interest (one per line)", 
                                         value="\n".join(default_config.get('specific_points_of_interest', [''])))
        
        # Custom sources
        st.markdown("### Custom Sources")
        custom_sources = st.text_area("Custom Sources (URLs, one per line)", 
                                    value="")
        
        # Source categories
        st.markdown("### Source Categories")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            use_consulting_firms = st.checkbox("Include Consulting Firms", value=True)
        
        with col2:
            use_news_sources = st.checkbox("Include News Sources", value=True)
        
        with col3:
            use_favourite_sources = st.checkbox("Include Favourite Sources", value=True)
        
        submitted = st.form_submit_button("Run Market Forces Analysis")
        
        if submitted:
            # Prepare the research inputs
            updated_config = default_config.copy()
            updated_config['topic'] = topic
            updated_config['topic_short'] = topic_short
            updated_config['market'] = market
            updated_config['business'] = business
            updated_config['audience'] = audience
            updated_config['minimum_number_of_sources'] = min_sources
            updated_config['maximum_number_of_sources'] = max_sources
            updated_config['minimum_number_of_forces'] = min_forces
            updated_config['specific_points_of_interest'] = [p.strip() for p in points_of_interest.split('\n') if p.strip()]
            
            # Prepare research sources
            research_sources = []
            if use_consulting_firms and 'SOURCES_CONSULTING_FIRMS' in globals():
                research_sources.extend(SOURCES_CONSULTING_FIRMS)
            if use_news_sources and 'SOURCES_NEWS_SOURCES' in globals():
                research_sources.extend(SOURCES_NEWS_SOURCES)
            if use_favourite_sources and 'SOURCES_FAVOURITE' in globals():
                research_sources.extend(SOURCES_FAVOURITE)
            
            # Add custom sources
            if custom_sources:
                custom_sources_list = [s.strip() for s in custom_sources.split('\n') if s.strip()]
                research_sources.extend(custom_sources_list)
                
                # Save custom sources to a file for the crew to use
                user_urls_data = {
                    "approved_sources": custom_sources_list,
                    "total_sources_found": len(custom_sources_list)
                }
                
                os.makedirs("Resume_files", exist_ok=True)
                with open("Resume_files/user_urls.json", "w") as f:
                    json.dump(user_urls_data, f)
            
            updated_config['research_sources'] = research_sources
            
            # Save updated config to a temporary file in the project root directory
            project_root = Path(__file__).parent.parent.parent
            config_path = os.path.join(project_root, "temp_config.json")
            with open(config_path, "w") as f:
                # Convert datetime objects to strings for JSON serialization
                config_for_json = {k: (v.strftime('%d %B %Y') if isinstance(v, datetime) else v) 
                                 for k, v in updated_config.items()}
                json.dump(config_for_json, f)
                st.info(f"Saved configuration to {config_path}")
            
            # Run the scan_sources crew using the wrapper script
            with st.spinner("Running Market Forces Analysis... This may take several minutes."):
                try:
                    # Run the process with real-time output
                    cmd = [venv_python, scan_sources_wrapper]
                    return_code, output_text = run_process_with_realtime_output(
                        cmd=cmd,
                        cwd=str(project_root),
                        title="Market Forces Analysis Output",
                        expanded=True,
                        show_debug_logs=show_debug_logs
                    )
                    
                    # Display log analysis buttons outside of any form context
                    from utils.process_runner import display_log_analysis_buttons
                    log_path = os.path.join("logs", f"process_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
                    if os.path.exists(log_path):
                        display_log_analysis_buttons(log_path)
                    
                    # Check if output files were generated
                    output_files = [
                        os.path.join(project_root, "Resume_files", "saved_report.json"),
                        os.path.join(project_root, "outputs", "market_forces_report.md")
                    ]
                    file_descriptions = ["Market Forces Report (JSON)", "Market Forces Report (Markdown)"]
                    
                    files_found = check_output_files(output_files, file_descriptions)
                    
                    # Display the report if it was generated
                    if files_found:
                        report_path = os.path.join(project_root, "Resume_files", "saved_report.json")
                        if os.path.exists(report_path):
                            with open(report_path, "r") as f:
                                report_data = json.load(f)
                            
                            with st.expander("View Analysis Results", expanded=False):
                                st.json(report_data)
                except subprocess.CalledProcessError as e:
                    st.error(f"Error running Market Forces Analysis: {e}")
                    st.code(e.stdout)
                    st.code(e.stderr)

def competitor_analysis():
    st.markdown('<h2 class="sub-header">Competitor Analysis</h2>', unsafe_allow_html=True)
    
    # Add a column layout for the info box and debug toggle
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown("""
        <div class="info-box">
        This tool performs a comprehensive analysis of your company and its competitors.
        It includes internal analysis, external analysis, and integrated analysis to provide strategic insights.
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        show_debug_logs = st.toggle("Show Debug Logs", value=False, help="Toggle to show or hide LiteLLM debug logs", key="competitor_analysis_debug_toggle")
    
    # Load default config
    try:
        # Try different import paths
        try:
            from scan_sources.src.competitor_analysis.config_competitor_analysis import RESEARCH_INPUTS
        except ImportError:
            try:
                from src.competitor_analysis.config_competitor_analysis import RESEARCH_INPUTS
            except ImportError:
                from competitor_analysis.config_competitor_analysis import RESEARCH_INPUTS
        
        default_config = RESEARCH_INPUTS.copy()
    except ImportError as e:
        st.error(f"Could not import competitor_analysis configuration: {e}. Please check your installation.")
        default_config = {
            'company_name': '',
            'ticker_symbol': '',
            'industry': '',
            'company_name_short': '',
            'time_period': '2022-2025',
            'detail_level': 'comprehensive',
            'audience': 'Expert Investors',
            'include_esg_analysis': True,
            'include_scenario_planning': True,
            'include_strategic_recommendations': True
        }
    
    with st.form("competitor_analysis_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", value=default_config.get('company_name', ''))
            ticker_symbol = st.text_input("Ticker Symbol", value=default_config.get('ticker_symbol', ''))
            industry = st.text_input("Industry", value=default_config.get('industry', ''))
            company_name_short = st.text_input("Company Short Name", value=default_config.get('company_name_short', ''))
        
        with col2:
            time_period = st.text_input("Time Period", value=default_config.get('time_period', '2022-2025'))
            detail_level = st.selectbox("Detail Level", 
                                      options=["brief", "standard", "comprehensive"], 
                                      index=2 if default_config.get('detail_level') == 'comprehensive' else 0)
            audience = st.text_input("Target Audience", value=default_config.get('audience', 'Expert Investors'))
        
        st.markdown("### Analysis Options")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            include_esg = st.checkbox("Include ESG Analysis", value=default_config.get('include_esg_analysis', True))
        
        with col2:
            include_scenario = st.checkbox("Include Scenario Planning", value=default_config.get('include_scenario_planning', True))
        
        with col3:
            include_recommendations = st.checkbox("Include Strategic Recommendations", value=default_config.get('include_strategic_recommendations', True))
        
        st.markdown("### Competitors")
        competitors = st.text_area("Competitor Names (one per line)", 
                                 value="\n".join(default_config.get('competitor_names', [])))
        
        st.markdown("### Focus Areas")
        focus_areas = st.text_area("Focus Areas (one per line)", 
                                  value="\n".join(default_config.get('focus_areas', [])))
        
        submitted = st.form_submit_button("Run Competitor Analysis")
        
        if submitted:
            # Prepare the research inputs
            updated_config = default_config.copy()
            updated_config['company_name'] = company_name
            updated_config['ticker_symbol'] = ticker_symbol
            updated_config['industry'] = industry
            updated_config['company_name_short'] = company_name_short
            updated_config['time_period'] = time_period
            updated_config['detail_level'] = detail_level
            updated_config['audience'] = audience
            updated_config['include_esg_analysis'] = include_esg
            updated_config['include_scenario_planning'] = include_scenario
            updated_config['include_strategic_recommendations'] = include_recommendations
            updated_config['competitor_names'] = [c.strip() for c in competitors.split('\n') if c.strip()]
            updated_config['focus_areas'] = [f.strip() for f in focus_areas.split('\n') if f.strip()]
            
            # Save updated config to a temporary file in the project root directory
            project_root = Path(__file__).parent.parent.parent
            config_path = os.path.join(project_root, "temp_competitor_config.json")
            with open(config_path, "w") as f:
                # Convert datetime objects to strings for JSON serialization
                config_for_json = {k: (v.strftime('%d %B %Y') if isinstance(v, datetime) else v) 
                                 for k, v in updated_config.items()}
                json.dump(config_for_json, f)
                st.info(f"Saved configuration to {config_path}")
            
            # Run the competitor_analysis crew using the wrapper script
            with st.spinner("Running Competitor Analysis... This may take several minutes."):
                try:
                    # Run the process with real-time output
                    cmd = [venv_python, competitor_analysis_wrapper]
                    return_code, output_text = run_process_with_realtime_output(
                        cmd=cmd,
                        cwd=str(project_root),
                        title="Competitor Analysis Output",
                        expanded=True,
                        show_debug_logs=show_debug_logs
                    )
                    
                    # Check if output files were generated
                    output_files = [
                        os.path.join(project_root, "internal_analysis_report.md"),
                        os.path.join(project_root, "external_analysis_report.md"),
                        os.path.join(project_root, "integrated_analysis_report.md")
                    ]
                    file_descriptions = [
                        "Internal Analysis Report", 
                        "External Analysis Report", 
                        "Integrated Analysis Report"
                    ]
                    
                    files_found = check_output_files(output_files, file_descriptions)
                    
                    # Display the reports if they were generated
                    if files_found:
                        # Internal Analysis Report
                        internal_report_path = os.path.join(project_root, "internal_analysis_report.md")
                        if os.path.exists(internal_report_path):
                            with open(internal_report_path, "r") as f:
                                internal_report = f.read()
                            
                            # Format the markdown for better display
                            formatted_report = format_markdown_for_display(internal_report)
                            
                            with st.expander("Internal Analysis Report", expanded=False):
                                st.markdown(formatted_report, unsafe_allow_html=True)
                        
                        # External Analysis Report
                        external_report_path = os.path.join(project_root, "external_analysis_report.md")
                        if os.path.exists(external_report_path):
                            with open(external_report_path, "r") as f:
                                external_report = f.read()
                            
                            # Format the markdown for better display
                            formatted_report = format_markdown_for_display(external_report)
                            
                            with st.expander("External Analysis Report", expanded=False):
                                st.markdown(formatted_report, unsafe_allow_html=True)
                        
                        # Integrated Analysis Report
                        integrated_report_path = os.path.join(project_root, "integrated_analysis_report.md")
                        if os.path.exists(integrated_report_path):
                            with open(integrated_report_path, "r") as f:
                                integrated_report = f.read()
                            
                            # Format the markdown for better display
                            formatted_report = format_markdown_for_display(integrated_report)
                            
                            with st.expander("Integrated Analysis Report", expanded=False):
                                st.markdown(formatted_report, unsafe_allow_html=True)
                except subprocess.CalledProcessError as e:
                    st.error(f"Error running Competitor Analysis: {e}")
                    st.code(e.stdout)
                    st.code(e.stderr)

if __name__ == "__main__":
    main()
