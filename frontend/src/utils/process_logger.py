"""
Process Logger Utility

A standalone utility for logging process output to files with timestamps and metadata.
Uses Python's standard logging library for robust logging capabilities.
Can be used independently in any project that needs to log process output.
"""

import os
import sys
import logging
import datetime
from pathlib import Path
from typing import Optional, List, Union, Dict, Any

class ProcessLogger:
    """A utility class for logging process output to files using Python's standard logging library."""
    
    def __init__(
        self, 
        logs_dir: Union[str, Path] = None, 
        prefix: str = "process_output",
        log_level: int = logging.DEBUG
    ):
        """
        Initialize the process logger.
        
        Args:
            logs_dir: Directory to store log files. If None, defaults to ~/Documents/Coding/undrstnd/logs
            prefix: Prefix for log filenames
            log_level: Logging level (default: DEBUG)
        """
        if logs_dir is None:
            logs_dir = Path(os.path.expanduser("~")) / "Documents" / "Coding" / "undrstnd" / "logs"
        elif isinstance(logs_dir, str):
            logs_dir = Path(logs_dir)
            
        self.logs_dir = logs_dir
        self.prefix = prefix
        self.log_level = log_level
        self.log_file_path = None
        self.logger = None
        
        # Ensure logs directory exists
        self.logs_dir.mkdir(exist_ok=True, parents=True)
    
    def start_logging(self, title: str, command: Optional[List[str]] = None, cwd: Optional[str] = None) -> Path:
        """
        Start logging a new process.
        
        Args:
            title: Title or description of the process
            command: Command being executed (list of command parts)
            cwd: Working directory for the command
            
        Returns:
            Path to the log file
        """
        # Generate log filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_name = f"{self.prefix}_{timestamp}"
        self.log_file_path = self.logs_dir / f"{log_name}.log"
        
        # Configure logger
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(self.log_level)
        
        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Create file handler
        file_handler = logging.FileHandler(self.log_file_path)
        file_handler.setLevel(self.log_level)
        
        # Create formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        
        # Add handler to logger
        self.logger.addHandler(file_handler)
        
        # Log header information
        self.logger.info(f"=== Process Output Log: {title} ===")
        if command:
            self.logger.info(f"Command: {' '.join(str(c) for c in command)}")
        if cwd:
            self.logger.info(f"Working Directory: {cwd}")
        self.logger.info(f"Start Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        self.logger.info("=== Output Begins ===")
        
        return self.log_file_path
    
    def log(self, content: str, level: int = logging.INFO) -> None:
        """
        Log content to the log file.
        
        Args:
            content: Content to log
            level: Logging level (default: INFO)
        """
        if self.logger:
            # Remove trailing newlines for cleaner logging
            content = content.rstrip('\n')
            if content:  # Only log non-empty content
                if level == logging.DEBUG:
                    self.logger.debug(content)
                elif level == logging.INFO:
                    self.logger.info(content)
                elif level == logging.WARNING:
                    self.logger.warning(content)
                elif level == logging.ERROR:
                    self.logger.error(content)
                elif level == logging.CRITICAL:
                    self.logger.critical(content)
                else:
                    self.logger.info(content)
    
    def log_debug(self, content: str) -> None:
        """Log content at DEBUG level."""
        self.log(content, logging.DEBUG)
    
    def log_info(self, content: str) -> None:
        """Log content at INFO level."""
        self.log(content, logging.INFO)
    
    def log_warning(self, content: str) -> None:
        """Log content at WARNING level."""
        self.log(content, logging.WARNING)
    
    def log_error(self, content: str) -> None:
        """Log content at ERROR level."""
        self.log(content, logging.ERROR)
    
    def end_logging(self, return_code: Optional[int] = None, error: Optional[Exception] = None) -> None:
        """
        End logging and close the log file.
        
        Args:
            return_code: Return code of the process (if available)
            error: Exception that occurred (if any)
        """
        if self.logger:
            if error:
                self.logger.error(f"=== Process failed with error: {error} ===")
            elif return_code is not None:
                if return_code == 0:
                    self.logger.info(f"=== Process completed successfully with return code: {return_code} ===")
                else:
                    self.logger.error(f"=== Process completed with non-zero return code: {return_code} ===")
            else:
                self.logger.info("=== Process completed ===")
                
            self.logger.info(f"End Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Close handlers
            for handler in self.logger.handlers:
                handler.close()
                self.logger.removeHandler(handler)
    
    def get_log_file_path(self) -> Optional[Path]:
        """
        Get the path to the current log file.
        
        Returns:
            Path to the log file, or None if no logging is active
        """
        return self.log_file_path
    
    def __enter__(self):
        """Support for context manager usage."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure log file is closed when exiting context."""
        if exc_val:
            self.end_logging(error=exc_val)
        else:
            self.end_logging()
