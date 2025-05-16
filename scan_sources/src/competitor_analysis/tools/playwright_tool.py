import asyncio
import json
import logging
import os
from typing import Any, Dict, List, Optional, Type, Union
import nest_asyncio

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from playwright.async_api import async_playwright

# Apply nest_asyncio to allow running asyncio within an existing event loop
nest_asyncio.apply()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PlaywrightToolSchema(BaseModel):
    """Input schema for PlaywrightTool."""
    
    action: str = Field(
        ..., 
        description="The action to perform (goto, screenshot, click, type, extract_text, extract_html, evaluate)"
    )
    url: Optional[str] = Field(
        None, 
        description="URL to navigate to when using 'goto' action"
    )
    selector: Optional[str] = Field(
        None, 
        description="CSS selector for elements when using 'click', 'type', or 'extract' actions"
    )
    text: Optional[str] = Field(
        None, 
        description="Text to type when using 'type' action"
    )
    xpath: Optional[str] = Field(
        None, 
        description="XPath selector as an alternative to CSS selector"
    )
    wait_for: Optional[str] = Field(
        None, 
        description="Selector to wait for before proceeding with the action"
    )
    timeout: Optional[int] = Field(
        30000, 
        description="Timeout in milliseconds for operations"
    )
    javascript: Optional[str] = Field(
        None, 
        description="JavaScript to evaluate in the browser context when using 'evaluate' action"
    )
    path: Optional[str] = Field(
        None, 
        description="File path to save screenshot when using 'screenshot' action"
    )
    browser_type: Optional[str] = Field(
        "chromium", 
        description="Browser type to use: 'chromium', 'firefox', or 'webkit'"
    )
    headless: Optional[bool] = Field(
        True, 
        description="Whether to run browser in headless mode"
    )


