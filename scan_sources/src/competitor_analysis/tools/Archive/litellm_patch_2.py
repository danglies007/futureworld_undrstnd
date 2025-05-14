# litellm_patch.py
import litellm
import functools
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("litellm_patch")

# Save reference to the original function
original_completion = litellm.completion

# Create a patched version that fixes issues with Perplexity
@functools.wraps(original_completion)
def patched_completion(*args, **kwargs):
    model = kwargs.get('model', '')
    provider = kwargs.get('custom_llm_provider', '')
    
    # Check if using Perplexity
    if 'perplexity' in model or 'perplexity' in provider:
        logger.info("Perplexity detected, applying special handling")
        
        # 1. Remove stop words parameter
        if 'stop' in kwargs:
            logger.info("Removing 'stop' parameter")
            del kwargs['stop']
        
        # 2. Ensure messages are properly formatted
        if 'messages' in kwargs:
            # Check if any message has empty content
            messages = kwargs['messages']
            filtered_messages = []
            
            for msg in messages:
                # Skip messages with empty content
                if 'content' in msg and (msg['content'] is None or msg['content'] == ''):
                    logger.info(f"Skipping empty message with role: {msg.get('role', 'unknown')}")
                    continue
                
                # Ensure message has required fields
                if 'role' in msg and 'content' in msg:
                    filtered_messages.append(msg)
                else:
                    logger.warning(f"Skipping malformed message: {msg}")
            
            # If we have no valid messages, add a default system message
            if not filtered_messages:
                logger.info("No valid messages found, adding default system message")
                filtered_messages = [
                    {"role": "system", "content": "You are a helpful assistant."}
                ]
            
            # Replace messages with filtered ones
            kwargs['messages'] = filtered_messages
            logger.info(f"Using {len(filtered_messages)} messages")
        
        # 3. Ensure valid model name format for Perplexity
        if 'model' in kwargs and not kwargs['model'].startswith('perplexity/'):
            kwargs['model'] = f"perplexity/{kwargs['model']}"
            logger.info(f"Updated model name to {kwargs['model']}")
        
        # 4. Ensure API base is correctly set
        kwargs['api_base'] = "https://api.perplexity.ai"
        
        # 5. Set proper values for Perplexity
        kwargs['custom_llm_provider'] = 'perplexity'
    
    # Log the final parameters
    logger.info(f"Final model: {kwargs.get('model')}")
    logger.info(f"Provider: {kwargs.get('custom_llm_provider')}")
    
    # Call the original function with modified kwargs
    return original_completion(*args, **kwargs)

# Replace the original function with our patched version
litellm.completion = patched_completion

# Log that the patch has been applied
logger.info("LiteLLM patched for Perplexity compatibility")