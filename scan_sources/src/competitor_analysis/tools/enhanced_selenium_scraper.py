import re
import time
import random
from typing import Any, Optional, Type
from urllib.parse import urlparse

from crewai.tools import BaseTool
from pydantic import BaseModel, Field, validator


class FixedSeleniumScrapingToolSchema(BaseModel):
    """Input for SeleniumScrapingTool."""


class SeleniumScrapingToolSchema(FixedSeleniumScrapingToolSchema):
    """Input for SeleniumScrapingTool."""

    website_url: str = Field(
        ...,
        description="Mandatory website url to read the file. Must start with http:// or https://",
    )
    css_element: str = Field(
        ...,
        description="Mandatory css reference for element to scrape from the website",
    )

    @validator("website_url")
    def validate_website_url(cls, v):
        if not v:
            raise ValueError("Website URL cannot be empty")

        if len(v) > 2048:  # Common maximum URL length
            raise ValueError("URL is too long (max 2048 characters)")

        if not re.match(r"^https?://", v):
            raise ValueError("URL must start with http:// or https://")

        try:
            result = urlparse(v)
            if not all([result.scheme, result.netloc]):
                raise ValueError("Invalid URL format")
        except Exception as e:
            raise ValueError(f"Invalid URL: {str(e)}")

        if re.search(r"\s", v):
            raise ValueError("URL cannot contain whitespace")

        return v


