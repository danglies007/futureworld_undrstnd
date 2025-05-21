#!/usr/bin/env python3
"""
Requirements Updater for CrewAI Application

This script helps manage requirements.txt for deployment by:
1. Comparing pip and uv requirements
2. Identifying critical packages
3. Creating a clean, deployment-ready requirements file
"""

import os
import subprocess
import sys
from pathlib import Path
import tempfile
import shutil
import argparse
from typing import List, Dict, Set, Tuple

# Critical packages that must be correctly versioned
CRITICAL_PACKAGES = [
    "crewai",
    "litellm",
    "openai",
    "agentops",
    "pandas",
    "numpy",
    "torch",
    "transformers",
    "langchain",
    "pydantic"
]

def run_command(cmd: List[str]) -> str:
    """Run a command and return its output."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error running command: {' '.join(cmd)}")
        print(f"Error: {result.stderr}")
        sys.exit(1)
    return result.stdout

def get_pip_requirements() -> Dict[str, str]:
    """Get requirements from pip freeze."""
    output = run_command(["pip", "freeze"])
    return parse_requirements_output(output)

def get_uv_requirements() -> Dict[str, str]:
    """Get requirements directly from the current environment using uv pip list."""
    # Check if uv is installed
    try:
        subprocess.run(["uv", "--version"], capture_output=True)
    except FileNotFoundError:
        print("UV is not installed. Installing UV...")
        run_command(["pip", "install", "uv"])
    
    # Get the actual UV list from the current environment
    try:
        print("Getting package list directly from UV in the current environment...")
        output = run_command(["uv", "pip", "list", "--format=freeze"])
        if not output:
            print("⚠️ Failed to get UV pip list. Falling back to standard pip.")
            return get_pip_requirements()
            
        # Convert UV pip list format to requirements format
        return parse_requirements_output(output)
    except Exception as e:
        print(f"⚠️ Error getting UV requirements: {e}")
        print("Falling back to pip requirements...")
        return get_pip_requirements()
    
    # If we want to also check for conflicts, we can use this approach
    def check_for_conflicts():
        # Read requirements file
        requirements_path = Path("requirements.txt").absolute()
        with open(requirements_path, 'r') as f:
            requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        # Check for known conflicts
        chromadb_version = None
        embedchain_version = None
        
        for req in requirements:
            if req.startswith("chromadb=="):
                chromadb_version = req.split("==")[1]
            elif req.startswith("embedchain=="):
                embedchain_version = req.split("==")[1]
        
        if chromadb_version and embedchain_version:
            if chromadb_version.startswith("0.6") and embedchain_version == "0.1.125":
                print("\n⚠️ Detected conflict: embedchain==0.1.125 requires chromadb<0.6.0")
                print("  Solution: Run ./fix_requirements.py to fix this conflict")
    
    # Optionally check for conflicts
    check_for_conflicts()

def parse_requirements_output(output: str) -> Dict[str, str]:
    """Parse requirements output into a dictionary of package:version."""
    requirements = {}
    for line in output.strip().split("\n"):
        if not line or line.startswith("#"):
            continue
        
        # Handle direct references (git+, http://, etc.)
        if "==" not in line and line.startswith(("git+", "http://", "https://")):
            # Just store the whole line as both key and value
            requirements[line] = line
            continue
            
        # Handle normal package==version format
        try:
            package, version = line.split("==", 1)
            requirements[package.lower()] = version
        except ValueError:
            # Handle packages without version specifiers
            requirements[line.lower()] = ""
            
    return requirements

def generate_merged_requirements(pip_reqs: Dict[str, str], uv_reqs: Dict[str, str]) -> str:
    """Generate a merged requirements file content, preferring UV versions for critical packages."""
    merged_reqs = {}
    
    # Start with pip requirements
    merged_reqs.update(pip_reqs)
    
    # Override with UV versions for critical packages
    for package in CRITICAL_PACKAGES:
        package_lower = package.lower()
        if package_lower in uv_reqs:
            if package_lower in merged_reqs:
                print(f"Using UV version for {package}: {uv_reqs[package_lower]} (was: {merged_reqs.get(package_lower, 'not specified')})")
            else:
                print(f"Adding UV version for {package}: {uv_reqs[package_lower]}")
            merged_reqs[package_lower] = uv_reqs[package_lower]
    
    # Generate the requirements file content
    content = []
    for package, version in sorted(merged_reqs.items()):
        if version:
            content.append(f"{package}=={version}")
        else:
            content.append(package)
    
    return "\n".join(content)

def compare_requirements(pip_reqs: Dict[str, str], uv_reqs: Dict[str, str]) -> Tuple[Set[str], Set[str], Dict[str, Tuple[str, str]]]:
    """Compare pip and UV requirements."""
    pip_packages = set(pip_reqs.keys())
    uv_packages = set(uv_reqs.keys())
    
    # Packages only in pip
    only_in_pip = pip_packages - uv_packages
    
    # Packages only in UV
    only_in_uv = uv_packages - pip_packages
    
    # Packages with different versions
    different_versions = {}
    for package in pip_packages & uv_packages:
        if pip_reqs[package] != uv_reqs[package]:
            different_versions[package] = (pip_reqs[package], uv_reqs[package])
    
    return only_in_pip, only_in_uv, different_versions

def main():
    parser = argparse.ArgumentParser(description="Update requirements.txt for deployment")
    parser.add_argument("--apply", action="store_true", help="Apply changes to requirements.txt")
    parser.add_argument("--output", default="requirements.merged.txt", help="Output file for merged requirements")
    args = parser.parse_args()
    
    print("🔍 Analyzing requirements...")
    
    # Get requirements from pip and UV
    print("Getting requirements from pip...")
    pip_reqs = get_pip_requirements()
    
    print("Getting requirements from UV...")
    uv_reqs = get_uv_requirements()
    
    # Compare requirements
    only_in_pip, only_in_uv, different_versions = compare_requirements(pip_reqs, uv_reqs)
    
    print("\n📊 Requirements Analysis:")
    print(f"Total packages in pip: {len(pip_reqs)}")
    print(f"Total packages in UV: {len(uv_reqs)}")
    
    if only_in_pip:
        print(f"\n⚠️ {len(only_in_pip)} packages only in pip (not in UV):")
        for package in sorted(only_in_pip):
            print(f"  - {package}=={pip_reqs[package]}")
    
    if only_in_uv:
        print(f"\n🆕 {len(only_in_uv)} packages only in UV (not in pip):")
        for package in sorted(only_in_uv):
            print(f"  - {package}=={uv_reqs[package]}")
    
    if different_versions:
        print(f"\n⚠️ {len(different_versions)} packages with different versions:")
        for package, (pip_version, uv_version) in sorted(different_versions.items()):
            print(f"  - {package}: pip=={pip_version}, uv=={uv_version}")
    
    # Check critical packages
    print("\n🔑 Critical package versions:")
    for package in CRITICAL_PACKAGES:
        package_lower = package.lower()
        pip_version = pip_reqs.get(package_lower, "not found")
        uv_version = uv_reqs.get(package_lower, "not found")
        print(f"  - {package}: pip=={pip_version}, uv=={uv_version}")
    
    # Generate merged requirements
    merged_content = generate_merged_requirements(pip_reqs, uv_reqs)
    
    # Write to output file
    output_path = args.output
    with open(output_path, "w") as f:
        f.write(merged_content)
    
    print(f"\n✅ Generated merged requirements file: {output_path}")
    
    if args.apply:
        # Backup original requirements
        backup_path = "requirements.backup.txt"
        shutil.copy("requirements.txt", backup_path)
        print(f"✅ Backed up original requirements to: {backup_path}")
        
        # Apply changes
        shutil.copy(output_path, "requirements.txt")
        print("✅ Updated requirements.txt with merged requirements")
    else:
        print("\nTo apply these changes, run with --apply flag or manually copy the file:")
        print(f"cp {output_path} requirements.txt")

if __name__ == "__main__":
    main()
