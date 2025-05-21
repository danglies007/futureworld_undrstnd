"""
Utility module for running processes with real-time output in Streamlit.
"""
import os
import subprocess
import streamlit as st
import html
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Any
from ansi2html import Ansi2HTMLConverter
from utils.process_logger import ProcessLogger

# Initialize the ANSI to HTML converter
conv = Ansi2HTMLConverter(inline=True)

def format_markdown_for_display(markdown_text: str) -> str:
    """Format markdown text for better display in Streamlit.
    
    This function processes markdown text to ensure proper rendering in Streamlit,
    handling ANSI color codes, newlines, code blocks, and other markdown elements correctly.
    
    Args:
        markdown_text: The markdown text to format
        
    Returns:
        Formatted markdown text ready for display
    """
    # First convert any ANSI color codes to HTML
    try:
        html_text = conv.convert(markdown_text)
        
        # Remove the default styling from ansi2html that might interfere with our styling
        html_text = re.sub(r'<style.*?</style>', '', html_text, flags=re.DOTALL)
        
        # Clean up any remaining ANSI escape sequences that weren't converted
        html_text = re.sub(r'\x1b\[[0-9;]*[mK]', '', html_text)
        
        return html_text
    except Exception as e:
        # If conversion fails, fall back to basic formatting
        st.warning(f"Error converting ANSI codes: {e}. Falling back to basic formatting.")
        
        # Replace escaped newlines with actual newlines
        formatted_text = markdown_text.replace('\\n', '\n')
        
        # Ensure code blocks are properly formatted
        formatted_text = re.sub(r'```(\w+)\\n', r'```\1\n', formatted_text)
        formatted_text = re.sub(r'\\n```', r'\n```', formatted_text)
        
        # Handle bullet points and other markdown elements
        formatted_text = re.sub(r'\\n\s*-\s', r'\n- ', formatted_text)
        
        # Handle headers
        for i in range(6, 0, -1):
            hashes = '#' * i
            formatted_text = re.sub(fr'\n\s*{re.escape(hashes)}\s', f'\n{hashes} ', formatted_text)
        
        # Escape any HTML to prevent injection
        return html.escape(formatted_text)

def run_process_with_realtime_output(
    cmd: List[str], 
    cwd: str, 
    title: str = "Process Output", 
    expanded: bool = True,
    env: Optional[Dict[str, str]] = None,
    show_debug_logs: bool = False,
    log_to_file: bool = True,
    use_task_viewer: bool = True
) -> Tuple[int, str]:
    """
    Run a subprocess and display its output in real-time in a Streamlit expander.
    
    Args:
        cmd: Command to run as a list of strings
        cwd: Working directory for the command
        title: Title for the expander
        expanded: Whether the expander should be expanded by default
        env: Environment variables to pass to the subprocess
        show_debug_logs: Whether to show debug logs
        log_to_file: Whether to log output to a file
        use_task_viewer: Whether to use the task-based log viewer
    
    Returns:
        Tuple of (return_code, output_text)
    """
    output_text = ""
    
    # Create an expander for the output
    with st.expander(title, expanded=expanded):
        # Set up logging to file if enabled
        logger = None
        if log_to_file:
            logger = ProcessLogger()
            log_file_path = logger.start_logging(title, cmd, cwd)
            st.info(f"Logging output to: {log_file_path}")
        
        # Create tabs for different views if using task viewer
        if use_task_viewer:
            tab1, tab2 = st.tabs(["Live Output", "Task View"])
            with tab1:
                output_area = st.empty()
            with tab2:
                task_view_area = st.empty()
                st.info("Task view will be available once the process completes.")
        else:
            output_area = st.empty()
        
        try:
            # Prepare environment variables
            process_env = os.environ.copy()
            if env:
                process_env.update(env)
            
            # Run the process with real-time output
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                cwd=cwd,
                env=process_env
            )
            
            # Display output in real-time
            for line in iter(process.stdout.readline, ''):
                # More comprehensive check for LiteLLM debug logs
                is_debug_log = ("LiteLLM" in line or 
                              "DEBUG:" in line or 
                              "Request to litellm:" in line or 
                              "litellm.completion" in line or
                              "utils.py:" in line or
                              "litellm_logging.py:" in line or
                              "cost_calculator.py:" in line)
                
                # If it's a debug log and we're showing debug logs, add it with special formatting
                if is_debug_log and show_debug_logs:
                    # Add debug logs with a special marker for styling
                    output_text += f"<span class='debug-log'>{line}</span>"
                # If it's not a debug log, add it normally
                elif not is_debug_log:
                    output_text += line
                
                # Print to terminal for debugging
                print(line, end='', flush=True)
                
                # Write to log file if enabled
                if log_to_file and logger:
                    logger.log(line)
                
                # Convert ANSI color codes to HTML
                html_output = conv.convert(output_text)
                
                # Clean up any HTML artifacts in the output
                cleaned_html = html_output.replace('<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">', '')
                
                # Update the Streamlit display with proper ANSI color rendering and clean formatting
                output_area.markdown(
                    f"""<style>
                    .debug-log {{color: #888; font-style: italic; font-size: 0.9em;}}
                    .output-container {{background-color: #f0f2f6; padding: 10px; border-radius: 5px;}}
                    .output-text {{white-space: pre-wrap; word-wrap: break-word; overflow-wrap: break-word; 
                                margin: 0; font-family: monospace; line-height: 1.4;}}
                    </style>
                    <div class="output-container">
                      <div class="output-text">{cleaned_html}</div>
                    </div>""", 
                    unsafe_allow_html=True
                )
            
            # Wait for the process to complete
            return_code = process.wait()
            
            if return_code == 0:
                st.success(f"{title} completed successfully!")
            else:
                st.error(f"{title} failed with return code {return_code}")
            
            # Add final log entry and close log file if enabled
            if log_to_file and logger:
                logger.end_logging(return_code)
                log_path = logger.get_log_file_path()
                st.success(f"Log file saved to: {log_path}")
                
                # Show task log viewer if enabled
                if use_task_viewer:
                    from utils.task_log_viewer import display_task_selector
                    with tab2:
                        # Clear the placeholder message
                        task_view_area.empty()
                        # Display the task selector
                        display_task_selector(log_path)
                
            # Exit the expander context before adding buttons
            
            # Return the values early to avoid any form context issues
            return return_code, output_text
        
        except Exception as e:
            error_msg = f"Error running {title}: {e}"
            st.error(error_msg)
            if logger:
                logger.log_error(error_msg)
            return 1, error_msg