class PlaywrightTool(BaseTool):
    """A tool that enables browser automation using Playwright."""
    
    name: str = "Playwright Browser Automation"
    description: str = (
        "A tool for web browser automation that can navigate to URLs, "
        "take screenshots, click elements, type text, extract content, "
        "and evaluate JavaScript in a browser context."
    )
    args_schema: Type[BaseModel] = PlaywrightToolSchema

    async def _goto(self, page, url: str, wait_for: Optional[str] = None, timeout: int = 30000) -> Dict[str, Any]:
        """Navigate to a URL."""
        try:
            await page.goto(url, wait_until="networkidle", timeout=timeout)
            if wait_for:
                await page.wait_for_selector(wait_for, timeout=timeout)
            return {"status": "success", "url": url, "title": await page.title()}
        except Exception as e:
            logger.error(f"Error navigating to URL {url}: {e}")
            return {"status": "error", "message": str(e)}

    async def _screenshot(self, page, path: str = None) -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        try:
            if not path:
                # Generate a default filename if none provided
                import datetime
                path = f"screenshot_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
            
            await page.screenshot(path=path, full_page=True)
            return {"status": "success", "path": path}
        except Exception as e:
            logger.error(f"Error taking screenshot: {e}")
            return {"status": "error", "message": str(e)}

    async def _click(self, page, selector: str = None, xpath: str = None, timeout: int = 30000) -> Dict[str, Any]:
        """Click on an element identified by CSS selector or XPath."""
        try:
            if selector:
                await page.wait_for_selector(selector, timeout=timeout)
                await page.click(selector)
                return {"status": "success", "clicked": selector}
            elif xpath:
                await page.wait_for_selector(f"xpath={xpath}", timeout=timeout)
                await page.click(f"xpath={xpath}")
                return {"status": "success", "clicked": xpath}
            else:
                return {"status": "error", "message": "Either selector or xpath must be provided"}
        except Exception as e:
            logger.error(f"Error clicking element: {e}")
            return {"status": "error", "message": str(e)}

    async def _type(self, page, selector: str, text: str, timeout: int = 30000) -> Dict[str, Any]:
        """Type text into an input field."""
        try:
            await page.wait_for_selector(selector, timeout=timeout)
            await page.fill(selector, text)
            return {"status": "success", "selector": selector, "text": text}
        except Exception as e:
            logger.error(f"Error typing text: {e}")
            return {"status": "error", "message": str(e)}

    async def _extract_text(self, page, selector: str = None, xpath: str = None) -> Dict[str, Any]:
        """Extract text content from elements matching a selector."""
        try:
            if selector:
                elements = await page.query_selector_all(selector)
            elif xpath:
                elements = await page.query_selector_all(f"xpath={xpath}")
            else:
                return {"status": "error", "message": "Either selector or xpath must be provided"}
            
            texts = []
            for element in elements:
                text = await element.text_content()
                if text and text.strip():
                    texts.append(text.strip())
            
            return {"status": "success", "count": len(texts), "texts": texts}
        except Exception as e:
            logger.error(f"Error extracting text: {e}")
            return {"status": "error", "message": str(e)}

    async def _extract_html(self, page, selector: str = None) -> Dict[str, Any]:
        """Extract HTML content from the page or a specific element."""
        try:
            if selector:
                element = await page.query_selector(selector)
                if not element:
                    return {"status": "error", "message": f"No element found with selector: {selector}"}
                html = await page.evaluate("(element) => element.outerHTML", element)
            else:
                html = await page.content()
            
            return {"status": "success", "html": html}
        except Exception as e:
            logger.error(f"Error extracting HTML: {e}")
            return {"status": "error", "message": str(e)}

    async def _evaluate(self, page, javascript: str) -> Dict[str, Any]:
        """Evaluate JavaScript in the browser context."""
        try:
            result = await page.evaluate(javascript)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"Error evaluating JavaScript: {e}")
            return {"status": "error", "message": str(e)}

    async def _async_run(self, **kwargs: Any) -> Any:
        """Execute browser automation asynchronously."""
        action = kwargs.get("action")
        url = kwargs.get("url")
        selector = kwargs.get("selector")
        xpath = kwargs.get("xpath")
        text = kwargs.get("text")
        wait_for = kwargs.get("wait_for")
        timeout = kwargs.get("timeout", 30000)
        javascript = kwargs.get("javascript")
        path = kwargs.get("path")
        browser_type = kwargs.get("browser_type", "chromium")
        headless = kwargs.get("headless", True)
        
        async with async_playwright() as p:
            # Select the browser type
            if browser_type == "chromium":
                browser_instance = p.chromium
            elif browser_type == "firefox":
                browser_instance = p.firefox
            elif browser_type == "webkit":
                browser_instance = p.webkit
            else:
                return {"status": "error", "message": f"Unsupported browser type: {browser_type}"}
            
            # Launch browser
            browser = await browser_instance.launch(headless=headless)
            page = await browser.new_page()
            
            result = {"status": "error", "message": "No action performed"}
            
            try:
                # Perform the requested action
                if action == "goto":
                    if not url:
                        result = {"status": "error", "message": "URL is required for 'goto' action"}
                    else:
                        result = await self._goto(page, url, wait_for, timeout)
                
                elif action == "screenshot":
                    result = await self._screenshot(page, path)
                
                elif action == "click":
                    result = await self._click(page, selector, xpath, timeout)
                
                elif action == "type":
                    if not selector or not text:
                        result = {"status": "error", "message": "Both selector and text are required for 'type' action"}
                    else:
                        result = await self._type(page, selector, text, timeout)
                
                elif action == "extract_text":
                    result = await self._extract_text(page, selector, xpath)
                
                elif action == "extract_html":
                    result = await self._extract_html(page, selector)
                
                elif action == "evaluate":
                    if not javascript:
                        result = {"status": "error", "message": "JavaScript is required for 'evaluate' action"}
                    else:
                        result = await self._evaluate(page, javascript)
                
                else:
                    result = {"status": "error", "message": f"Unsupported action: {action}"}
            
            except Exception as e:
                logger.error(f"Error performing action {action}: {e}")
                result = {"status": "error", "message": str(e)}
            
            finally:
                # Clean up
                await browser.close()
                return result

    def _run(self, **kwargs: Any) -> Any:
        """Execute the browser automation."""
        # With nest_asyncio applied, we can safely use asyncio.run()
        return asyncio.run(self._async_run(**kwargs))


