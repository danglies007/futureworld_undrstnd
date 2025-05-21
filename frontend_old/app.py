import os
import sys
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Add the parent directory to the path to import modules
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="UNDRSTND Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def main():
    st.title("UNDRSTND Analytics Dashboard")
    st.write("Welcome to the UNDRSTND Analytics Dashboard. Use the sidebar to navigate between different analysis tools.")
    
    # Add a brief description of the available tools
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔍 Source Scanner")
        st.markdown("""
        - Scan and analyze various sources
        - Extract market forces
        - Generate comprehensive reports
        - Analyze implications
        """)
    
    with col2:
        st.subheader("🏢 Competitor Analysis")
        st.markdown("""
        - Analyze competitors' internal and external factors
        - Generate integrated analysis reports
        - Compare multiple competitors
        - Export analysis results
        """)
    
    st.markdown("---")
    st.info("💡 Start by selecting a tool from the sidebar to begin your analysis.")

if __name__ == "__main__":
    main()
