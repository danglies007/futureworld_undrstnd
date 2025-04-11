# litellm_patch.py
import litellm
import functools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("litellm_patch")

# Save reference to the original function
original_completion = litellm.completion

# Create a patched version that removes stop words for Perplexity
@functools.wraps(original_completion)
def patched_completion(*args, **kwargs):
    model = kwargs.get('model', '')
    provider = kwargs.get('custom_llm_provider', '')
    
    # Check if using Perplexity
    if 'perplexity' in model or 'perplexity' in provider:
        logger.info("Perplexity detected, applying special handling")
        
        # Remove stop words parameter
        if 'stop' in kwargs:
            logger.info("Removing 'stop' parameter")
            del kwargs['stop']
        
        # Ensure API base is correctly set
        kwargs['api_base'] = "https://api.perplexity.ai"
        
        # Set proper values for Perplexity
        kwargs['custom_llm_provider'] = 'perplexity'
    
    # Call the original function with modified kwargs
    return original_completion(*args, **kwargs)

# Replace the original function with our patched version
litellm.completion = patched_completion

# Log that the patch has been applied
logger.info("LiteLLM patched for Perplexity compatibility")