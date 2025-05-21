#!/usr/bin/env python3
"""
Log Analyzer for LiteLLM and CrewAI Logs

A simple command-line utility for analyzing process logs to extract metrics like:
- LLM models used
- Cost information
- Timing information for tasks and crews
- Token usage

Usage:
  python log_analyzer.py <log_file_path>
  
Example:
  python log_analyzer.py /path/to/logs/process_output_20250519_163138.log
"""

import re
import os
import sys
import json
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union, Set
from collections import defaultdict


def extract_timing_info(log_content: str) -> Dict[str, Any]:
    """Extract process start and end times from the log."""
    timing_info = {
        "start_time": None,
        "end_time": None,
        "duration": None
    }
    
    # Extract start time
    start_match = re.search(r"Start Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", log_content)
    if start_match:
        start_time_str = start_match.group(1)
        timing_info["start_time"] = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
    
    # Extract end time
    end_match = re.search(r"End Timestamp: (\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})", log_content)
    if end_match:
        end_time_str = end_match.group(1)
        timing_info["end_time"] = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
        
    # Calculate duration if both start and end times are available
    if timing_info["start_time"] and timing_info["end_time"]:
        timing_info["duration"] = (timing_info["end_time"] - timing_info["start_time"]).total_seconds()
        
    return timing_info


def format_duration(seconds: float) -> str:
    """Format a duration in seconds into a human-readable string."""
    if seconds is None:
        return "Unknown duration"
    
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    
    if hours > 0:
        return f"{int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"
    elif minutes > 0:
        return f"{int(minutes)} minutes, {int(seconds)} seconds"
    else:
        return f"{int(seconds)} seconds"


def format_time_delta(delta: timedelta) -> str:
    """Format a timedelta object into a human-readable string."""
    total_seconds = delta.total_seconds()
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    
    if hours > 0:
        return f"{int(hours)} hours, {int(minutes)} minutes, {int(seconds)} seconds"
    elif minutes > 0:
        return f"{int(minutes)} minutes, {int(seconds)} seconds"
    else:
        return f"{int(seconds)} seconds"


def extract_llm_usage(log_content: str) -> List[Dict[str, str]]:
    """Extract LLM usage information from the log."""
    llm_usage = []
    
    # Pattern to match LLM completion calls
    llm_pattern = r"LiteLLM completion\(\) model=\s*([^\s;]+);\s*provider\s*=\s*([^\s]+)"
    
    # Find all matches
    for match in re.finditer(llm_pattern, log_content):
        model = match.group(1)
        provider = match.group(2)
        
        # Add to metrics if not already present
        llm_entry = {"model": model, "provider": provider}
        if llm_entry not in llm_usage:
            llm_usage.append(llm_entry)
    
    return llm_usage


def extract_cost_info(log_content: str) -> Dict[str, Any]:
    """Extract cost information from the log."""
    cost_info = {
        "costs": [],
        "total_cost": 0.0
    }
    
    # Pattern to match cost information
    cost_pattern = r"response_cost:\s*([\d.]+)"
    
    # Find all matches
    for match in re.finditer(cost_pattern, log_content):
        cost = float(match.group(1))
        cost_info["costs"].append(cost)
        cost_info["total_cost"] += cost
    
    return cost_info


