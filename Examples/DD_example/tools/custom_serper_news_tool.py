from crewai.tools import BaseTool
import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()

class CustomSerperNewsTool(BaseTool):
    name: str = "News Search Tool"
    description: str = "a Tool that can be used to search the internet for news."

    def _run(self, query: str) -> str:
        """
        Search the internet for news.
        """

        url = "https://google.serper.dev/news"

        payload = json.dumps({
            "q": query,
            # "gl": "",         
            "num": 20,
            "autocorrect": False,
            # "tbs": "qdr:y"
        })

        headers = {
            'X-API-KEY': os.getenv('SERPER_API_KEY'),
            'Content-Type': 'application/json'
        }

        response = requests.request("POST", url, headers=headers, data=payload)

        # Parse the JSON response
        response_data = response.json()

        # Extract only the 'news' property
        news_data = response_data.get('news', [])

        # Convert the news data back to a JSON string
        return json.dumps(news_data, indent=2)