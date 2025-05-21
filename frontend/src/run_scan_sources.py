#!/usr/bin/env python3
"""
Wrapper script to run the scan_sources crew with the proper Python path setup.
"""
import os
import sys
from pathlib import Path

# Add the necessary paths to sys.path
project_root = Path(__file__).parent.parent.parent
scan_sources_dir = os.path.join(project_root, "scan_sources")
src_dir = os.path.join(scan_sources_dir, "src")
scan_sources_main_dir = os.path.join(src_dir, "scan_sources")

# Add paths to sys.path if they're not already there
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(scan_sources_dir))
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(scan_sources_main_dir))

# Import and run the main function directly
sys.path.insert(0, os.path.join(src_dir, "scan_sources"))

# Import the main module directly
scan_sources_main_path = os.path.join(src_dir, "scan_sources", "main.py")
if not os.path.exists(scan_sources_main_path):
    print(f"Error: Could not find main.py at {scan_sources_main_path}")
    sys.exit(1)

# Use importlib to import the module from file path
import importlib.util
spec = importlib.util.spec_from_file_location("main", scan_sources_main_path)
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)

# Get the kickoff function
kickoff = main_module.kickoff

if __name__ == "__main__":
    # Check if a config file exists and print a message
    config_path = os.path.join(project_root, "temp_config.json")
    if os.path.exists(config_path):
        print(f"Using configuration from: {config_path}")
    
    # Run the scan_sources crew
    print("Starting Scan Sources crew...")
    kickoff()
    print("Scan Sources crew completed.")