class EnhancedSeleniumScrapingTool(BaseTool):
    name: str = "Read a website content"
    description: str = "A tool that can be used to read a website content with enhanced anti-detection capabilities."
    args_schema: Type[BaseModel] = SeleniumScrapingToolSchema
    website_url: Optional[str] = None
    driver: Optional[Any] = None
    cookie: Optional[dict] = None
    wait_time: Optional[int] = 3
    css_element: Optional[str] = None
    return_html: Optional[bool] = False
    _options: Optional[dict] = None
    _by: Optional[Any] = None
    max_retries: int = 3

    def __init__(
        self,
        website_url: Optional[str] = None,
        cookie: Optional[dict] = None,
        css_element: Optional[str] = None,
        site_specific_handling: Optional[dict] = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            from selenium.common.exceptions import TimeoutException
        except ImportError:
            import click

            if click.confirm(
                "You are missing the 'selenium' and 'webdriver-manager' packages. Would you like to install it?"
            ):
                import subprocess

                subprocess.run(
                    ["uv", "pip", "install", "selenium", "webdriver-manager"],
                    check=True,
                )
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options
                from selenium.webdriver.common.by import By
                from selenium.webdriver.support.ui import WebDriverWait
                from selenium.webdriver.support import expected_conditions as EC
                from selenium.common.exceptions import TimeoutException
            else:
                raise ImportError(
                    "`selenium` and `webdriver-manager` package not found, please run `uv add selenium webdriver-manager`"
                )
        
        self.webdriver = webdriver
        self._options = Options()
        self._by = By
        self._WebDriverWait = WebDriverWait
        self._EC = EC
        self._TimeoutException = TimeoutException
        self.site_specific_handling = site_specific_handling or {}
        
        if cookie is not None:
            self.cookie = cookie

        if css_element is not None:
            self.css_element = css_element

        if website_url is not None:
            self.website_url = website_url
            self.description = (
                f"A tool that can be used to read {website_url}'s content."
            )
            self.args_schema = FixedSeleniumScrapingToolSchema

        self._generate_description()

    def _run(
        self,
        **kwargs: Any,
    ) -> Any:
        website_url = kwargs.get("website_url", self.website_url)
        css_element = kwargs.get("css_element", self.css_element)
        return_html = kwargs.get("return_html", self.return_html)
        
        # Try multiple times with different strategies
        for attempt in range(self.max_retries):
            try:
                driver = self._create_driver(website_url, self.cookie, self.wait_time)
                content = self._get_content(driver, css_element, return_html)
                driver.quit()
                return "\n".join(content)
            except Exception as e:
                if attempt < self.max_retries - 1:
                    # Wait with exponential backoff
                    wait_time = (2 ** attempt) + random.uniform(1, 3)
                    time.sleep(wait_time)
                    continue
                else:
                    raise Exception(f"Failed after {self.max_retries} attempts. Last error: {str(e)}")

    def _get_content(self, driver, css_element, return_html):
        content = []
        
        # Wait for page to fully load
        try:
            self._WebDriverWait(driver, 10).until(
                self._EC.presence_of_element_located((self._by.TAG_NAME, "body"))
            )
        except self._TimeoutException:
            pass

        if self._is_css_element_empty(css_element):
            content.append(self._get_body_content(driver, return_html))
        else:
            content.extend(self._get_elements_content(driver, css_element, return_html))

        return content

    def _is_css_element_empty(self, css_element):
        return css_element is None or css_element.strip() == ""

    def _get_body_content(self, driver, return_html):
        # Wait for specific McKinsey content to load
        try:
            self._WebDriverWait(driver, 10).until(
                self._EC.presence_of_element_located((self._by.CLASS_NAME, "mck-hero"))
            )
        except self._TimeoutException:
            pass

        body_element = driver.find_element(self._by.TAG_NAME, "body")

        return (
            body_element.get_attribute("outerHTML")
            if return_html
            else body_element.text
        )

    def _get_elements_content(self, driver, css_element, return_html):
        elements_content = []
        
        # Wait for the specific elements to be present
        try:
            self._WebDriverWait(driver, 10).until(
                self._EC.presence_of_element_located((self._by.CSS_SELECTOR, css_element))
            )
        except self._TimeoutException:
            pass

        for element in driver.find_elements(self._by.CSS_SELECTOR, css_element):
            elements_content.append(
                element.get_attribute("outerHTML") if return_html else element.text
            )

        return elements_content

    def _create_driver(self, url, cookie, wait_time):
        if not url:
            raise ValueError("URL cannot be empty")

        # Validate URL format
        if not re.match(r"^https?://", url):
            raise ValueError("URL must start with http:// or https://")

        options = self._options
        
        # Enhanced anti-detection measures
        options.add_argument("--headless")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Realistic browser settings
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        
        # Realistic headers
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
        }
        options.add_experimental_option("prefs", prefs)
        
        # Create driver with enhanced options
        driver = self.webdriver.Chrome(options=options)
        
        # Remove webdriver flag
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Set realistic user agent
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
        
        # Add random delay
        delay = random.uniform(2, 5)
        time.sleep(delay)
        
        # Handle site-specific requirements
        for domain, homepage in self.site_specific_handling.items():
            if domain in url:
                driver.get(homepage)
                time.sleep(random.uniform(2, 4))
                break
        
        # Now visit the target URL
        driver.get(url)
        
        # Enhanced wait with random component
        base_wait = wait_time + random.uniform(1, 3)
        time.sleep(base_wait)
        
        if cookie:
            driver.add_cookie(cookie)
            time.sleep(wait_time)
            driver.get(url)
            time.sleep(wait_time)
            
        # Scroll down a bit to simulate human behaviour
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight/4);")
        time.sleep(random.uniform(1, 2))
        driver.execute_script("window.scrollTo(0, 0);")
        
        return driver

    def close(self):
        if self.driver:
            self.driver.quit()


# Additional utility for testing directly
def test_mckinsey_scraper():
    """Test function to validate the enhanced scraper"""
    from crewai import Agent, Task, Crew
    
    # Create test scraper
    scraper = EnhancedSeleniumScrapingTool()
    
    # Create a simple agent for testing
    test_agent = Agent(
        role='Web Content Analyst',
        goal='Extract content from McKinsey websites',
        backstory='You are a research assistant specializing in extracting market insights.',
        tools=[scraper]
    )
    
    # Create test task
    test_task = Task(
        description="""
        Extract the main content from this McKinsey article:
        https://www.mckinsey.com/industries/financial-services/our-insights/whats-next-for-global-banking
        
        Focus on the key insights and recommendations.
        """,
        agent=test_agent,
        expected_output='A summary of the key insights and recommendations from the article.'
    )
    
    # Run the test
    crew = Crew(
        agents=[test_agent],
        tasks=[test_task],
        verbose=True
    )
    
    try:
        result = crew.kickoff()
        print("Success! Content extracted:")
        print(result)
    except Exception as e:
        print(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_mckinsey_scraper()