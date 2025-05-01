#!/usr/bin/env python
"""
Setup script for creating the data directory structure for the AI Economic News Agent.
"""

import os
import sys
from datetime import datetime

# Define the data directory structure
DATA_DIRS = [
    "data/articles",
    "data/processed",
    "data/logs",
    "data/exports/markdown",
    "data/exports/json",
]

def main():
    """Create the data directory structure."""
    print("\n=== Setting up AI Economic News Agent data directories ===\n")
    
    # Get the project root directory
    project_root = os.path.abspath(os.path.dirname(__file__))
    
    # Create each directory
    for dir_path in DATA_DIRS:
        full_path = os.path.join(project_root, dir_path)
        
        if not os.path.exists(full_path):
            try:
                os.makedirs(full_path)
                print(f"Created directory: {dir_path}")
            except Exception as e:
                print(f"Error creating directory {dir_path}: {str(e)}")
        else:
            print(f"Directory already exists: {dir_path}")
    
    # Create a .gitkeep file in each directory to ensure it's tracked by git
    for dir_path in DATA_DIRS:
        full_path = os.path.join(project_root, dir_path, ".gitkeep")
        
        if not os.path.exists(full_path):
            try:
                with open(full_path, "w") as f:
                    f.write(f"# This file ensures the {dir_path} directory is tracked by git\n")
                print(f"Created .gitkeep in: {dir_path}")
            except Exception as e:
                print(f"Error creating .gitkeep in {dir_path}: {str(e)}")
    
    # Create a README file in the data directory
    readme_path = os.path.join(project_root, "data", "README.md")
    if not os.path.exists(readme_path):
        try:
            with open(readme_path, "w") as f:
                f.write("""# Data Directory

This directory contains data files used by the AI Economic News Agent.

## Structure

- `articles/`: Stored article content
- `processed/`: Processed and analyzed data
- `logs/`: Log files
- `exports/`: Exported findings
  - `markdown/`: Markdown format exports
  - `json/`: JSON format exports

Note: The contents of this directory are not tracked by git (except for .gitkeep files).
""")
            print("Created README.md in data directory")
        except Exception as e:
            print(f"Error creating README.md: {str(e)}")
    
    print("\nSetup complete!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