# For convenience, define specialized tools that focus on specific actions

class NavigateTool(PlaywrightTool):
    """Tool to navigate to a URL."""
    
    name: str = "Navigate to URL"
    description: str = "Navigate to a specific URL in a browser."
    
    class Schema(BaseModel):
        """Input for NavigateTool."""
        url: str = Field(..., description="URL to navigate to")
        wait_for: Optional[str] = Field(None, description="Optional selector to wait for after navigation")
        browser_type: Optional[str] = Field("chromium", description="Browser type: 'chromium', 'firefox', or 'webkit'")
        headless: Optional[bool] = Field(True, description="Whether to run browser in headless mode")
    
    args_schema: Type[BaseModel] = Schema
    
    def _run(self, **kwargs: Any) -> Any:
        """Navigate to a URL."""
        kwargs["action"] = "goto"
        return asyncio.run(self._async_run(**kwargs))


class ScreenshotTool(PlaywrightTool):
    """Tool to take a screenshot of a webpage."""
    
    name: str = "Take Screenshot"
    description: str = "Navigate to a URL and take a screenshot."
    
    class Schema(BaseModel):
        """Input for ScreenshotTool."""
        url: str = Field(..., description="URL to navigate to before taking screenshot")
        path: Optional[str] = Field(None, description="File path to save the screenshot")
        wait_for: Optional[str] = Field(None, description="Optional selector to wait for before taking screenshot")
        browser_type: Optional[str] = Field("chromium", description="Browser type: 'chromium', 'firefox', or 'webkit'")
        headless: Optional[bool] = Field(True, description="Whether to run browser in headless mode")
    
    args_schema: Type[BaseModel] = Schema
    
    def _run(self, **kwargs: Any) -> Any:
        """Take a screenshot of a webpage."""
        async def run_sequence():
            async with async_playwright() as p:
                browser_type_name = kwargs.get("browser_type", "chromium")
                if browser_type_name == "chromium":
                    browser_instance = p.chromium
                elif browser_type_name == "firefox":
                    browser_instance = p.firefox
                elif browser_type_name == "webkit":
                    browser_instance = p.webkit
                else:
                    return {"status": "error", "message": f"Unsupported browser type: {browser_type_name}"}
                
                browser = await browser_instance.launch(headless=kwargs.get("headless", True))
                page = await browser.new_page()
                
                try:
                    # Navigate
                    url = kwargs.get("url")
                    wait_for = kwargs.get("wait_for")
                    await page.goto(url, wait_until="networkidle")
                    if wait_for:
                        await page.wait_for_selector(wait_for)
                    
                    # Take screenshot
                    path = kwargs.get("path")
                    if not path:
                        import datetime
                        path = f"screenshot_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
                    
                    await page.screenshot(path=path, full_page=True)
                    return {"status": "success", "url": url, "screenshot_path": path}
                
                except Exception as e:
                    logger.error(f"Error during screenshot sequence: {e}")
                    return {"status": "error", "message": str(e)}
                
                finally:
                    await browser.close()
        
        return asyncio.run(run_sequence())


