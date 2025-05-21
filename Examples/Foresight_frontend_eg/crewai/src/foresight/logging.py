#!/usr/bin/env python

import os
import sys
import logging
from datetime import datetime

# Custom class to redirect stdout/stderr to logger
class LoggerWriter:
    def __init__(self, write_function):
        self.write_function = write_function
        self.buffer = ''
        
    def write(self, message):
        if message and message.strip():
            self.write_function(message.rstrip())
            
    def flush(self):
        pass

def setup_logging():
    """Configure logging to capture all CrewAI process output"""
    # Get the root directory of the project
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_file = os.path.join(root_dir, 'crewai_process.log')
    
    # Create a logger
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    
    # Create handlers
    console_handler = logging.StreamHandler(sys.stdout)
    file_handler = logging.FileHandler(log_file, mode='w')
    
    # Set level for handlers
    console_handler.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    
    # Create a formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    # Add the handlers to the logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    # Redirect stdout and stderr to the logger
    sys.stdout = LoggerWriter(logger.info)
    sys.stderr = LoggerWriter(logger.error)
    
    logging.info("Logging initialized for CrewAI process")
    return logger

def backup_log_file(suffix=None):
    """Create a backup of the current log file with optional suffix"""
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_file = os.path.join(root_dir, 'crewai_process.log')
    
    if os.path.exists(log_file):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        suffix_text = f"_{suffix}" if suffix else ""
        backup_log_file = os.path.join(root_dir, f'crewai_process{suffix_text}_{timestamp}.log')
        
        try:
            # Copy the log file to preserve logs
            import shutil
            shutil.copy2(log_file, backup_log_file)
            print(f"Logs backed up to: {backup_log_file}")
            return backup_log_file
        except Exception as e:
            print(f"Error backing up log file: {e}")
            return None
    
    return None