def extract_task_info(log_content: str) -> List[Dict[str, Any]]:
    """Extract detailed task information from the log."""
    tasks = []
    task_data = {}
    
    # First, extract overall LLM usage and costs
    overall_llm_usage = extract_llm_usage(log_content)
    overall_cost_info = extract_cost_info(log_content)
    
    # Pattern to match task IDs and names
    task_id_pattern = r"📋 Task: ([a-f0-9\-]+)\s*\n.*Status: ([^\n]+)"
    task_name_pattern = r"## Task:[^\n]*\n([^\n]+)"
    
    # Additional patterns to extract task names from specific log formats
    task_name_patterns = [
        r"Your goal is to discover ([^\n\.]+) for further evaluation",  # Source Discovery
        r"Your goal is to analyze ([^\n\.]+) and provide",              # Analysis
        r"Your goal is to ([^\n\.]+)",                                 # Generic goal
        r"GOAL: ([^\n\.]+)",                                          # Direct goal
        r"Task: ([^\n\.]+) \(ID: [a-f0-9\-]+\)",                     # Task with ID
        r"\[95m## Task:\[00m \[92m([^\n]+)\[00m"                      # Colored task
    ]
    
    # Additional patterns to extract task names and descriptions
    additional_task_patterns = [
        r"Task Name: ([^\n]+)",                   # Direct task name
        r"Task Description: ([^\n]+)",            # Task description
        r"GOAL: ([^\n]+)",                        # Task goal
        r"Your goal is to ([^\n\.]+)",            # Goal statement format
        r"\[95m## Task:\[00m \[92m([^\n]+)\[00m",  # Color-coded task format
        r"Task: ([^\n]+) \(ID: [a-f0-9\-]+\)",   # Task with ID format
        r"Executing task: ([^\n]+)",              # Executing task format
        r"Running task: ([^\n]+)",                # Running task format
        r"discover ([^\n\.]+) from",              # Discovery task pattern
        r"analyze ([^\n\.]+) for",               # Analysis task pattern
        r"evaluate ([^\n\.]+) based",             # Evaluation task pattern
        r"generate ([^\n\.]+) using",             # Generation task pattern
        r"Task: ([^\n]+)"                         # Simple task format
    ]
    
    # Patterns to extract task goals
    goal_patterns = [
        r"Your goal is to ([^\n\.]+)",            # Standard goal format
        r"Goal: ([^\n\.]+)",                      # Simple goal format
        r"The goal is to ([^\n\.]+)",             # Alternative goal format
        r"Task goal: ([^\n\.]+)",                 # Task goal format
        r"Objective: ([^\n\.]+)"                  # Objective format
    ]
    task_start_pattern = r"Task Started: ([^\n]+)"
    task_end_pattern = r"Task Completed: ([^\n]+)"
    
    # Find all task IDs
    for match in re.finditer(task_id_pattern, log_content):
        task_id = match.group(1).strip()
        task_status = match.group(2).strip()
        
        if task_id not in task_data:
            # Initialize with default values
            task_data[task_id] = {
                "id": task_id,
                "status": task_status,
                "name": "",
                "description": "",
                "start_time": None,
                "end_time": None,
                "duration": None,
                "agents": [],
                "llm_models": set(),
                "costs": [],
                "total_cost": 0.0
            }
            
            # Add default LLM models from overall metrics if we don't have task-specific data
            if overall_llm_usage:
                for llm_info in overall_llm_usage:
                    model_name = llm_info.get('model')
                    if model_name:
                        task_data[task_id]["llm_models"].add(model_name)
            
            # Add default cost from overall metrics divided by number of tasks
            if overall_cost_info and overall_cost_info.get("total_cost", 0) > 0:
                # Count the number of tasks
                task_count = len(re.findall(r"📋 Task: ([a-f0-9\-]+)", log_content))
                if task_count == 0:
                    task_count = 1  # Avoid division by zero
                
                # Distribute cost evenly among tasks as a fallback
                task_data[task_id]["total_cost"] = overall_cost_info.get("total_cost", 0) / task_count
                task_data[task_id]["costs"] = [task_data[task_id]["total_cost"]]
    
    # Find task descriptions using the main pattern
    for match in re.finditer(task_name_pattern, log_content):
        task_desc = match.group(1).strip()
        # Associate with the most recently mentioned task ID
        if task_data and task_desc:
            latest_task_id = list(task_data.keys())[-1]
            task_data[latest_task_id]["description"] = task_desc
    
    # Look for task names and descriptions using additional patterns
    for task_id, data in task_data.items():
        # Look for task section in the log - properly fixed escape sequence
        task_section = re.search(f"Task: {task_id}.*?(?=Task: [a-f0-9\\-]+|$)", log_content, re.DOTALL)
        if task_section:
            task_content = task_section.group(0)
            
            # Try each pattern to find task name/description
            for pattern in additional_task_patterns:
                match = re.search(pattern, task_content)
                if match:
                    name_or_desc = match.group(1).strip()
                    if name_or_desc:
                        # If we don't have a name yet, use this as the name
                        if not data["name"]:
                            data["name"] = name_or_desc
                        # Otherwise, if we don't have a description, use this as the description
                        elif not data["description"]:
                            data["description"] = name_or_desc
                        # If we already have both, prefer to update the name as it's more important
                        else:
                            data["name"] = name_or_desc
            
            # Look for task goals specifically
            for pattern in goal_patterns:
                match = re.search(pattern, task_content)
                if match:
                    goal = match.group(1).strip()
                    if goal:
                        # If we don't have a description yet, use the goal as the description
                        if not data["description"]:
                            data["description"] = f"Goal: {goal}"
                        # If we already have a description but no name, use the goal as the name
                        elif not data["name"]:
                            data["name"] = f"Goal: {goal}"
                        # Otherwise, append the goal to the description
                        else:
                            data["description"] += f" | Goal: {goal}"
            
            # Look for specific task types using the task name patterns
            if not data["name"]:
                for pattern in task_name_patterns:
                    match = re.search(pattern, task_content)
                    if match:
                        task_name = match.group(1).strip()
                        if task_name:
                            # Format the task name based on the pattern
                            if "discover" in pattern:
                                data["name"] = f"Discover {task_name}"
                            elif "analyze" in pattern:
                                data["name"] = f"Analyze {task_name}"
                            else:
                                data["name"] = task_name
                            break
    
    # Extract task timing information
    for task_id, data in task_data.items():
        # Look for timing information related to this task - properly fixed escape sequence
        task_section = re.search(f"Task: {task_id}.*?(?=Task: [a-f0-9\\-]+|$)", log_content, re.DOTALL)
        if task_section:
            task_content = task_section.group(0)
            
            # Extract task name/description if not already set
            if not data["name"] and not data["description"]:
                # Try to find task name or description in the task content
                task_name_match = re.search(r"Task Name: ([^\n]+)", task_content)
                if task_name_match:
                    data["name"] = task_name_match.group(1).strip()
                
                # Look for task description or goal
                task_desc_match = re.search(r"GOAL: ([^\n]+)", task_content)
                if task_desc_match:
                    data["description"] = task_desc_match.group(1).strip()
                else:
                    # Try alternative patterns for task description
                    alt_desc_match = re.search(r"Description: ([^\n]+)", task_content)
                    if alt_desc_match:
                        data["description"] = alt_desc_match.group(1).strip()
            
            # Extract start time
            start_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[^\n]*Task[^\n]*Start", task_content)
            if start_match:
                start_time_str = start_match.group(1)
                data["start_time"] = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            else:
                # Try alternative pattern for start time
                alt_start_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[^\n]*Executing Task", task_content)
                if alt_start_match:
                    start_time_str = alt_start_match.group(1)
                    data["start_time"] = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            
            # Extract end time
            end_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[^\n]*Task[^\n]*Complet", task_content)
            if end_match:
                end_time_str = end_match.group(1)
                data["end_time"] = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
            
            # Calculate duration
            if data["start_time"] and data["end_time"]:
                data["duration"] = (data["end_time"] - data["start_time"]).total_seconds()
            
            # Extract agent information - improved patterns with color codes
            agent_patterns = [
                r"🤖 Agent: ([^\n]+)",                  # Standard emoji pattern
                r"Agent: ([^\n]+)",                         # Simple agent pattern
                r"\[1m\[92m# Agent:\[00m \[1m\[92m([^\n]+)\[00m",  # Color-coded agent pattern
                r"Using agent: ([^\n]+)",                   # Using agent format
                r"Agent ([^\n]+) is working on",            # Working on format
                r"([^\n]+) \(Agent\)",                     # Name (Agent) format
                r"Running agent ([^\n]+)",                  # Running agent format
                r"Source Discovery Specialist",             # Specific agent name
                r"Content Analysis Specialist",             # Specific agent name
                r"Research Coordinator"                      # Specific agent name
            ]
            
            # Dictionary to store agent details
            agent_details = {}
            
            for pattern in agent_patterns:
                # Handle patterns with capture groups
                if "(" in pattern and ")" in pattern:
                    for agent_match in re.finditer(pattern, task_content):
                        agent_name = agent_match.group(1).strip()
                        if agent_name and agent_name not in data["agents"]:
                            data["agents"].append(agent_name)
                            agent_details[agent_name] = {"name": agent_name}
                # Handle specific agent names without capture groups
                else:
                    if re.search(pattern, task_content):
                        agent_name = pattern.strip()
                        if agent_name and agent_name not in data["agents"]:
                            data["agents"].append(agent_name)
                            agent_details[agent_name] = {"name": agent_name}
            
            # Look for agent roles and descriptions
            for agent_name in data["agents"]:
                # Look for role information
                role_pattern = f"{re.escape(agent_name)}.*?role: ([^\n,]+)"
                role_match = re.search(role_pattern, task_content, re.IGNORECASE)
                if role_match:
                    role = role_match.group(1).strip()
                    if agent_name not in agent_details:
                        agent_details[agent_name] = {"name": agent_name}
                    agent_details[agent_name]["role"] = role
                
                # Look for goal information
                goal_pattern = f"{re.escape(agent_name)}.*?goal: ([^\n]+)"
                goal_match = re.search(goal_pattern, task_content, re.IGNORECASE)
                if goal_match:
                    goal = goal_match.group(1).strip()
                    if agent_name not in agent_details:
                        agent_details[agent_name] = {"name": agent_name}
                    agent_details[agent_name]["goal"] = goal
            
            # Store detailed agent information
            data["agent_details"] = list(agent_details.values())
            
            # Extract LLM usage within this task section - improved pattern
            llm_patterns = [
                r"LiteLLM completion\(\) model=\s*([^\s;]+);",  # Standard pattern
                r"Using model: ([^\s;\n]+)",                    # Alternative pattern
                r"model=([^,\s]+),",                          # Another alternative
                r"model='([^']+)'",                           # Quoted model name
                r'model="([^"]+)"',                           # Double-quoted model name
                r"Using (gpt-[\w.-]+)",                        # Direct model mention
                r"(gpt-[\w.-]+) \(Provider: [\w]+\)"           # Model with provider
            ]
            
            for pattern in llm_patterns:
                for llm_match in re.finditer(pattern, task_content):
                    model = llm_match.group(1).strip('"').strip("'").strip()
                    if model:  # Only add non-empty models
                        data["llm_models"].add(model)
            
            # Extract cost information within this task section - improved patterns
            cost_patterns = [
                r"response_cost:\s*([\d.]+)",                # Standard pattern
                r"Total cost: \$([\d.]+)",                   # Alternative pattern
                r"Cost: \$([\d.]+)",                        # Another alternative
                r"cost=([\d.]+)",                           # Simple cost parameter
                r"total_cost: ([\d.]+)",                    # Total cost field
                r"completion_cost: ([\d.]+)",               # Completion cost
                r"cost: ([\d.]+)"                           # Generic cost field
            ]
            
            for pattern in cost_patterns:
                for cost_match in re.finditer(pattern, task_content):
                    try:
                        cost = float(cost_match.group(1))
                        if cost > 0:  # Only add positive costs
                            data["costs"].append(cost)
                            data["total_cost"] += cost
                    except (ValueError, IndexError):
                        pass  # Skip invalid cost values
            
            # Extract token usage information
            token_patterns = [
                r"completion_tokens: (\d+)",
                r"prompt_tokens: (\d+)",
                r"total_tokens: (\d+)"
            ]
            
            token_counts = {
                "completion_tokens": 0,
                "prompt_tokens": 0,
                "total_tokens": 0
            }
            
            for pattern in token_patterns:
                for token_match in re.finditer(pattern, task_content):
                    try:
                        token_type = pattern.split(':')[0].strip('r" ')
                        token_count = int(token_match.group(1))
                        token_counts[token_type] += token_count
                    except (ValueError, IndexError, KeyError):
                        pass  # Skip invalid token values
            
            # Add token counts to task data
            data["token_usage"] = token_counts
    
    # Convert task_data dictionary to list
    for task_id, data in task_data.items():
        # Convert set to list for JSON serialization
        data["llm_models"] = list(data["llm_models"])
        tasks.append(data)
    
    return tasks


