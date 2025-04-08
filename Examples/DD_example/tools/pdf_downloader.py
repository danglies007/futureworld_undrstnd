import os
import logging
from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests

logger = logging.getLogger(__name__)

# Define reference directory path - same level as main.py
REFERENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reference")

class PDFDownloaderSchema(BaseModel):
    """Input schema for PDFDownloaderTool."""
    url: str = Field(
        ..., 
        description="The URL of the PDF file to download. Must be a direct link to a PDF file."
    )

class PDFDownloaderTool(BaseTool):
    name: str = "Download PDF Tool"
    description: str = "A tool that can be used to download PDF files from URLs and save them to a reference directory"
    args_schema: Type[BaseModel] = PDFDownloaderSchema

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__()
        os.makedirs(REFERENCE_DIR, exist_ok=True)
        logger.info(f"Using reference directory: {REFERENCE_DIR}")
        
        # Setup session with reasonable timeouts
        self._session = requests.Session()
        self._session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })

    def _is_likely_pdf_url(self, url: str) -> tuple[bool, str]:
        """
        Check if the URL is likely to point to a PDF and is accessible.
        Returns (is_valid, message)
        """
        # Check URL pattern
        url_lower = url.lower()
        
        try:
            # Try HEAD request first to check if URL exists and get content type
            head = self._session.head(url, timeout=5, allow_redirects=True)
            
            # Check if URL exists
            if head.status_code == 404:
                return False, "URL not found (404 error)"
            elif head.status_code != 200:
                return False, f"URL returned status code {head.status_code}"
            
            # Check content type
            content_type = head.headers.get('content-type', '').lower()
            if 'pdf' in content_type or 'application/pdf' in content_type:
                return True, "Content-Type indicates PDF"
            
            # If content type check fails, check URL extension
            if url_lower.endswith('.pdf'):
                return True, "URL ends with .pdf"
            
            return False, f"URL does not appear to be a PDF (Content-Type: {content_type})"
            
        except requests.exceptions.ConnectionError:
            return False, "Could not connect to the server"
        except requests.exceptions.Timeout:
            return False, "Request timed out"
        except requests.exceptions.RequestException as e:
            return False, f"Error checking URL: {str(e)}"

    def _sanitize_filename(self, url: str) -> str:
        """Create a safe filename from URL."""
        filename = os.path.basename(url)
        if not filename or not filename.strip():
            filename = "downloaded.pdf"
        elif not filename.lower().endswith('.pdf'):
            filename += '.pdf'

        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename

    def _run(self, url: str, **kwargs: Any) -> str:
        """Download a PDF from a URL and save it to the reference directory."""
        try:
            logger.info(f"Validating URL: {url}")
            
            # Validate URL first
            is_valid, message = self._is_likely_pdf_url(url)
            if not is_valid:
                error_msg = f"Could not download PDF: {message}"
                logger.warning(error_msg)
                return error_msg
            
            logger.info(f"Downloading PDF from: {url}")
            
            # Download PDF with timeout
            response = self._session.get(url, stream=True, timeout=(5, 30))
            response.raise_for_status()
            
            # Save file
            filename = self._sanitize_filename(url)
            filepath = os.path.join(REFERENCE_DIR, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Successfully downloaded PDF: {filename}")
            return f"Successfully downloaded PDF: {filename}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error downloading PDF from {url}: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error downloading PDF: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def _arun(self, url: str, **kwargs: Any) -> str:
        """Async implementation of the tool."""
        return self._run(url, **kwargs)
