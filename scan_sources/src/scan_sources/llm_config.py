import litellm
import os
# Custom Perplexity patch - using litellm_patch.py
import litellm_patch

# Importing patch PerplexityLLM
from crew_perplexity import PerplexityLLM


from crewai import LLM

# Define LLMs with token tracking
# Reasoning
llm_gpto4_mini = LLM(model="o4-mini-2025-04-16") # $1.10/$4.40
llm_gpto3_mini = LLM(model="o3-mini-2025-01-31") # Fast flexible reasoning $1.10/4.40
llm_gpto1_mini = LLM(model="o1-mini-2024-09-12") # Faster more affordable reasoning than o1 $1.10/4.40
llm_gemini_2_5_pro = LLM(model="gemini/gemini-2.5-pro-exp-03-25", max_rpm=5) # 
llm_gemini_2_5_pro_preview = LLM(model="gemini/gemini-2.5-pro-preview") # Pro reasoning $2.50/$15

# Chat
llm_gpt_4_1 = LLM(model="gpt-4.1-2025-04-14") # $2.00/$8.00
llm_gpt_4_1_mini = LLM(model="gpt-4.1-mini-2025-04-14") # $0.4/$1.60
llm_gpt4o_mini = LLM(model="gpt-4o-mini-2024-07-18") # Fast and cheap $0.15/$0.60
llm_claude_3_5_hauku = LLM(model="claude-3-5-hauku-latest") # Fast and cheap $.80/$4
llm_gpt4o = LLM(model="gpt-4o-2024-11-20") # Fast intelligent $2.50/$10
llm_claude_3_7_sonnet = LLM(model="claude-3-7-sonnet-latest")# Fast intelligent $3/$15 - May need rate limiting via litellm.rate_limit_config
llm_claude_3_5_sonnet = LLM(model="claude-3-5-sonnet-latest") # Fast intelligent $3/$15
llm_gemini_2_0_flash = LLM(model="gemini/gemini-2.0-flash") # Fast intelligent $0.1/$0.4
llm_gemini_2_5_flash = LLM(model="gemini/gemini-2.5-flash-preview-04-17") # Fast intelligent $0.15/$0.6
llm_gemini_2_0_flash_lite = LLM(model="gemini/gemini-2.0-flash-lite") # Fast intelligent $.075/$0.30


# Customised
llm_gpt4o_accurate = LLM(model="gpt-4o-2024-11-20", temperature=0.1, max_completion_tokens=8000, max_tokens=8000)
llm_gpt4o_mini_accurate = LLM(model="gpt-4o-mini-2024-07-18", temperature=0.1, max_completion_tokens=8000, max_tokens=8000)

# Perplexity
llm_perplexity_sonar = LLM(model="perplexity/sonar") #Fast searc
llm_perplexity_sonar_pro = LLM(model="perplexity/sonar-pro") # Advanced Search - $3/$15
llm_perplexity_sonar.stop_words = []
llm_perplexity_sonar_pro.stop_words = []


lmm_perplexity_litellm_patch = LLM(
    provider="perplexity",
    model="perplexity/sonar",
    config={
        "stop": None,  # Explicitly set stop to None
        "litellm_params": {
            "api_base": "https://api.perplexity.ai",
            "custom_llm_provider": "perplexity",
            "force_timeout": 120,
            "drop_params": ["stop"],  # Tell LiteLLM to drop the stop parameter
            "temperature": 0.1
        }
    }
)


# Perplexity via OpenAI client approach
perplexity_api_key = os.environ.get("PERPLEXITY_API_KEY")

# Create a Perplexity LLM using OpenAI client
llm_perplexity_via_openai = LLM(
    provider="openai",  # Use OpenAI as provider
    model="perplexity/sonar",  # Perplexity model
    api_key=perplexity_api_key,  # Use Perplexity API key
    config={
        "api_base": "https://api.perplexity.ai",
        "extra_headers": {
            "x-api-type": "perplexity"  # Tell LiteLLM this is Perplexity
        }
    }
)


# Perplexity via custom PerplexityLLM
llm_perplexity_custom_patch = PerplexityLLM(
    model="perplexity/sonar",  # Or "perplexity/sonar-pro" for the pro version
    api_key=os.environ.get("PERPLEXITYAI_API_KEY")
)