def extract_config_info(log_content: str) -> Dict[str, Any]:
    """
    Extract configuration information from the log.
    
    This function looks for references to the config file in the log,
    then attempts to read that file to extract the configuration variables
    that were used for the run.
    
    Args:
        log_content: The content of the log file
        
    Returns:
        Dictionary containing configuration variables
    """
    config_info = {}
    
    # Look for the config file path in the log
    config_path_match = re.search(r"Using configuration from: ([^\n]+)", log_content)
    if not config_path_match:
        return config_info
    
    config_path = config_path_match.group(1).strip()
    
    # Check if the config file exists
    if not os.path.exists(config_path):
        return config_info
    
    # Read the config file
    try:
        with open(config_path, 'r') as f:
            config_data = json.load(f)
            return config_data
    except Exception as e:
        # If we can't read the config file, just return an empty dict
        return config_info


def extract_crew_info(log_content: str) -> List[Dict[str, Any]]:
    """Extract detailed crew information from the log."""
    crews = []
    crew_data = {}
    
    # Pattern to match crew IDs and names
    crew_id_pattern = r"Crew Execution Started[\s\S]*?ID: ([a-f0-9\-]+)"
    crew_name_pattern = r"Name: ([^\n]+)\s*\n[^\n]*ID: ([a-f0-9\-]+)"
    
    # Find all crew IDs and names
    for match in re.finditer(crew_name_pattern, log_content):
        crew_name = match.group(1).strip()
        crew_id = match.group(2).strip()
        
        if crew_id not in crew_data:
            crew_data[crew_id] = {
                "id": crew_id,
                "name": crew_name,
                "start_time": None,
                "end_time": None,
                "duration": None,
                "tasks": [],
                "agents": [],
                "llm_models": set(),
                "costs": [],
                "total_cost": 0.0
            }
    
    # Extract crew timing information
    for crew_id, data in crew_data.items():
        # Look for crew section in the log - properly fixed escape sequence
        crew_section = re.search(f"ID: {crew_id}.*?(?=Crew Execution Started|$)", log_content, re.DOTALL)
        if crew_section:
            crew_content = crew_section.group(0)
            
            # Extract start time
            start_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[^\n]*Crew[^\n]*Start", crew_content)
            if start_match:
                start_time_str = start_match.group(1)
                data["start_time"] = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            else:
                # Try to find the timestamp at the beginning of the crew section
                start_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[^\n]*Crew Execution Started", crew_content)
                if start_match:
                    start_time_str = start_match.group(1)
                    data["start_time"] = datetime.strptime(start_time_str, "%Y-%m-%d %H:%M:%S")
            
            # Extract end time
            end_match = re.search(r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})[^\n]*Crew[^\n]*Complet", crew_content)
            if end_match:
                end_time_str = end_match.group(1)
                data["end_time"] = datetime.strptime(end_time_str, "%Y-%m-%d %H:%M:%S")
            
            # Calculate duration
            if data["start_time"] and data["end_time"]:
                data["duration"] = (data["end_time"] - data["start_time"]).total_seconds()
            
            # Extract task IDs associated with this crew
            task_pattern = r"📋 Task: ([a-f0-9\-]+)"
            for task_match in re.finditer(task_pattern, crew_content):
                task_id = task_match.group(1).strip()
                if task_id not in data["tasks"]:
                    data["tasks"].append(task_id)
            
            # Extract agent information
            agent_pattern = r"🤖 Agent: ([^\n]+)"
            for agent_match in re.finditer(agent_pattern, crew_content):
                agent_name = agent_match.group(1).strip()
                if agent_name not in data["agents"]:
                    data["agents"].append(agent_name)
            
            # Extract LLM usage within this crew section
            llm_pattern = r"LiteLLM completion\(\) model=\s*([^\s;]+);"
            for llm_match in re.finditer(llm_pattern, crew_content):
                model = llm_match.group(1)
                data["llm_models"].add(model)
            
            # Extract cost information within this crew section
            cost_pattern = r"response_cost:\s*([\d.]+)"
            for cost_match in re.finditer(cost_pattern, crew_content):
                cost = float(cost_match.group(1))
                data["costs"].append(cost)
                data["total_cost"] += cost
    
    # Convert crew_data dictionary to list
    for crew_id, data in crew_data.items():
        # Convert set to list for JSON serialization
        data["llm_models"] = list(data["llm_models"])
        crews.append(data)
    
    return crews


