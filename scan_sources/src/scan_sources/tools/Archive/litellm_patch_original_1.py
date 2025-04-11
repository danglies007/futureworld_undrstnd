# litellm_patch.py
import litellm
import functools

# Save reference to the original function
original_completion = litellm.completion

# Create a patched version that removes stop words for Perplexity
@functools.wraps(original_completion)
def patched_completion(*args, **kwargs):
    # Check if using Perplexity
    model = kwargs.get('model', '')
    if 'perplexity' in model or kwargs.get('custom_llm_provider') == 'perplexity':
        # Remove the stop parameter if it exists
        if 'stop' in kwargs:
            del kwargs['stop']
            
    # Call the original function with modified kwargs
    return original_completion(*args, **kwargs)

# Replace the original function with our patched version
litellm.completion = patched_completion