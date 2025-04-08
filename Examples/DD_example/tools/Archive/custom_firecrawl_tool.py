import os
from typing import TYPE_CHECKING, Any, Dict, Optional, Type
from pydantic import BaseModel, Field
# from crewai_tools.tools.base_tool import BaseTool
from crewai.tools import BaseTool


if TYPE_CHECKING:
    from firecrawl import FirecrawlApp

class CustomFirecrawlScrapeWebsiteToolSchema(BaseModel):
    url: str = Field(description="Website URL")
    page_options: Optional[Dict[str, Any]] = Field(default=None, description="Options for page scraping")
    extractor_options: Optional[Dict[str, Any]] = Field(default=None, description="Options for data extraction")
    timeout: Optional[int] = Field(default=30000, description="Timeout in milliseconds for the scraping operation.")

class CustomFirecrawlScrapeWebsiteTool(BaseTool):
    name: str = "Firecrawl web scrape tool"
    description: str = "Scrape webpages using Firecrawl and return the contents"
    args_schema: Type[BaseModel] = CustomFirecrawlScrapeWebsiteToolSchema
    api_key: Optional[str] = os.getenv("FIRECRAWL_API_KEY")
    firecrawl: Optional["FirecrawlApp"] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        try:
            from firecrawl import FirecrawlApp  # type: ignore
            self.firecrawl = FirecrawlApp(api_key=self.api_key)
        except ImportError:
            raise ImportError("`firecrawl` package not found, please install it using `pip install firecrawl-py`")
        except Exception as e:
            raise Exception(f"Error initializing Firecrawl: {e}")

    def _run(self, url: str, page_options: Optional[Dict[str, Any]] = None, extractor_options: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None) -> str:
        """
        Scrape the given website URL using Firecrawl.

        Args:
            url (str): The website URL to scrape.
            page_options (Optional[Dict[str, Any]]): Options for page scraping.
            extractor_options (Optional[Dict[str, Any]]): Options for data extraction.
            timeout (Optional[int]): Timeout in milliseconds for the scraping operation.

        Returns:
            str: The scraped website content.
        """
        if self.firecrawl is None:
            raise Exception("Firecrawl app is not initialized. Please provide a valid API key.")

        if page_options is None:
            page_options = {}
        if extractor_options is None:
            extractor_options = {}
        if timeout is None:
            timeout = 30000

        options = {
            "pageOptions": page_options,
            "extractorOptions": extractor_options,
            "timeout": timeout,
        }

        try:
            return self.firecrawl.scrape_url(url, options)
        except Exception as e:
            raise Exception(f"Error scraping website: {e}")

    async def _arun(self, url: str, page_options: Optional[Dict[str, Any]] = None, extractor_options: Optional[Dict[str, Any]] = None, timeout: Optional[int] = None) -> str:
        """
        Asynchronous version of the _run method.
        """
        return await self.loop.run_in_executor(None, self._run, url, page_options, extractor_options, timeout)