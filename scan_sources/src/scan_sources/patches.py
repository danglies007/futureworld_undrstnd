# Patches to get Gemini 2.5pro API working with crew AI


from typing import Any, Dict, Optional
import json
import re

def clean_json_response(response: str) -> str:
    """Remove markdown formatting and extract JSON from responses."""
    # Check for code blocks
    code_block_pattern = r"```(?:json)?([\s\S]*?)```"
    matches = re.findall(code_block_pattern, response)
    
    if matches:
        # Use the first JSON code block found
        return matches[0].strip()
    
    # Try to find JSON-like content
    json_pattern = r"(\{[\s\S]*\})"
    matches = re.findall(json_pattern, response)
    
    if matches:
        # Use the first JSON-like content found
        return matches[0].strip()
        
    # Return the original if no pattern matches
    return response

def safe_parse_json(json_string: str) -> Dict[str, Any]:
    """Safely parse JSON with better error handling."""
    try:
        return json.loads(json_string)
    except json.JSONDecodeError:
        # Try cleaning the string
        cleaned = clean_json_response(json_string)
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON: {str(e)}, Content: {cleaned[:100]}...")

# Monkey patch CrewAI's converter if possible
def apply_patches():
    try:
        from crewai.utilities import converter
        
        # Save the original function
        original_to_pydantic = converter.ModelConverter.to_pydantic
        
        # Define a new function with better error handling
        def patched_to_pydantic(self, current_attempt=0):
            try:
                # First try to clean the response
                cleaned_response = clean_json_response(self.response)
                result = self.model.model_validate_json(cleaned_response)
                return result
            except Exception as e:
                if current_attempt < 3:  # Try a few times
                    # For subsequent attempts, try different strategies
                    return original_to_pydantic(self, current_attempt + 1)
                else:
                    raise converter.ConverterError(f"Failed to convert: {str(e)}")
        
        # Apply the patch
        converter.ModelConverter.to_pydantic = patched_to_pydantic
        
        print("Successfully applied CrewAI patches")
    except Exception as e:
        print(f"Failed to apply CrewAI patches: {str(e)}")