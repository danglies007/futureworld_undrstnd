#!/usr/bin/env python3
"""
Wrapper script to run the competitor_analysis crew with the proper Python path setup.
"""
import os
import sys
from pathlib import Path

# Add the necessary paths to sys.path
project_root = Path(__file__).parent.parent.parent
scan_sources_dir = os.path.join(project_root, "scan_sources")
src_dir = os.path.join(scan_sources_dir, "src")
competitor_analysis_dir = os.path.join(src_dir, "competitor_analysis")

# Add paths to sys.path if they're not already there
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(scan_sources_dir))
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(competitor_analysis_dir))

# Import the main module directly
competitor_analysis_main_path = os.path.join(src_dir, "competitor_analysis", "main.py")
if not os.path.exists(competitor_analysis_main_path):
    print(f"Error: Could not find main.py at {competitor_analysis_main_path}")
    sys.exit(1)

# Use importlib to import the module from file path
import importlib.util
spec = importlib.util.spec_from_file_location("main", competitor_analysis_main_path)
main_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(main_module)

# Get the kickoff function
kickoff = main_module.kickoff

if __name__ == "__main__":
    # Check if a config file exists and print a message
    config_path = os.path.join(project_root, "temp_competitor_config.json")
    if os.path.exists(config_path):
        print(f"Using configuration from: {config_path}")
    
    # Run the competitor_analysis crew
    print("Starting Competitor Analysis crew...")
    kickoff()
    print("Competitor Analysis crew completed.")
