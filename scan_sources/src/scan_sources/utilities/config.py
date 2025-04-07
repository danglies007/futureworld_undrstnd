"""Configuration module for the Scan Sources CrewAI project.

This module provides a centralized location for all configurable parameters
used throughout the application, making it easier for users to modify settings.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field


class FlowConfig(BaseModel):
    """Configuration model for the Scan Sources application."""
    
    # Basic scan parameters
    target_industry: str = Field(
        default="Banking",
        description="Target industry for the market scan"
    )
    target_market: str = Field(
        default="Global",
        description="Target market for the scan (e.g., Global, US, Europe)"
    )
    time_horizon: str = Field(
        default="5+ years",
        description="Time horizon for the analysis"
    )
    
    # Advanced scan parameters
    max_web_sources: int = Field(
        default=5,
        description="Maximum number of web sources to scan"
    )
    max_document_sources: int = Field(
        default=3,
        description="Maximum number of document sources to scan"
    )
    
    # Output configuration
    output_directory: str = Field(
        default="outputs",
        description="Directory where output files will be saved"
    )
    
    # Additional parameters can be added here as needed
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the configuration to a dictionary for use in the flow."""
        return self.model_dump(mode='json')


# Default configuration instance
default_config = FlowConfig()


def load_config_from_file(file_path: str) -> FlowConfig:
    """Load configuration from a JSON or YAML file.
    
    Args:
        file_path: Path to the configuration file
        
    Returns:
        FlowConfig: Loaded configuration
    """
    import json
    import os
    from pathlib import Path
    
    if not os.path.exists(file_path):
        print(f"Warning: Configuration file {file_path} not found. Using default configuration.")
        return default_config
    
    file_extension = Path(file_path).suffix.lower()
    
    try:
        if file_extension == '.json':
            with open(file_path, 'r') as f:
                config_data = json.load(f)
            return FlowConfig(**config_data)
        elif file_extension in ['.yaml', '.yml']:
            import yaml
            with open(file_path, 'r') as f:
                config_data = yaml.safe_load(f)
            return FlowConfig(**config_data)
        else:
            print(f"Warning: Unsupported file extension {file_extension}. Using default configuration.")
            return default_config
    except Exception as e:
        print(f"Error loading configuration from {file_path}: {e}")
        print("Using default configuration.")
        return default_config


def get_config(config_file: Optional[str] = None) -> Dict[str, Any]:
    """Get the configuration as a dictionary.
    
    Args:
        config_file: Optional path to a configuration file
        
    Returns:
        Dict[str, Any]: Configuration dictionary for use in the flow
    """
    if config_file:
        config = load_config_from_file(config_file)
    else:
        config = default_config
    
    return config.to_dict()