class ExtractContentTool(PlaywrightTool):
    """Tool to extract content from a webpage."""
    
    name: str = "Extract Web Content"
    description: str = "Navigate to a URL and extract text or HTML content."
    
    class Schema(BaseModel):
        """Input for ExtractContentTool."""
        url: str = Field(..., description="URL to navigate to")
        selector: Optional[str] = Field(None, description="CSS selector for elements to extract (if None, extracts from whole page)")
        extract_type: str = Field("text", description="Type of content to extract: 'text' or 'html'")
        wait_for: Optional[str] = Field(None, description="Optional selector to wait for before extraction")
        browser_type: Optional[str] = Field("chromium", description="Browser type: 'chromium', 'firefox', or 'webkit'")
        headless: Optional[bool] = Field(True, description="Whether to run browser in headless mode")
    
    args_schema: Type[BaseModel] = Schema
    
    def _run(self, **kwargs: Any) -> Any:
        """Extract content from a webpage."""
        async def run_sequence():
            async with async_playwright() as p:
                browser_type_name = kwargs.get("browser_type", "chromium")
                if browser_type_name == "chromium":
                    browser_instance = p.chromium
                elif browser_type_name == "firefox":
                    browser_instance = p.firefox
                elif browser_type_name == "webkit":
                    browser_instance = p.webkit
                else:
                    return {"status": "error", "message": f"Unsupported browser type: {browser_type_name}"}
                
                browser = await browser_instance.launch(headless=kwargs.get("headless", True))
                page = await browser.new_page()
                
                try:
                    # Navigate
                    url = kwargs.get("url")
                    wait_for = kwargs.get("wait_for")
                    await page.goto(url, wait_until="networkidle")
                    if wait_for:
                        await page.wait_for_selector(wait_for)
                    
                    # Extract content
                    selector = kwargs.get("selector")
                    extract_type = kwargs.get("extract_type", "text")
                    
                    if extract_type == "text":
                        if selector:
                            elements = await page.query_selector_all(selector)
                            texts = []
                            for element in elements:
                                text = await element.text_content()
                                if text and text.strip():
                                    texts.append(text.strip())
                            result = {"status": "success", "url": url, "count": len(texts), "texts": texts}
                        else:
                            text = await page.text_content("body")
                            result = {"status": "success", "url": url, "text": text}
                    
                    elif extract_type == "html":
                        if selector:
                            element = await page.query_selector(selector)
                            if not element:
                                return {"status": "error", "message": f"No element found with selector: {selector}"}
                            html = await page.evaluate("(element) => element.outerHTML", element)
                            result = {"status": "success", "url": url, "html": html}
                        else:
                            html = await page.content()
                            result = {"status": "success", "url": url, "html": html}
                    
                    else:
                        result = {"status": "error", "message": f"Unsupported extract_type: {extract_type}"}
                    
                    return result
                
                except Exception as e:
                    logger.error(f"Error during content extraction: {e}")
                    return {"status": "error", "message": str(e)}
                
                finally:
                    await browser.close()
        
        return asyncio.run(run_sequence())


