from crewai.tools import BaseTool # Use BaseTool for more control if needed, but @tool is usually fine
from crewai.tools import tool
from exa_py import Exa
import os
import logging

exa_api_key = os.getenv("EXA_API_KEY") # Ensure this is accessible

@tool("Exa Crawl URL Tool")
def Exa_crawl_scrape_tool(url: str) -> str:
    """
    Scrape and crawl a specific site to retrieve content
    Uses the Exa API to crawl a specific URL and retrieve its full text content.

    Input:
        url (str): The exact URL of the webpage to crawl.

    Output:
        str: The full text content of the crawled webpage. Returns an error message
             if the API key is missing, the URL is invalid, or the crawl fails.
             Returns 'No content found.' if the crawl succeeds but extracts no text.
    """
    if not exa_api_key:
        logging.error("EXA_API_KEY environment variable not set for crawl tool.")
        return "Error: Exa API key is not configured."

    # Basic URL validation (optional but recommended)
    if not url.startswith(('http://', 'https://')):
        logging.warning(f"Invalid URL format provided for crawl: {url}")
        return f"Error: Invalid URL format. Please provide a full URL starting with http:// or https://."

    try:
        exa = Exa(exa_api_key)
        logging.info(f"Performing Exa crawl for URL: {url}")

        # Use the 'crawl' method
        # Adjust parameters as needed (e.g., text=True is default, content_format)
        response = exa.crawl(
            url=url,
            # text=True, # Usually default, explicitly state if needed
            # You might explore other parameters like 'content_format' if required
        )

        # Check if content was actually retrieved
        # The exact attribute might vary, check exa-py documentation/response object
        # Assuming response directly gives the text or has a .text attribute
        content = response.text if hasattr(response, 'text') else str(response) # Adapt based on actual response object

        if not content or content.strip() == "":
             logging.info(f"Exa crawl for {url} returned no content.")
             return f"No content found at URL: {url}"

        logging.info(f"Exa crawl successful for URL: {url}. Content length: {len(content)}")
        # Consider truncating very long content if necessary for agent processing
        # max_len = 10000
        # if len(content) > max_len:
        #     content = content[:max_len] + "\n... [Content Truncated]"
        return content

    except APIError as e: # Replace with actual Exa APIError if it exists
         logging.error(f"Exa API Error during crawl of {url}: {e}")
         return f"Error: Exa API request failed for crawling {url}: {e}"
    except Exception as e:
        logging.error(f"An unexpected error occurred during Exa crawl of {url}: {e}", exc_info=True)
        return f"Error: An unexpected error occurred while crawling {url}: {e}"

# --- How to use them together in CrewAI ---

# from crewai import Agent, Task, Crew
# from your_module import search_and_get_contents_tool, crawl_url_tool

# # Ensure EXA_API_KEY is set

# researcher = Agent(
#     role='Web Researcher',
#     goal='Find relevant articles and extract their full content using Exa tools',
#     backstory='Expert at finding information online using semantic search and then extracting full text from specific URLs.',
#     tools=[search_and_get_contents_tool, crawl_url_tool], # Give the agent BOTH tools
#     verbose=True,
#     allow_delegation=False # Usually False for research agents
# )

# research_task = Task(
#     description='Find the top 2 most recent articles about advancements in battery technology. Then, retrieve the full text content of the most promising article.',
#     expected_output='The full text content of the single most relevant recent article about battery technology advancements found via Exa.',
#     agent=researcher
# )

# crew = Crew(
#     agents=[researcher],
#     tasks=[research_task],
#     verbose=2
# )

# result = crew.kickoff()
# print(result)