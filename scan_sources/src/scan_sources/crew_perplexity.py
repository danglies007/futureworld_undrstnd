# crew_perplexity.py
from crewai import LLM
import os

class PerplexityLLM(LLM):
    """A custom LLM adapter for CrewAI that properly works with Perplexity"""
    
    def __init__(self, api_key=None, model="perplexity/sonar"):
        """Initialize the Perplexity LLM adapter"""
        # Set the API key if provided
        if api_key:
            os.environ["PERPLEXITYAI_API_KEY"] = api_key
            
        # Always ensure provider is set correctly
        super().__init__(
            provider="openai",  # Changed from "perplexity" to "openai"
            model=model,
            api_key=os.getenv("PERPLEXITYAI_API_KEY"),
            config={
                "api_base": "https://api.perplexity.ai",
                "request_timeout": 120
            }
        )
        
    def _prepare_messages(self, messages):
        """Ensure messages are valid before sending to LiteLLM"""
        # Filter out invalid messages
        valid_messages = []
        for msg in messages:
            if msg.get('content') and msg.get('role'):
                valid_messages.append(msg)
        
        # Ensure we have at least one message
        if not valid_messages:
            valid_messages = [{"role": "system", "content": "You are a helpful assistant."}]
        
        # Add a user message at the end if the last message isn't from the user
        if valid_messages and valid_messages[-1].get('role') != 'user':
            valid_messages.append({
                "role": "user",
                "content": "Please continue analyzing."
            })
            
        return valid_messages
    
    def call(self, messages=None, **kwargs):
        """Override call to ensure proper message formatting"""
        if messages:
            messages = self._prepare_messages(messages)
        return super().call(messages=messages, **kwargs)