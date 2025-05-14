# --- START OF FILE custom_web_scrape_market_forces.py ---

import os
import re
import traceback # Added for error logging
from typing import Any, Optional, Type

import requests
import litellm # Added for internal LLM call
from bs4 import BeautifulSoup
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


# --- Schema definitions remain the same ---
class MarketForcesScrapeWebsiteToolSchema(BaseModel):
    """Input for MarketForcesScrapeWebsiteTool."""

class MarketForcesScrapeWebsiteToolSchema(MarketForcesScrapeWebsiteToolSchema):
    """Input for MarketForcesScrapeWebsiteTool."""
    website_url: str = Field(..., description="Mandatory website url to read the file")

# --- Modified ScrapeWebsiteTool ---
class MarketForcesScrapeWebsiteTool(BaseTool):
    # Updated Name and Description
    name: str = "Scrape and Analyze Website Content"
    description: str = "Scrapes a website's content and analyzes it to extract key information relevant to a specific topic."
    args_schema: Type[BaseModel] = MarketForcesScrapeWebsiteToolSchema # _run still only needs URL

    # --- NEW: Internal state for LLM and topic ---
    llm: Any = None # Will hold the LLM configuration object
    topic: str = "" # Will hold the research topic
    analysis_model: str = "gemini/gemini-2.5-flash-preview-04-17" # Model for internal analysis (configurable)
    # ---

    website_url: Optional[str] = None # Kept for potential fixed URL usage
    cookies: Optional[dict] = None
    headers: Optional[dict] = { # Kept existing headers
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "Accept-Language": "en-US,en;q=0.9",
        "Referer": "https://www.google.com/",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
    }

    # --- MODIFIED: __init__ to accept LLM and topic ---
    def __init__(
        self,
        llm: Any, # Require an LLM configuration object
        topic: str, # Require the research topic
        analysis_model: Optional[str] = None, # Allow overriding internal model
        website_url: Optional[str] = None,
        cookies: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)

        # --- Store LLM and topic ---
        if llm is None:
            raise ValueError("An LLM configuration object must be provided to ScrapeWebsiteTool.")
        if not topic:
            raise ValueError("A research topic must be provided to ScrapeWebsiteTool.")

        self.llm = llm # Store the passed LLM config (though we primarily use its settings)
        self.topic = topic
        if analysis_model:
            self.analysis_model = analysis_model
        # Extract model name from llm object if possible, otherwise use default
        # This part depends heavily on how your llm objects (llm_gpt4o etc.) are structured
        # For simplicity, we'll use the configured self.analysis_model directly with litellm
        # If your llm object has a clear attribute like llm.model_name, you could use that:
        # self.analysis_model = getattr(llm, 'model_name', self.analysis_model)


        # --- Handle fixed URL case (optional) ---
        if website_url is not None:
            self.website_url = website_url
            self.description = f"Scrapes and analyzes {website_url}'s content for information relevant to {self.topic}."
            self.args_schema = MarketForcesScrapeWebsiteToolSchema
            self._generate_description() # Regenerate description if fixed URL
            if cookies is not None:
                # Assuming cookies format { "name": "COOKIE_NAME", "value": "ENV_VAR_NAME" }
                cookie_name = cookies.get("name")
                env_var = cookies.get("value")
                if cookie_name and env_var:
                    cookie_value = os.getenv(env_var)
                    if cookie_value:
                        self.cookies = {cookie_name: cookie_value}
                    else:
                        print(f"Warning: Environment variable {env_var} for cookie {cookie_name} not found.")
                else:
                     print(f"Warning: Invalid cookie configuration provided: {cookies}")

    # --- MODIFIED: _run to include LLM analysis ---
    def _run(
        self,
        **kwargs: Any,
    ) -> str: # Return type is now always string (analysis or error)
        website_url = kwargs.get("website_url", self.website_url)
        if not website_url:
            return "Error: Website URL must be provided either during initialization or execution."

        # 1. Scrape Website
        try:
            page = requests.get(
                website_url,
                timeout=20, # Increased timeout slightly
                headers=self.headers,
                cookies=self.cookies if self.cookies else {},
            )
            page.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        except requests.exceptions.RequestException as e:
            return f"Error scraping website {website_url}: {e}"

        # 2. Parse Content
        try:
            page.encoding = page.apparent_encoding # Guess encoding
            parsed = BeautifulSoup(page.content, "html.parser", from_encoding=page.encoding)

            # Basic text extraction and cleaning (consider more advanced cleaning if needed)
            text = parsed.get_text(" ", strip=True) # strip=True removes extra whitespace
            text = re.sub(r'\s{2,}', ' ', text) # Replace multiple spaces/newlines with single space
            text = text.strip()

            if not text:
                return f"No text content found on {website_url} after parsing."

        except Exception as e:
            return f"Error parsing website content from {website_url}: {e}"

        # 3. Analyze Content with Internal LLM
        # Prepare the prompt for the internal analysis LLM
        analysis_prompt = f"""Analyze the following text scraped from {website_url}.
        Your goal is to extract key information relevant ONLY to the topic: "{self.topic}".

        Focus on identifying:
        - Market forces, trends, drivers, or shifts related to the topic.
        - Key statistics, facts, or figures relevant to the topic.
        - Specific examples or case studies mentioned related to the topic.
        - Relevant quotes from individuals or organizations about the topic.
        - Any direct insights or predictions about the future of "{self.topic}".ß

        Keep the output concise and focused ONLY on information directly pertaining to "{self.topic}". Ignore irrelevant sections, boilerplate text, ads, navigation elements, etc. If no relevant information is found, state that explicitly.

        Scraped Text:
        ---
        {text[:10000]}
        ---
        """ # Limit text size to avoid exceeding context window easily

        try:
            # Use litellm for the internal call
            response = litellm.completion(
                model=self.analysis_model,
                messages=[{"role": "user", "content": analysis_prompt}],
                max_tokens=8000,
                temperature=0.1,
                # Consider adding retry logic here if needed for APIConnectionErrors
                max_retries=3,
            )

            # --- IMPROVED ERROR HANDLING FOR LLM RESPONSE ---
            if not response or not response.choices or not response.choices[0].message or not response.choices[0].message.content:
                 # Log details before returning error string
                 print(f"Internal LLM analysis returned no content for {website_url}. Response: {response}")
                 return f"TOOL_ANALYSIS_ERROR: Internal LLM analysis returned no content for {website_url}."

            analysis_result = response.choices[0].message.content.strip()

            if not analysis_result:
                 print(f"Internal LLM analysis returned empty string for {website_url}. Response: {response}")
                 return f"TOOL_ANALYSIS_ERROR: Internal LLM analysis returned empty content for {website_url}."
            # --- END IMPROVED HANDLING ---

            # Prepend the source URL to the analysis for clarity
            return f"Analysis results for {website_url}:\n\n{analysis_result}"

        except litellm.exceptions.APIConnectionError as e:
             print(f"Internal LLM API connection error for {website_url}: {e}")
             print(traceback.format_exc())
             return f"TOOL_ANALYSIS_ERROR: Internal LLM API connection error for {website_url}: {e}"
        except litellm.exceptions.BadRequestError as e:
             print(f"Internal LLM BadRequest error for {website_url}: {e}")
             print(traceback.format_exc())
             # This might happen if the analysis prompt + text is too large for the analysis model
             return f"TOOL_ANALYSIS_ERROR: Internal LLM BadRequest for {website_url}: {e}"
        except Exception as e:
            # Catch any other unexpected errors during the LLM call
            print(f"An unexpected error occurred during internal LLM analysis for {website_url}: {e}")
            print(traceback.format_exc())
            return f"TOOL_ANALYSIS_ERROR: Unexpected error during internal LLM analysis for {website_url}: {e}"

# Example of how you might instantiate this tool later in your crew setup:
# from .llm_config import llm_gpt4o_mini # Assuming your llm configs are here
# from .config import USER_INPUT_VARIABLES
#
# topic = USER_INPUT_VARIABLES.get("topic", "Default Topic")
# llm_for_analysis = llm_gpt4o_mini # Or choose another suitable LLM
#
# analysis_scraper_tool = ScrapeWebsiteTool(llm=llm_for_analysis, topic=topic)
#
# # Then pass this tool to the agent:
# # agent = Agent(
# #     # ... other agent config ...
# #     tools=[analysis_scraper_tool, other_tool1, ...],
# #     llm=llm_main_agent_llm # The agent's primary LLM
# # )

# --- END OF FILE scrape_website_tool.py ---