# Create this in a new file named crew_perplexity.py
from crewai import LLM
import os

class PerplexityLLM(LLM):
    """A custom LLM adapter for CrewAI that properly works with Perplexity"""
    
    def __init__(self, api_key=None, model="sonar"):
        """Initialize the Perplexity LLM adapter"""
        # Set the API key if provided
        if api_key:
            os.environ["PERPLEXITYAI_API_KEY"] = api_key
            
        # Always ensure provider is set correctly
        super().__init__(
            provider="perplexity",
            model=model,
            config={
                "request_timeout": 120,
                "litellm_params": {
                    "custom_llm_provider": "perplexity",
                    "api_base": "https://api.perplexity.ai"
                }
            }
        )
        
    def _prepare_messages(self, messages):
        """Ensure messages are valid before sending to LiteLLM"""
        valid_messages = []
        for msg in messages:
            if msg.get('content') and msg.get('role'):
                valid_messages.append(msg)
        
        # Ensure we have at least one message
        if not valid_messages:
            valid_messages = [{"role": "system", "content": "You are a helpful assistant."}]
            
        return valid_messages
    
    def call(self, prompt=None, messages=None, **kwargs):
        """Override call to ensure proper message formatting"""
        if messages:
            messages = self._prepare_messages(messages)
        return super().call(prompt=prompt, messages=messages, **kwargs)