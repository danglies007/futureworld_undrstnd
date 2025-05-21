"""
Task Log Viewer for Streamlit

This module provides a Streamlit component for viewing logs organized by tasks.
It extracts tasks from log files and allows users to select specific tasks to view.
"""
import os
import re
import streamlit as st
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from utils.log_analyzer import extract_task_info, extract_crew_info

def extract_tasks_from_log(log_content: str) -> List[Dict[str, Any]]:
    """
    Extract tasks from log content.
    
    Args:
        log_content: The content of the log file
        
    Returns:
        List of task dictionaries
    """
    return extract_task_info(log_content)

def extract_crews_from_log(log_content: str) -> List[Dict[str, Any]]:
    """
    Extract crews from log content.
    
    Args:
        log_content: The content of the log file
        
    Returns:
        List of crew dictionaries
    """
    return extract_crew_info(log_content)

def extract_task_log_content(log_content: str, task_id: str) -> str:
    """
    Extract the log content specific to a task.
    
    Args:
        log_content: The full log content
        task_id: The ID of the task to extract
        
    Returns:
        Log content specific to the task
    """
    # Look for the task section in the log
    task_section = re.search(f"Task: {task_id}[\\s\\S]*?(?=Task: [a-f0-9\\-]+|$)", log_content)
    if task_section:
        return task_section.group(0)
    return "Task log content not found."

def extract_crew_log_content(log_content: str, crew_id: str) -> str:
    """
    Extract the log content specific to a crew.
    
    Args:
        log_content: The full log content
        crew_id: The ID of the crew to extract
        
    Returns:
        Log content specific to the crew
    """
    # Look for the crew section in the log
    crew_section = re.search(f"ID: {crew_id}[\\s\\S]*?(?=Crew Execution Started|$)", log_content)
    if crew_section:
        return crew_section.group(0)
    return "Crew log content not found."

