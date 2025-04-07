"""Streamlit interface for human interactions with the CrewAI flow."""

import os
import json
import time
import streamlit as st
from pathlib import Path
from typing import Dict, Any, List, Optional

# Create a directory for storing interaction data
INTERACTION_DIR = Path("interaction_data")
INTERACTION_DIR.mkdir(exist_ok=True)

# File paths for interaction data
HUMAN_INPUT_REQUEST_PATH = INTERACTION_DIR / "human_input_request.json"
HUMAN_INPUT_RESPONSE_PATH = INTERACTION_DIR / "human_input_response.json"
FLOW_STATUS_PATH = INTERACTION_DIR / "flow_status.json"

def save_json(data: Dict[str, Any], file_path: Path) -> None:
    """Save data to a JSON file."""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def load_json(file_path: Path) -> Optional[Dict[str, Any]]:
    """Load data from a JSON file if it exists."""
    if file_path.exists():
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

def request_human_input(task_id: str, task_description: str, data_to_review: Any) -> None:
    """Request human input from the Streamlit interface."""
    request_data = {
        "task_id": task_id,
        "task_description": task_description,
        "data_to_review": data_to_review,
        "timestamp": time.time()
    }
    save_json(request_data, HUMAN_INPUT_REQUEST_PATH)
    
    # Clear any previous response
    if HUMAN_INPUT_RESPONSE_PATH.exists():
        HUMAN_INPUT_RESPONSE_PATH.unlink()

def get_human_input_response() -> Optional[Dict[str, Any]]:
    """Check if human input has been provided."""
    return load_json(HUMAN_INPUT_RESPONSE_PATH)

def update_flow_status(status: str, message: str = "", current_step: str = "") -> None:
    """Update the flow status for the Streamlit interface."""
    status_data = {
        "status": status,
        "message": message,
        "current_step": current_step,
        "timestamp": time.time()
    }
    save_json(status_data, FLOW_STATUS_PATH)

def get_flow_status() -> Dict[str, Any]:
    """Get the current flow status."""
    status = load_json(FLOW_STATUS_PATH)
    if not status:
        return {"status": "unknown", "message": "Flow status not available", "current_step": "", "timestamp": time.time()}
    return status
