import litellm
# from agentops.llm_wrapper import LLM
from crewai import LLM

# Define LLMs with token tracking
# Reasoning
llm_gpto3_mini = LLM(model="o3-mini-2025-01-31") # Fast flexible reasoning $1.10/4.40
llm_gpto1_mini = LLM(model="o1-mini-2024-09-12") # Faster more affordable reasoning than o1 $1.10/4.40
llm_gemini_2_5_pro = LLM(model="gemini/gemini-2.5-pro-exp-03-25", max_rpm=5) # Fast reasoning $0.1/$0.4

# Chat
llm_gpt4o_mini = LLM(model="gpt-4o-mini-2024-07-18") # Fast and cheap $0.15/$0.60
llm_claude_3_5_hauku = LLM(model="claude-3-5-hauku-latest") # Fast and cheap $.80/$4
llm_gpt4o = LLM(model="gpt-4o-2024-11-20") # Fast intelligent $2.50/$10
llm_claude_3_7_sonnet = LLM(model="claude-3-7-sonnet-latest")# Fast intelligent $3/$15 - May need rate limiting via litellm.rate_limit_config
llm_claude_3_5_sonnet = LLM(model="claude-3-5-sonnet-latest") # Fast intelligent $3/$15
llm_gemini_2_0_flash = LLM(model="gemini/gemini-2.0-flash") # Fast intelligent $0.1/$0.4
llm_gemini_2_0_flash_lite = LLM(model="gemini/gemini-2.0-flash-lite") # Fast intelligent $.075/$0.30

# Customised
llm_accurate = LLM(model="gpt-4o-2024-11-20", temperature=0.1, max_completion_tokens=8000, max_tokens=8000)