def display_task_selector(log_file_path: Union[str, Path]) -> None:
    """
    Display a task selector for viewing logs by task.
    
    Args:
        log_file_path: Path to the log file
    """
    if isinstance(log_file_path, str):
        log_file_path = Path(log_file_path)
    
    if not log_file_path.exists():
        st.error(f"Log file not found: {log_file_path}")
        return
    
    # Read log content
    with open(log_file_path, 'r') as f:
        log_content = f.read()
    
    # Extract tasks and crews
    tasks = extract_tasks_from_log(log_content)
    crews = extract_crews_from_log(log_content)
    
    # Create tabs for Tasks and Crews
    tab1, tab2, tab3 = st.tabs(["Current Task", "All Tasks", "Crews"])
    
    with tab1:
        # Show the most recent task by default
        if tasks:
            latest_task = tasks[-1]
            task_name = latest_task.get("name", "Unnamed Task")
            task_desc = latest_task.get("description", "")
            task_id = latest_task.get("id", "")
            
            # Display task information
            st.subheader(f"Current Task: {task_name if task_name else task_desc[:50] + '...' if len(task_desc) > 50 else task_desc}")
            st.markdown(f"**ID:** `{task_id}`")
            
            if latest_task.get("start_time"):
                st.markdown(f"**Start Time:** {latest_task['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            
            if latest_task.get("end_time"):
                st.markdown(f"**End Time:** {latest_task['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                
                if latest_task.get("duration"):
                    minutes, seconds = divmod(latest_task["duration"], 60)
                    st.markdown(f"**Duration:** {int(minutes)} minutes, {int(seconds)} seconds")
            
            # Display task log content
            st.markdown("### Task Log")
            task_log = extract_task_log_content(log_content, task_id)
            st.code(task_log, language="text")
            
            # Display task metrics
            if latest_task.get("total_cost") > 0:
                st.markdown("### Task Metrics")
                st.markdown(f"**Total Cost:** ${latest_task['total_cost']:.6f}")
                st.markdown(f"**Number of API Calls:** {len(latest_task.get('costs', []))}")
                
                if latest_task.get("llm_models"):
                    st.markdown("**LLM Models Used:**")
                    for model in latest_task["llm_models"]:
                        st.markdown(f"- {model}")
        else:
            st.info("No tasks found in the log file.")
    
    with tab2:
        if tasks:
            # Create a selectbox for task selection
            task_options = []
            for task in tasks:
                task_name = task.get("name", "Unnamed Task")
                task_desc = task.get("description", "")
                task_id = task.get("id", "")
                
                # Create a display name for the task
                if task_name:
                    display_name = f"{task_name} (ID: {task_id})"
                elif task_desc:
                    # Truncate long descriptions
                    short_desc = task_desc[:50] + "..." if len(task_desc) > 50 else task_desc
                    display_name = f"{short_desc} (ID: {task_id})"
                else:
                    display_name = f"Task ID: {task_id}"
                
                task_options.append((display_name, task_id))
            
            # Display the selectbox
            selected_task_option = st.selectbox(
                "Select a task to view:",
                options=[option[0] for option in task_options],
                index=len(task_options) - 1  # Select the latest task by default
            )
            
            # Get the selected task ID
            selected_task_id = next((option[1] for option in task_options if option[0] == selected_task_option), None)
            
            if selected_task_id:
                # Find the selected task
                selected_task = next((task for task in tasks if task["id"] == selected_task_id), None)
                
                if selected_task:
                    # Display task information
                    st.markdown(f"**Task ID:** `{selected_task_id}`")
                    
                    if selected_task.get("name"):
                        st.markdown(f"**Task Name:** {selected_task['name']}")
                    
                    if selected_task.get("description"):
                        st.markdown(f"**Task Description:** {selected_task['description']}")
                    
                    if selected_task.get("start_time"):
                        st.markdown(f"**Start Time:** {selected_task['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    if selected_task.get("end_time"):
                        st.markdown(f"**End Time:** {selected_task['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        if selected_task.get("duration"):
                            minutes, seconds = divmod(selected_task["duration"], 60)
                            st.markdown(f"**Duration:** {int(minutes)} minutes, {int(seconds)} seconds")
                    
                    # Display task log content
                    st.markdown("### Task Log")
                    task_log = extract_task_log_content(log_content, selected_task_id)
                    st.code(task_log, language="text")
                    
                    # Display task metrics
                    if selected_task.get("total_cost") > 0:
                        st.markdown("### Task Metrics")
                        st.markdown(f"**Total Cost:** ${selected_task['total_cost']:.6f}")
                        st.markdown(f"**Number of API Calls:** {len(selected_task.get('costs', []))}")
                        
                        if selected_task.get("llm_models"):
                            st.markdown("**LLM Models Used:**")
                            for model in selected_task["llm_models"]:
                                st.markdown(f"- {model}")
        else:
            st.info("No tasks found in the log file.")
    
    with tab3:
        if crews:
            # Create a selectbox for crew selection
            crew_options = []
            for crew in crews:
                crew_name = crew.get("name", "Unnamed Crew")
                crew_id = crew.get("id", "")
                display_name = f"{crew_name} (ID: {crew_id})"
                crew_options.append((display_name, crew_id))
            
            # Display the selectbox
            selected_crew_option = st.selectbox(
                "Select a crew to view:",
                options=[option[0] for option in crew_options],
                index=0
            )
            
            # Get the selected crew ID
            selected_crew_id = next((option[1] for option in crew_options if option[0] == selected_crew_option), None)
            
            if selected_crew_id:
                # Find the selected crew
                selected_crew = next((crew for crew in crews if crew["id"] == selected_crew_id), None)
                
                if selected_crew:
                    # Display crew information
                    st.markdown(f"**Crew ID:** `{selected_crew_id}`")
                    
                    if selected_crew.get("name"):
                        st.markdown(f"**Crew Name:** {selected_crew['name']}")
                    
                    if selected_crew.get("start_time"):
                        st.markdown(f"**Start Time:** {selected_crew['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                    
                    if selected_crew.get("end_time"):
                        st.markdown(f"**End Time:** {selected_crew['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
                        
                        if selected_crew.get("duration"):
                            minutes, seconds = divmod(selected_crew["duration"], 60)
                            st.markdown(f"**Duration:** {int(minutes)} minutes, {int(seconds)} seconds")
                    
                    # Display crew tasks
                    if selected_crew.get("tasks"):
                        st.markdown("### Crew Tasks")
                        for task_id in selected_crew["tasks"]:
                            task = next((t for t in tasks if t["id"] == task_id), None)
                            if task:
                                task_name = task.get("name", "Unnamed Task")
                                task_desc = task.get("description", "")
                                
                                if task_name:
                                    st.markdown(f"- **{task_name}** (ID: `{task_id}`)")
                                elif task_desc:
                                    # Truncate long descriptions
                                    short_desc = task_desc[:50] + "..." if len(task_desc) > 50 else task_desc
                                    st.markdown(f"- **{short_desc}** (ID: `{task_id}`)")
                                else:
                                    st.markdown(f"- Task ID: `{task_id}`")
                    
                    # Display crew log content
                    st.markdown("### Crew Log")
                    crew_log = extract_crew_log_content(log_content, selected_crew_id)
                    st.code(crew_log, language="text")
                    
                    # Display crew metrics
                    if selected_crew.get("total_cost") > 0:
                        st.markdown("### Crew Metrics")
                        st.markdown(f"**Total Cost:** ${selected_crew['total_cost']:.6f}")
                        st.markdown(f"**Number of API Calls:** {len(selected_crew.get('costs', []))}")
                        
                        if selected_crew.get("llm_models"):
                            st.markdown("**LLM Models Used:**")
                            for model in selected_crew["llm_models"]:
                                st.markdown(f"- {model}")
        else:
            st.info("No crews found in the log file.")
