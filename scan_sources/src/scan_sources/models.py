# models.py
from pydantic import BaseModel, Field, HttpUrl, create_model
from typing import List, Optional, Dict, Union, Type, Any
from enum import Enum
from datetime import datetime

# Research Plan for market forces
class Market_Force(BaseModel):
    market_force_id: int
    market_force_short_description: str
    market_force_long_description: str
    research_objectives: List[str]
    content_examples: List[str]
    minimum_sources: List[str]
    source_priority: List[str]
    quality_criteria: List[str]
    integration_approach: List[str]

class Market_Force_Plan(BaseModel):
    market_forces: List[Market_Force]
