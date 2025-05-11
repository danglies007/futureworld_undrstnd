# url_counter_tool.py
from typing import Type, Dict, Set, List, Optional
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

class URLCounterState:
    """Singleton class to maintain state of processed URLs across tool calls."""
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(URLCounterState, cls).__new__(cls)
            cls._instance.processed_urls = set()
        return cls._instance

# Create a singleton instance
url_state = URLCounterState()

class URLCounterInput(BaseModel):
    """Input schema for URLCounterTool."""
    action: str = Field(..., description="Action to perform: 'add', 'count', 'list', or 'reset'")
    url: Optional[str] = Field(None, description="URL to add (only needed for 'add' action)")

class URLCounterTool(BaseTool):
    name: str = "url_counter"
    description: str = """
    Track and manage processed URLs. This tool can:
    - Add a URL to the processed list
    - Count how many URLs have been processed
    - List all processed URLs
    - Reset the URL counter
    
    Use this to keep track of how many sources have been evaluated.
    """
    args_schema: Type[BaseModel] = URLCounterInput
    
    def _run(self, action: str, url: Optional[str] = None) -> str:
        """Run the URL counter tool with the specified action."""
        global url_state
        
        if action == "add":
            if not url:
                return "Error: URL is required for 'add' action"
            url_state.processed_urls.add(url.strip())
            return f"Added URL: {url}. Total processed: {len(url_state.processed_urls)}"
            
        elif action == "count":
            return f"Total URLs processed: {len(url_state.processed_urls)}"
            
        elif action == "list":
            urls = list(url_state.processed_urls)
            return f"Processed URLs ({len(urls)}): {urls}"
            
        elif action == "reset":
            url_state.processed_urls.clear()
            return "URL counter reset."
            
        else:
            return f"Error: Unknown action '{action}'. Use 'add', 'count', 'list', or 'reset'."