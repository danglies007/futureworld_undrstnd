"""Handler for human input in CrewAI flows."""

import time
from pathlib import Path
from typing import Dict, Any, Optional

from scan_sources.utilities.streamlit_interface import (
    request_human_input,
    get_human_input_response,
    update_flow_status
)

def handle_human_input_task(task_id: str, task_description: str, data_to_review: Any) -> Dict[str, Any]:
    """
    Handle a task that requires human input by interfacing with the Streamlit app.
    
    Args:
        task_id: Unique identifier for the task
        task_description: Description of what the human needs to review
        data_to_review: Data that needs human review
        
    Returns:
        Dictionary containing the human feedback
    """
    # Update flow status to waiting for human input
    update_flow_status(
        status="waiting", 
        message=f"Waiting for human input on task: {task_id}", 
        current_step=task_id
    )
    
    # Request human input through the Streamlit interface
    request_human_input(task_id, task_description, data_to_review)
    
    print(f"\n[HUMAN INPUT REQUIRED] Task: {task_id}")
    print("Please provide your input through the Streamlit interface.")
    print("Run the Streamlit app with: streamlit run scan_sources/src/scan_sources/streamlit_app.py\n")
    
    # Wait for human input
    response = None
    while response is None:
        response = get_human_input_response()
        if response is None:
            print("Waiting for human input... (checking every 5 seconds)")
            time.sleep(5)
    
    # Update flow status to running again
    update_flow_status(
        status="running", 
        message=f"Received human input for task: {task_id}", 
        current_step=task_id
    )
    
    print(f"\n[HUMAN INPUT RECEIVED] Task: {task_id}")
    
    return response
