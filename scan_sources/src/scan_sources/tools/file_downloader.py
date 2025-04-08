import os
import logging
import mimetypes
from typing import Any, Type
from pydantic import BaseModel, Field
from crewai.tools import BaseTool
import requests

logger = logging.getLogger(__name__)

# Define reference directory path - same level as main.py
REFERENCE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "reference")

class FileDownloaderSchema(BaseModel):
    """Input schema for FileDownloaderTool."""
    url: str = Field(
        ..., 
        description="The URL of the file to download."
    )

class FileDownloaderTool(BaseTool):
    name: str = "Download File Tool"
    description: str = "A tool that can be used to download files from URLs and save them to a reference directory"
    args_schema: Type[BaseModel] = FileDownloaderSchema

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

    def _check_url_accessibility(self, url: str) -> tuple[bool, str, str]:
        """
        Check if the URL is accessible and get its content type.
        Returns (is_valid, content_type, message)
        """
        try:
            # Try HEAD request first to check if URL exists and get content type
            head = self._session.head(url, timeout=5, allow_redirects=True)
            
            # Check if URL exists
            if head.status_code == 404:
                return False, "", "URL not found (404 error)"
            elif head.status_code != 200:
                return False, "", f"URL returned status code {head.status_code}"
            
            # Get content type
            content_type = head.headers.get('content-type', '').lower()
            if not content_type:
                # If no content type, try to guess from URL
                content_type, _ = mimetypes.guess_type(url)
                content_type = content_type or 'application/octet-stream'
            
            return True, content_type, "URL is accessible"
            
        except requests.exceptions.ConnectionError:
            return False, "", "Could not connect to the server"
        except requests.exceptions.Timeout:
            return False, "", "Request timed out"
        except requests.exceptions.RequestException as e:
            return False, "", f"Error checking URL: {str(e)}"

    def _get_extension_from_content_type(self, content_type: str, url: str) -> str:
        """Get file extension from content type or URL."""
        if content_type:
            ext = mimetypes.guess_extension(content_type)
            if ext:
                return ext
        
        # Fall back to URL extension
        _, ext = os.path.splitext(url)
        return ext if ext else ''

    def _sanitize_filename(self, url: str, content_type: str) -> str:
        """Create a safe filename from URL and content type."""
        # Get base filename from URL
        filename = os.path.basename(url)
        
        # If no filename in URL, create generic one
        if not filename or not filename.strip():
            filename = "downloaded"
        
        # Ensure proper extension
        _, current_ext = os.path.splitext(filename)
        if not current_ext:
            ext = self._get_extension_from_content_type(content_type, url)
            filename += ext

        # Replace invalid characters
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        
        return filename

    def _run(self, url: str, **kwargs: Any) -> str:
        """Download a file from a URL and save it to the reference directory."""
        try:
            logger.info(f"Validating URL: {url}")
            
            # Validate URL first
            is_valid, content_type, message = self._check_url_accessibility(url)
            if not is_valid:
                error_msg = f"Could not download file: {message}"
                logger.warning(error_msg)
                return error_msg
            
            logger.info(f"Downloading file from: {url}")
            
            # Download file with timeout
            response = self._session.get(url, stream=True, timeout=(5, 30))
            response.raise_for_status()
            
            # Save file
            filename = self._sanitize_filename(url, content_type)
            filepath = os.path.join(REFERENCE_DIR, filename)
            
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Successfully downloaded file: {filename}")
            return f"Successfully downloaded file: {filename}"
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error downloading file from {url}: {str(e)}"
            logger.error(error_msg)
            return error_msg
        except Exception as e:
            error_msg = f"Unexpected error downloading file: {str(e)}"
            logger.error(error_msg)
            return error_msg

    async def _arun(self, url: str, **kwargs: Any) -> str:
        """Async implementation of the tool."""
        return self._run(url, **kwargs)
