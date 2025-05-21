import os
import json
from typing import Type, Dict, Any
import requests

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, PrivateAttr
from tavily import TavilyClient


class TavilySearchToolInput(BaseModel):
    query: str = Field(..., description="The query to search the web for.")
    max_results: int = Field(10, description="The maximum number of results to return.")


class TavilySearchTool(BaseTool):
    name: str = "Tavily Search Tool"
    description: str = "Search the web using Tavily"
    args_schema: Type[BaseModel] = TavilySearchToolInput

    _tavily_client: TavilyClient = PrivateAttr(default=None)
    _use_fallback: bool = PrivateAttr(default=False)
    _api_key: str = PrivateAttr(default="")

    def __init__(self):
        super().__init__()
        # Get API key with various fallbacks
        self._api_key = os.getenv("TAVILY_API_KEY", "").strip()
        
        # Try to create client only if we have a key
        if self._api_key:
            try:
                self._tavily_client = TavilyClient(api_key=self._api_key)
                # You could test the client here, but we'll do it on first request
            except Exception as e:
                print(f"Warning: Could not initialize Tavily client: {str(e)}")
                self._use_fallback = True
        else:
            print("Warning: TAVILY_API_KEY environment variable is not set. Will use fallback methods.")
            self._use_fallback = True

    def _fallback_search(self, query: str) -> str:
        """
        Fallback method when Tavily search is unavailable
        """
        # Include API key error details
        if not self._api_key:
            key_status = "No API key found in environment variables."
        else:
            key_status = f"API key found (starts with: {self._api_key[:4]}...), but was rejected by Tavily."
        
        return (f"⚠️ Tavily Search Error: {key_status}\n\n"
                f"I couldn't search for '{query}' using Tavily. To fix this issue:\n\n"
                "1. Check your Tavily API key is correct and active\n"
                "2. Make sure the TAVILY_API_KEY environment variable is properly set\n"
                "3. Verify your Tavily account has sufficient credits\n\n"
                "In the meantime, I'll continue with the available information and use alternative search methods if needed.")

    def _run(self, query: str, max_results: int) -> str:
        """
        Execute a search using the Tavily API with better error handling
        """
        # If we already know we need to use the fallback, do it right away
        if self._use_fallback:
            return self._fallback_search(query)
            
        try:
            # Set search parameters
            search_params = {
                "query": query,
                "max_results": max_results,
                "search_depth": "advanced",  # Use advanced for more comprehensive results
                "include_answer": True,
                "include_images": False,
                "include_raw_content": False
            }
            
            # Execute the search
            search_result = self._tavily_client.search(**search_params)
            
            # Format results for better readability
            if isinstance(search_result, dict):
                # Extract the most useful information
                answer = search_result.get("answer", "")
                results = search_result.get("results", [])
                
                formatted_results = []
                for i, result in enumerate(results, 1):
                    formatted_result = f"[{i}] {result.get('title', 'No Title')}\n"
                    formatted_result += f"URL: {result.get('url', 'No URL')}\n"
                    formatted_result += f"Content: {result.get('content', 'No content available')}\n"
                    formatted_results.append(formatted_result)
                
                response = f"Answer Summary: {answer}\n\n"
                response += "Detailed Results:\n\n"
                response += "\n\n".join(formatted_results)
                
                return response
            else:
                # If the response isn't a dict, try to format it as a string
                return f"Search Results for '{query}':\n\n{search_result}"
                
        except Exception as e:
            # Set the fallback flag so we don't keep trying
            self._use_fallback = True
            
            # Detailed error handling
            error_type = type(e).__name__
            error_msg = str(e)
            
            # Specific handling for known error types
            if "invalid" in error_msg.lower() and "api key" in error_msg.lower():
                return (f"⚠️ Tavily API Key Error: {error_msg}\n\n"
                        f"Your API key (starting with {self._api_key[:4]}...) was rejected by Tavily.\n"
                        "Please check that your key is valid and properly set in the environment variables.\n\n"
                        "In the meantime, I'll continue with available information and use alternative search methods.")
            else:
                # Generic error handling
                return (f"⚠️ Tavily Search Error ({error_type}): {error_msg}\n\n"
                        f"I couldn't search for '{query}' using Tavily. I'll continue with "
                        "available information and use alternative search methods if needed.")