# Function to display log analysis buttons outside of any form context
def display_log_analysis_buttons(log_path: str) -> None:
    """Display buttons for log analysis outside of any form context."""
    if not log_path or not os.path.exists(log_path):
        return
        
    st.markdown("### Log Analysis")  # Add a separator
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Detailed Log Report", key=f"gen_report_{log_path}"):
            from utils.log_analyzer import analyze_log_file, generate_report_file
            try:
                # Analyze the log file
                metrics = analyze_log_file(log_path)
                # Generate the report
                report_path = generate_report_file(metrics, log_path)
                st.success(f"Log report generated: {report_path}")
                # Store the report path in session state for the view button
                st.session_state["latest_report_path"] = report_path
            except Exception as e:
                st.error(f"Error generating log report: {e}")
    
    with col2:
        # Only enable the view button if a report has been generated
        if "latest_report_path" in st.session_state:
            if st.button("View Log Report", key=f"view_report_{log_path}"):
                report_path = st.session_state["latest_report_path"]
                if os.path.exists(report_path):
                    with open(report_path, "r") as f:
                        report_content = f.read()
                    st.markdown("### Log Analysis Report")
                    st.text_area("Report Content", report_content, height=500)
                else:
                    st.error(f"Report file not found: {report_path}")
        else:
            st.button("View Log Report", disabled=True, key=f"view_report_disabled_{log_path}", help="Generate a report first")
            
            # Log the error if logging is enabled
            if log_to_file and logger:
                logger.end_logging(error=e)
                st.info(f"Error log saved to: {logger.get_log_file_path()}")
            
            return 1, output_text

def check_output_files(
    file_paths: List[str], 
    file_descriptions: Optional[List[str]] = None
) -> bool:
    """
    Check if output files were generated and display their status.
    
    Args:
        file_paths: List of file paths to check
        file_descriptions: Optional list of descriptions for each file
    
    Returns:
        True if at least one file exists, False otherwise
    """
    if file_descriptions is None:
        file_descriptions = [f"File {i+1}" for i in range(len(file_paths))]
    
    found_files = False
    
    for path, desc in zip(file_paths, file_descriptions):
        if os.path.exists(path):
            found_files = True
            st.success(f"{desc} was generated: {path}")
    
    if not found_files:
        st.warning("No output files were generated. Check the process output for details.")
    
    return found_files