def analyze_log_file(log_file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Analyze a log file and extract metrics.
    
    Args:
        log_file_path: Path to the log file to analyze
        
    Returns:
        Dictionary containing extracted metrics
    """
    if isinstance(log_file_path, str):
        log_file_path = Path(log_file_path)
    
    if not log_file_path.exists():
        raise FileNotFoundError(f"Log file not found: {log_file_path}")
    
    # Read log content
    with open(log_file_path, 'r') as f:
        log_content = f.read()
    
    # Extract metrics
    tasks = extract_task_info(log_content)
    crews = extract_crew_info(log_content)
    
    # Create task ID to task data mapping for easier lookup
    task_map = {task["id"]: task for task in tasks}
    
    # Associate tasks with crews
    for crew in crews:
        crew["task_details"] = []
        for task_id in crew["tasks"]:
            if task_id in task_map:
                crew["task_details"].append(task_map[task_id])
    
    # Extract configuration information
    config_info = extract_config_info(log_content)
    
    metrics = {
        "timing": extract_timing_info(log_content),
        "llm_usage": extract_llm_usage(log_content),
        "costs": extract_cost_info(log_content),
        "tasks": tasks,
        "crews": crews,
        "config": config_info
    }
    
    return metrics


def generate_summary(metrics: Dict[str, Any]) -> str:
    """
    Generate a human-readable summary of the metrics.
    
    Args:
        metrics: Dictionary of metrics from analyze_log_file
        
    Returns:
        String containing the summary
    """
    summary = []
    summary.append("=== Log Analysis Summary ===")
    
    # Add timing information
    timing = metrics["timing"]
    if timing["start_time"]:
        summary.append(f"Start Time: {timing['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    if timing["end_time"]:
        summary.append(f"End Time: {timing['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    if timing["duration"]:
        minutes, seconds = divmod(timing["duration"], 60)
        summary.append(f"Duration: {int(minutes)} minutes, {int(seconds)} seconds")
    
    # Add LLM usage information
    if metrics["llm_usage"]:
        summary.append("\nLLM Models Used:")
        for llm in metrics["llm_usage"]:
            summary.append(f"- {llm['model']} (Provider: {llm['provider']})")
    
    # Add cost information
    costs = metrics["costs"]
    if costs["total_cost"] > 0:
        summary.append(f"\nTotal Cost: ${costs['total_cost']:.6f}")
        if len(costs["costs"]) > 1:
            summary.append(f"Number of API Calls: {len(costs['costs'])}")
            summary.append(f"Average Cost per Call: ${sum(costs['costs']) / len(costs['costs']):.6f}")
    
    # Add crew information
    if metrics["crews"]:
        summary.append("\nCrews Used:")
        for crew in metrics["crews"]:
            crew_name = crew.get("name", "Unknown")
            crew_id = crew.get("id", "Unknown")
            summary.append(f"- {crew_name} (ID: {crew_id})")
    
    # Add task information
    if metrics["tasks"]:
        summary.append("\nTasks Executed:")
        for task in metrics["tasks"]:
            task_desc = task.get("description", "Unknown")
            task_id = task.get("id", "Unknown")
            summary.append(f"- {task_desc} (ID: {task_id})")
    
    return "\n".join(summary)


def generate_detailed_report(metrics: Dict[str, Any]) -> str:
    """
    Generate a detailed report of tasks and crews.
    
    Args:
        metrics: Dictionary of metrics from analyze_log_file
        
    Returns:
        String containing the detailed report
    """
    report = []
    report.append("======================================================")
    report.append("                DETAILED ANALYSIS REPORT              ")
    report.append("======================================================\n")
    
    # Add overall timing information
    timing = metrics["timing"]
    report.append("OVERALL EXECUTION")
    report.append("------------------")
    if timing["start_time"]:
        report.append(f"Start Time: {timing['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    if timing["end_time"]:
        report.append(f"End Time: {timing['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    if timing["duration"]:
        report.append(f"Total Duration: {format_time_delta(timedelta(seconds=timing['duration']))}")
    
    # Add overall cost information
    costs = metrics["costs"]
    if costs["total_cost"] > 0:
        report.append(f"Total Cost: ${costs['total_cost']:.6f}")
        report.append(f"Number of API Calls: {len(costs['costs'])}")
        report.append(f"Average Cost per Call: ${sum(costs['costs']) / len(costs['costs']):.6f}")
    
    # Add LLM usage information
    if metrics["llm_usage"]:
        report.append("\nLLM MODELS USED")
        report.append("-------------")
        for llm in metrics["llm_usage"]:
            report.append(f"- {llm['model']} (Provider: {llm['provider']})")
    
    # Add configuration information
    if "config" in metrics and metrics["config"]:
        report.append("\n\n======================================================")
        report.append("                CONFIGURATION DETAILS                ")
        report.append("======================================================")
        
        config = metrics["config"]
        
        # Add key configuration parameters
        report.append("\nFRONTEND PARAMETERS:")
        report.append("--------------------")
        
        # Topic and business information
        if "topic" in config:
            report.append(f"Topic: {config['topic']}")
        if "topic_short" in config:
            report.append(f"Topic Short Name: {config['topic_short']}")
        if "market" in config:
            report.append(f"Target Market: {config['market']}")
        if "business" in config:
            report.append(f"Business Name: {config['business']}")
        if "audience" in config:
            report.append(f"Target Audience: {config['audience']}")
        if "specialisation" in config:
            report.append(f"Specialisation: {config['specialisation']}")
        
        # Source parameters
        if "minimum_number_of_sources" in config:
            report.append(f"Minimum Number of Sources: {config['minimum_number_of_sources']}")
        if "maximum_number_of_sources" in config:
            report.append(f"Maximum Number of Sources: {config['maximum_number_of_sources']}")
        if "minimum_number_of_forces" in config:
            report.append(f"Minimum Number of Forces: {config['minimum_number_of_forces']}")
        if "source_score_threshold" in config:
            report.append(f"Source Score Threshold: {config['source_score_threshold']}")
        
        # Points of interest
        if "specific_points_of_interest" in config and config["specific_points_of_interest"]:
            report.append("\nSpecific Points of Interest:")
            for point in config["specific_points_of_interest"]:
                if point:  # Only add non-empty points
                    report.append(f"- {point}")
        
        # Research sources
        if "research_sources" in config and config["research_sources"]:
            report.append("\nResearch Sources:")
            for source in config["research_sources"]:
                if source:  # Only add non-empty sources
                    report.append(f"- {source}")
        
        # Date
        if "date" in config:
            report.append(f"\nDate: {config['date']}")
            
        # Other configuration details can be added as needed
    
    # Add crew information
    if metrics["crews"]:
        report.append("\n\n======================================================")
        report.append("                    CREW DETAILS                   ")
        report.append("======================================================")
        
        for crew in metrics["crews"]:
            crew_name = crew.get("name", "Unknown")
            crew_id = crew.get("id", "Unknown")
            report.append(f"\nCREW: {crew_name}")
    
    # Task information
    if "tasks" in metrics and metrics["tasks"]:
        report.append("\n\n======================================================")
        report.append("                    TASK DETAILS                   ")
        report.append("======================================================\n")
        
        for task in metrics["tasks"]:
            task_name = task.get("name", "")
            task_desc = task.get("description", "")
            task_id = task.get("id", "")
            task_status = task.get("status", "")
            
            # Task header with name
            if task_name:
                report.append(f"TASK: {task_name}")
            else:
                report.append(f"TASK: Task {task_id[-8:]}")
            report.append("-" * 60)
            
            # Task details
            report.append(f"ID: {task_id}")
            report.append(f"Status: {task_status}")
            
            # Add description if available and different from name
            if task_desc and task_desc != task_name:
                report.append(f"Description: {task_desc}")
            
            # Add timing information
            if task.get("start_time"):
                report.append(f"Start Time: {task['start_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            if task.get("end_time"):
                report.append(f"End Time: {task['end_time'].strftime('%Y-%m-%d %H:%M:%S')}")
            if task.get("duration") is not None:
                report.append(f"Duration: {format_duration(task['duration'])}")
            
            # Add LLM models used
            if task.get("llm_models"):
                report.append("\nLLM Models Used:")
                for model in sorted(task["llm_models"]):
                    report.append(f"- {model}")
            
            # Add cost information
            if task.get("total_cost", 0) > 0:
                report.append(f"\nTotal Cost: ${task['total_cost']:.6f}")
                report.append(f"Number of API Calls: {len(task.get('costs', []))}")
                if len(task.get('costs', [])) > 0:
                    avg_cost = task['total_cost'] / len(task['costs'])
                    report.append(f"Average Cost per Call: ${avg_cost:.6f}")
            
            # Add token usage
            if task.get("token_usage"):
                report.append("\nToken Usage:")
                for token_type, count in task["token_usage"].items():
                    if count > 0:
                        report.append(f"- {token_type.replace('_', ' ').title()}: {count:,}")
            
            # Add detailed agent information
            if task.get("agents"):
                report.append("\nAgents:")
                
                # Check if we have detailed agent information
                if task.get("agent_details"):
                    for agent_detail in task["agent_details"]:
                        agent_name = agent_detail.get("name", "Unknown Agent")
                        report.append(f"- {agent_name}")
                        
                        # Add role if available
                        if "role" in agent_detail:
                            report.append(f"  Role: {agent_detail['role']}")
                            
                        # Add goal if available
                        if "goal" in agent_detail:
                            report.append(f"  Goal: {agent_detail['goal']}")
                else:
                    # Simple agent list if no details available
                    for agent in task["agents"]:
                        report.append(f"- {agent}")
                        
            # Add a separator between tasks
            report.append("\n" + "-" * 60 + "\n")
    
    return "\n".join(report)


def generate_report_file(metrics: Dict[str, Any], output_path: Union[str, Path]) -> str:
    """
    Generate a detailed report file for tasks and crews.
    
    Args:
        metrics: Dictionary of metrics from analyze_log_file
        output_path: Path to save the report file
        
    Returns:
        Path to the saved report file
    """
    if isinstance(output_path, str):
        output_path = Path(output_path)
    
    # Generate the report
    report = generate_detailed_report(metrics)
    
    # Write to file
    with open(output_path, 'w') as f:
        f.write(report)
        
    return str(output_path)


def export_metrics_json(metrics: Dict[str, Any], output_path: Union[str, Path]) -> str:
    """
    Export metrics to a JSON file.
    
    Args:
        metrics: Dictionary of metrics from analyze_log_file
        output_path: Path to save the JSON file
        
    Returns:
        Path to the saved JSON file
    """
    if isinstance(output_path, str):
        output_path = Path(output_path)
    
    # Prepare metrics for JSON serialization (convert datetime objects to strings)
    json_metrics = {}
    
    # Handle timing info
    json_metrics["timing"] = metrics["timing"].copy()
    if json_metrics["timing"]["start_time"]:
        json_metrics["timing"]["start_time"] = json_metrics["timing"]["start_time"].strftime("%Y-%m-%d %H:%M:%S")
    if json_metrics["timing"]["end_time"]:
        json_metrics["timing"]["end_time"] = json_metrics["timing"]["end_time"].strftime("%Y-%m-%d %H:%M:%S")
    
    # Handle task timing info
    json_metrics["tasks"] = []
    for task in metrics["tasks"]:
        task_copy = task.copy()
        if task_copy.get("start_time"):
            task_copy["start_time"] = task_copy["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        if task_copy.get("end_time"):
            task_copy["end_time"] = task_copy["end_time"].strftime("%Y-%m-%d %H:%M:%S")
        json_metrics["tasks"].append(task_copy)
    
    # Handle crew timing info
    json_metrics["crews"] = []
    for crew in metrics["crews"]:
        crew_copy = crew.copy()
        if crew_copy.get("start_time"):
            crew_copy["start_time"] = crew_copy["start_time"].strftime("%Y-%m-%d %H:%M:%S")
        if crew_copy.get("end_time"):
            crew_copy["end_time"] = crew_copy["end_time"].strftime("%Y-%m-%d %H:%M:%S")
        
        # Handle task_details timing info
        if "task_details" in crew_copy:
            for i, task in enumerate(crew_copy["task_details"]):
                if task.get("start_time"):
                    crew_copy["task_details"][i]["start_time"] = task["start_time"].strftime("%Y-%m-%d %H:%M:%S")
                if task.get("end_time"):
                    crew_copy["task_details"][i]["end_time"] = task["end_time"].strftime("%Y-%m-%d %H:%M:%S")
        
        json_metrics["crews"].append(crew_copy)
    
    # Copy other metrics
    json_metrics["llm_usage"] = metrics["llm_usage"]
    json_metrics["costs"] = metrics["costs"]
    
    # Write to file
    with open(output_path, 'w') as f:
        json.dump(json_metrics, f, indent=2)
        
    return str(output_path)


def main():
    parser = argparse.ArgumentParser(description='Analyze LiteLLM and CrewAI log files')
    parser.add_argument('log_file', help='Path to the log file to analyze')
    parser.add_argument('--json', '-j', help='Export metrics to JSON file', action='store_true')
    parser.add_argument('--report', '-r', help='Generate detailed report file', action='store_true')
    parser.add_argument('--output', '-o', help='Output path for export (default: log_file_path.json or log_file_path.report.log)')
    
    args = parser.parse_args()
    
    try:
        # Analyze log file
        metrics = analyze_log_file(args.log_file)
        
        # Print summary
        print(generate_summary(metrics))
        
        # Export to JSON if requested
        if args.json:
            output_path = args.output or Path(args.log_file).with_suffix('.json')
            json_path = export_metrics_json(metrics, output_path)
            print(f"\nMetrics exported to: {json_path}")
        
        # Generate detailed report if requested
        if args.report:
            output_path = args.output
            if not output_path:
                # Use the original log file name with .report.log extension
                log_path = Path(args.log_file)
                output_path = log_path.with_name(f"{log_path.stem}.report.log")
            report_path = generate_report_file(metrics, output_path)
            print(f"\nDetailed report generated: {report_path}")
            
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
