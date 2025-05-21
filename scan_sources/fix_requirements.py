#!/usr/bin/env python3
"""
Requirements Fixer for CrewAI Application

This script specifically addresses known dependency conflicts in the requirements.txt file,
particularly the embedchain vs chromadb conflict.
"""

import os
import sys
import tempfile
import subprocess
from pathlib import Path

def run_command(cmd, shell=False):
    """Run a command and return its output."""
    if shell:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, executable="/bin/bash")
    else:
        result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"Error running command: {cmd}")
        print(f"Error: {result.stderr}")
        return None
    return result.stdout

def fix_embedchain_chromadb_conflict():
    """Fix the conflict between embedchain and chromadb."""
    print("🔧 Fixing embedchain vs chromadb conflict...")
    
    # Read the current requirements
    with open("requirements.txt", "r") as f:
        requirements = f.readlines()
    
    # Look for the conflicting packages
    embedchain_line = None
    chromadb_line = None
    
    for i, line in enumerate(requirements):
        if line.strip().startswith("embedchain=="):
            embedchain_line = (i, line.strip())
        elif line.strip().startswith("chromadb=="):
            chromadb_line = (i, line.strip())
    
    if not embedchain_line or not chromadb_line:
        print("⚠️ Could not find both embedchain and chromadb in requirements.txt")
        return False
    
    print(f"Found {embedchain_line[1]} and {chromadb_line[1]}")
    
    # Create a backup
    with open("requirements.backup.txt", "w") as f:
        f.writelines(requirements)
    
    print("✅ Created backup at requirements.backup.txt")
    
    # Fix the conflict by downgrading chromadb to 0.5.10
    requirements[chromadb_line[0]] = "chromadb==0.5.10\n"
    
    # Write the fixed requirements
    with open("requirements.fixed.txt", "w") as f:
        f.writelines(requirements)
    
    print("✅ Created fixed requirements at requirements.fixed.txt")
    
    # Test if the fixed requirements work
    with tempfile.TemporaryDirectory() as temp_dir:
        venv_path = os.path.join(temp_dir, "venv")
        
        # Create a virtual environment
        if run_command(["uv", "venv", venv_path]) is None:
            print("⚠️ Failed to create virtual environment")
            return False
        
        # Determine the activate script path
        if sys.platform == "win32":
            activate_script = os.path.join(venv_path, "Scripts", "activate")
        else:
            activate_script = os.path.join(venv_path, "bin", "activate")
        
        # Try to install the fixed requirements
        fixed_requirements_path = Path("requirements.fixed.txt").absolute()
        cmd = f"source {activate_script} && uv pip install -r {fixed_requirements_path}"
        
        if run_command(cmd, shell=True) is None:
            print("⚠️ Fixed requirements still have conflicts")
            return False
        
        print("✅ Fixed requirements work correctly!")
    
    # Ask to apply the fix
    print("\nDo you want to apply the fix to requirements.txt? (y/n)")
    choice = input().strip().lower()
    
    if choice == 'y':
        with open("requirements.txt", "w") as f:
            f.writelines(requirements)
        print("✅ Applied fix to requirements.txt")
        return True
    else:
        print("❌ Fix not applied. You can manually copy requirements.fixed.txt to requirements.txt")
        return False

def main():
    print("🔍 CrewAI Requirements Fixer")
    print("This tool fixes known dependency conflicts in your requirements.txt file.")
    
    fix_embedchain_chromadb_conflict()

if __name__ == "__main__":
    main()
