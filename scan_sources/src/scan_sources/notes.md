# General Notes

## To Do

1. Check LLM temperature for scrape
2. Improve the agent outputs for the source identification to ensure the date is correct etc.

## Tools

- Brave - Seems to hallucinate, if just using it as standard
- Serperdev - working okay but gets stuck in a single souce
- EXA - Looks good,
  - finds diverse content
  - but makes up the source, allocating it to one of the Futurists -
  - Dates are all a problem
  - Seems to use nural search which might be the challege
  - Looking to add Exa crawl to improve content
- FireCrawl - still cant get to work
- ScrapFly - works nicely
  - Maybe need to go off serper as search
  - Need to find a nice combination
- Perplexity -
  - needed to apply some patches to get it to work
    - Hallucinating
    - Timing out do to patch
    - might try openrouter
  - WORKS through crew_perplexty.py patch but very slow
  - Works well throuhg openAI API
    - uses about 10-20USc per research query

## Outputs

- Good output was generated with context being accuratly passed between LLMs - lost 2 output files when I edited the task goal, will try get it back.
  - Config was:
    - Agent LLM
      - ```
        	@agent
        	def futurist_source_identifier(self) -> Agent:
        		return Agent(
        			config=self.agents_config['futurist_source_identifier'],
        			llm=llm_gpt4o_mini_accurate,
        			tools=[SerperDevTool()],
        			verbose=True
        		)

        	@agent
        	def futurist_content_extractor(self) -> Agent:
        		return Agent(
        			config=self.agents_config['futurist_content_extractor'],
        			llm=llm_gpt4o_mini_accurate,
        			tools=[ScrapeWebsiteTool(), FileDownloaderTool()],
        			verbose=True,
        			respect_context_window=True,
        			cache=True,
        			function_calling_llm=llm_gpt4o_mini
        		)

        	@agent
        	def futurist_reporting_analyst(self) -> Agent:
        		return Agent(
        			config=self.agents_config['futurist_reporting_analyst'],
        			llm=llm_gpt4o_mini,
        			tools=[scrapfly_scrape_tool],
        			verbose=True
        		)

        	@agent
        	def futurist_formatter(self) -> Agent:
        		return Agent(
        			config=self.agents_config['futurist_formatter'],
        			llm=llm_gpt4o_mini,
        			verbose=True
        		)

        	@agent
        	def futurist_market_force_extractor(self) -> Agent:
        		return Agent(
        			config=self.agents_config['futurist_market_force_extractor'],
        			llm=llm_gpt4o_mini,
        			verbose=True
        		)

        ```
