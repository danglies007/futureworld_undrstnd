from crewai.tools import BaseTool # Use BaseTool for more control if needed, but @tool is usually fine
from crewai.tools import tool
from exa_py import Exa
import os
import logging

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

exa_api_key = os.getenv("EXA_API_KEY")

@tool("Exa Search and Get Contents Tool")
def Exa_search_tool(question: str) -> str:
    """
    Search and retrieve content using Exa API.
    
    Performs a semantic search using the Exa API based on the input question,
    retrieves the contents of the top results, and returns them in a structured format.

    Input:
        question (str): The search query or question.

    Output:
        str: A formatted string containing the search results (Title, URL, Highlights),
             separated by '---'. Returns an error message if the API key is missing
             or if the search fails. Returns 'No results found.' if the search yields no results.
    """
    if not exa_api_key:
        logging.error("EXA_API_KEY environment variable not set.")
        return "Error: Exa API key is not configured."

    try:
        exa = Exa(exa_api_key)
        logging.info(f"Performing Exa search for: {question}")

        response = exa.search_and_contents(
            question,
            type="neural",
            use_autoprompt=True,
            num_results=3,
            highlights={"num_sentences": 3, "highlights_per_url": 1} # More specific highlight options if needed
            # text=True, # Consider adding text=True if you want full content snippets too
        )

        if not response.results:
            logging.info("Exa search returned no results.")
            return "No results found."

        # Alternative Formatting (Markdown-like):
        result_strings = []
        for idx, result in enumerate(response.results):
            # Join highlights with newlines for better readability
            highlight_text = "\n".join(f"- {h}" for h in result.highlights) if result.highlights else "No highlights available."

            result_strings.append(
                f"Result {idx + 1}:\n"
                f"Title: {result.title}\n"
                f"URL: {result.url}\n"
                f"Highlights:\n{highlight_text}\n"
                # f"Content Snippet: {result.text}\n" # Add this if you fetch text content
            )

        parsed_result = "---\n".join(result_strings) # Use --- as a separator
        logging.info(f"Exa search successful. Returning {len(response.results)} results.")
        return parsed_result

    # Catch specific Exa errors if available, otherwise general Exception
    except APIError as e: # Replace with actual Exa APIError if it exists
         logging.error(f"Exa API Error during search: {e}")
         return f"Error: Exa API request failed: {e}"
    except Exception as e:
        logging.error(f"An unexpected error occurred during Exa search: {e}", exc_info=True)
        return f"Error: An unexpected error occurred while searching: {e}"

# --- How to use it in CrewAI ---

# from crewai import Agent, Task, Crew
# from your_module import search_and_get_contents_tool # Assuming you save the tool in 'your_module.py'

# # Ensure EXA_API_KEY is set in your environment before running

# research_agent = Agent(
#     role='Information Retriever',
#     goal='Find relevant information online using the Exa search tool',
#     backstory='An AI assistant specialized in using the Exa search engine to find and summarize web content.',
#     tools=[search_and_get_contents_tool],
#     verbose=True
# )

# research_task = Task(
#     description='What are the latest advancements in quantum computing?',
#     expected_output='A summary of the top 3 recent advancements found via Exa search, including titles, URLs, and key highlights.',
#     agent=research_agent
# )

# crew = Crew(
#     agents=[research_agent],
#     tasks=[research_task],
#     verbose=2
# )

# result = crew.kickoff()
# print("\n\n########################")
# print("## CrewAI Task Result:")
# print("########################\n")
# print(result)