class WebInteractionTool(PlaywrightTool):
    """Tool to interact with elements on a webpage."""
    
    name: str = "Web Interaction"
    description: str = "Navigate to a URL and interact with elements (click, type, etc.)."
    
    class Schema(BaseModel):
        """Input for WebInteractionTool."""
        url: str = Field(..., description="URL to navigate to")
        actions: List[Dict[str, Any]] = Field(..., description="List of actions to perform in sequence")
        browser_type: Optional[str] = Field("chromium", description="Browser type: 'chromium', 'firefox', or 'webkit'")
        headless: Optional[bool] = Field(True, description="Whether to run browser in headless mode")
    
    args_schema: Type[BaseModel] = Schema
    
    def _run(self, **kwargs: Any) -> Any:
        """Perform a sequence of interactions on a webpage."""
        url = kwargs.get("url")
        actions = kwargs.get("actions", [])
        browser_type = kwargs.get("browser_type", "chromium")
        headless = kwargs.get("headless", True)
        
        if not url or not actions:
            return {"status": "error", "message": "Both URL and actions are required"}
        
        async def run_sequence():
            async with async_playwright() as p:
                if browser_type == "chromium":
                    browser_instance = p.chromium
                elif browser_type == "firefox":
                    browser_instance = p.firefox
                elif browser_type == "webkit":
                    browser_instance = p.webkit
                else:
                    return {"status": "error", "message": f"Unsupported browser type: {browser_type}"}
                
                browser = await browser_instance.launch(headless=headless)
                page = await browser.new_page()
                results = []
                
                try:
                    # Navigate to the initial URL
                    await page.goto(url, wait_until="networkidle")
                    results.append({"action": "goto", "url": url, "status": "success"})
                    
                    # Perform each action in sequence
                    for action_info in actions:
                        action_type = action_info.get("type")
                        
                        if action_type == "click":
                            selector = action_info.get("selector")
                            if not selector:
                                results.append({"action": "click", "status": "error", "message": "Selector is required for click action"})
                                continue
                            
                            await page.wait_for_selector(selector)
                            await page.click(selector)
                            results.append({"action": "click", "selector": selector, "status": "success"})
                        
                        elif action_type == "type":
                            selector = action_info.get("selector")
                            text = action_info.get("text")
                            if not selector or not text:
                                results.append({
                                    "action": "type", 
                                    "status": "error", 
                                    "message": "Both selector and text are required for type action"
                                })
                                continue
                            
                            await page.wait_for_selector(selector)
                            await page.fill(selector, text)
                            results.append({"action": "type", "selector": selector, "text": text, "status": "success"})
                        
                        elif action_type == "wait":
                            selector = action_info.get("selector")
                            timeout = action_info.get("timeout", 30000)
                            if not selector:
                                results.append({
                                    "action": "wait", 
                                    "status": "error", 
                                    "message": "Selector is required for wait action"
                                })
                                continue
                            
                            await page.wait_for_selector(selector, timeout=timeout)
                            results.append({"action": "wait", "selector": selector, "status": "success"})
                        
                        elif action_type == "goto":
                            new_url = action_info.get("url")
                            if not new_url:
                                results.append({
                                    "action": "goto", 
                                    "status": "error", 
                                    "message": "URL is required for goto action"
                                })
                                continue
                            
                            await page.goto(new_url, wait_until="networkidle")
                            results.append({"action": "goto", "url": new_url, "status": "success"})
                        
                        elif action_type == "screenshot":
                            path = action_info.get("path")
                            if not path:
                                import datetime
                                path = f"screenshot_{datetime.datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.png"
                            
                            await page.screenshot(path=path, full_page=True)
                            results.append({"action": "screenshot", "path": path, "status": "success"})
                        
                        elif action_type == "extract_text":
                            selector = action_info.get("selector")
                            if not selector:
                                results.append({
                                    "action": "extract_text", 
                                    "status": "error", 
                                    "message": "Selector is required for extract_text action"
                                })
                                continue
                            
                            elements = await page.query_selector_all(selector)
                            texts = []
                            for element in elements:
                                text = await element.text_content()
                                if text and text.strip():
                                    texts.append(text.strip())
                            
                            results.append({
                                "action": "extract_text", 
                                "selector": selector, 
                                "texts": texts, 
                                "count": len(texts),
                                "status": "success"
                            })
                        
                        elif action_type == "evaluate":
                            javascript = action_info.get("javascript")
                            if not javascript:
                                results.append({
                                    "action": "evaluate", 
                                    "status": "error", 
                                    "message": "JavaScript is required for evaluate action"
                                })
                                continue
                            
                            result = await page.evaluate(javascript)
                            results.append({
                                "action": "evaluate", 
                                "result": result,
                                "status": "success"
                            })
                        
                        else:
                            results.append({
                                "action": action_type, 
                                "status": "error", 
                                "message": f"Unsupported action type: {action_type}"
                            })
                    
                    return {"status": "success", "results": results}
                
                except Exception as e:
                    logger.error(f"Error during interaction sequence: {e}")
                    return {"status": "error", "message": str(e), "partial_results": results}
                
                finally:
                    await browser.close()
        
        return asyncio.run(run_sequence())
