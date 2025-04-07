"""Streamlit application for managing human interactions with the CrewAI flow."""

import os
import sys
import json
import time
import streamlit as st
from pathlib import Path
from typing import Dict, Any, List, Optional

# Ensure the src directory is in the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Import utility functions
from scan_sources.utilities.streamlit_interface import (
    HUMAN_INPUT_REQUEST_PATH, 
    HUMAN_INPUT_RESPONSE_PATH,
    FLOW_STATUS_PATH,
    load_json,
    save_json
)

# Import Pydantic models for type checking
from scan_sources.utilities.models import IdentifiedForce, SourceFinding

# Page configuration
st.set_page_config(
    page_title="CrewAI Human Interaction",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.8rem;
        font-weight: bold;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .status-running {
        color: #1E90FF;
        font-weight: bold;
    }
    .status-waiting {
        color: #FFA500;
        font-weight: bold;
    }
    .status-completed {
        color: #32CD32;
        font-weight: bold;
    }
    .status-error {
        color: #FF4500;
        font-weight: bold;
    }
    .force-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 15px;
        border-left: 5px solid #4B0082;
    }
    .source-card {
        background-color: #f0f0f0;
        border-radius: 5px;
        padding: 10px;
        margin-top: 10px;
        margin-bottom: 10px;
        border-left: 3px solid #1E90FF;
    }
</style>
""", unsafe_allow_html=True)

def display_flow_status():
    """Display the current status of the CrewAI flow."""
    st.markdown('<div class="sub-header">Flow Status</div>', unsafe_allow_html=True)
    
    status_data = load_json(FLOW_STATUS_PATH) if FLOW_STATUS_PATH.exists() else None
    
    if not status_data:
        st.info("No flow status available. The CrewAI flow might not be running yet.")
        return
    
    status = status_data.get("status", "unknown")
    message = status_data.get("message", "")
    current_step = status_data.get("current_step", "")
    timestamp = status_data.get("timestamp", 0)
    
    # Format timestamp
    time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(timestamp))
    
    # Display status with appropriate styling
    if status == "running":
        st.markdown(f'<p>Status: <span class="status-running">Running</span></p>', unsafe_allow_html=True)
    elif status == "waiting":
        st.markdown(f'<p>Status: <span class="status-waiting">Waiting for Input</span></p>', unsafe_allow_html=True)
    elif status == "completed":
        st.markdown(f'<p>Status: <span class="status-completed">Completed</span></p>', unsafe_allow_html=True)
    elif status == "error":
        st.markdown(f'<p>Status: <span class="status-error">Error</span></p>', unsafe_allow_html=True)
    else:
        st.markdown(f'<p>Status: {status}</p>', unsafe_allow_html=True)
    
    st.write(f"Current Step: {current_step}")
    st.write(f"Last Updated: {time_str}")
    
    if message:
        st.write(f"Message: {message}")

def display_force(force, index):
    """Display a single market force with its details."""
    with st.container():
        st.markdown(f'<div class="force-card">', unsafe_allow_html=True)
        st.subheader(f"{index+1}. {force.get('name', 'Unnamed Force')}")
        
        # Display force description
        st.markdown("**Description:**")
        st.write(force.get('description', 'No description available'))
        
        # Display keywords
        keywords = force.get('keywords', [])
        if keywords:
            st.markdown("**Keywords:**")
            st.write(", ".join(keywords))
        
        # Display scope and time horizon
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("**Scope:**")
            st.write(force.get('scope', 'Not specified'))
        with col2:
            st.markdown("**Time Horizon:**")
            st.write(force.get('time_horizon', 'Not specified'))
        
        # Display supporting sources
        sources = force.get('supporting_sources', [])
        if sources:
            with st.expander("Supporting Sources", expanded=False):
                for i, source in enumerate(sources):
                    st.markdown(f'<div class="source-card">', unsafe_allow_html=True)
                    st.markdown(f"**Source {i+1}:** {source.get('source_name', 'Unknown Source')}")
                    st.write(f"Type: {source.get('source_type', 'Unknown')}")
                    if 'url' in source and source['url']:
                        st.write(f"URL: {source['url']}")
                    st.write(f"Snippet: {source.get('text_snippet', 'No text available')}")
                    st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)

def handle_human_input_request():
    """Handle requests for human input."""
    if not HUMAN_INPUT_REQUEST_PATH.exists():
        st.info("No pending requests for human input.")
        return
    
    request_data = load_json(HUMAN_INPUT_REQUEST_PATH)
    if not request_data:
        st.info("No valid request data found.")
        return
    
    task_id = request_data.get("task_id", "unknown")
    task_description = request_data.get("task_description", "")
    data_to_review = request_data.get("data_to_review", [])
    
    st.markdown('<div class="sub-header">Review Requested</div>', unsafe_allow_html=True)
    st.write(task_description)
    
    # Display data to review (assuming it's a list of market forces)
    if data_to_review:
        st.markdown("### Preliminary Findings")
        for i, force in enumerate(data_to_review):
            display_force(force, i)
    
    # Feedback form
    st.markdown("### Your Feedback")
    
    feedback_type = st.radio(
        "Feedback Type:",
        ["Approve as is", "Suggest modifications", "Request additional research"]
    )
    
    feedback_text = ""
    modified_forces = data_to_review.copy() if isinstance(data_to_review, list) else []
    
    if feedback_type == "Suggest modifications":
        st.write("Please provide your suggestions for each force:")
        
        # Create a tab for each force to edit
        if modified_forces:
            tabs = st.tabs([f"Force {i+1}: {force.get('name', 'Unnamed')}" for i, force in enumerate(modified_forces)])
            
            for i, tab in enumerate(tabs):
                with tab:
                    force = modified_forces[i]
                    force['name'] = st.text_input(f"Name", value=force.get('name', ''), key=f"name_{i}")
                    force['description'] = st.text_area(f"Description", value=force.get('description', ''), key=f"desc_{i}")
                    force['keywords'] = st.text_input(f"Keywords (comma-separated)", 
                                                    value=", ".join(force.get('keywords', [])), 
                                                    key=f"keywords_{i}")
                    force['scope'] = st.text_input(f"Scope", value=force.get('scope', ''), key=f"scope_{i}")
                    force['time_horizon'] = st.text_input(f"Time Horizon", 
                                                        value=force.get('time_horizon', ''), 
                                                        key=f"time_{i}")
        
        feedback_text = st.text_area("Additional comments or suggestions:", height=150)
    
    elif feedback_type == "Request additional research":
        feedback_text = st.text_area("Please specify what additional research is needed:", height=200)
    
    else:  # Approve as is
        feedback_text = st.text_area("Any additional comments (optional):", height=100)
    
    # Submit button
    if st.button("Submit Feedback"):
        # Process keywords from string back to list
        if feedback_type == "Suggest modifications":
            for force in modified_forces:
                if isinstance(force.get('keywords'), str):
                    force['keywords'] = [k.strip() for k in force['keywords'].split(',') if k.strip()]
        
        # Prepare response data
        response_data = {
            "task_id": task_id,
            "feedback_type": feedback_type,
            "feedback_text": feedback_text,
            "modified_data": modified_forces if feedback_type == "Suggest modifications" else data_to_review,
            "timestamp": time.time()
        }
        
        # Save response
        save_json(response_data, HUMAN_INPUT_RESPONSE_PATH)
        
        # Remove the request file to indicate it's been handled
        if HUMAN_INPUT_REQUEST_PATH.exists():
            HUMAN_INPUT_REQUEST_PATH.unlink()
        
        st.success("Feedback submitted successfully!")
        time.sleep(2)  # Give user time to see the success message
        st.experimental_rerun()  # Refresh the page

def main():
    """Main Streamlit application."""
    st.markdown('<div class="main-header">CrewAI Human Interaction Portal</div>', unsafe_allow_html=True)
    st.write("This interface allows you to interact with the CrewAI flow and provide human input when requested.")
    
    # Display flow status
    display_flow_status()
    
    # Check for human input requests
    handle_human_input_request()
    
    # Add a refresh button
    if st.button("Refresh"):
        st.experimental_rerun()

if __name__ == "__main__":
    main()
