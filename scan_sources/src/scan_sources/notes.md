# General Notes

## To Do

### Priority 1

#### Optimise (current features)

1. [ ] Improve the agent outputs for the source identification to ensure the date is correct etc.
2. [ ] Improve url search
3. [ ] Fix agents and tasks
4. [X] Cleanup code base
5. [ ] Optimise LLMs and defnitions
6. [X] Refine report format*sorted this out a bit into a market forces report, need to integrate this with other sources*
7. [ ] Refine pydantic models
8. [X] Update source url models
9. [ ] Parameterize inputs
1. [ ] Parameterise LLMs
1. [X] Consider the Market force definitions from Futureworld*captured some context here and have tried to incorporate it into the reports*
1. [ ] Optimise token usage with system prompts and other usefule tools and techniques
     1. [ ] See claude suggestions re:pydantic model optionsisation and optional text
1. [ ] Sort out names of agents and tasks in the .yaml files remove futurist references and make them more generic
1. [ ] Linked in posts are causing issues with comments - eclude for now

#### Quality

* [ ] Check and develop logs and tracking
* [ ] Improve quality of source links sometimes landing pages are provided not the detailed content - e.g. https://www.fanaticalfuturist.com/2025/03/ambition-power-opportunity-mbp-partners-uk-matthew-griffin-motivational-keynote-speaker/
* [ ] Dates still not working 100%
* [ ] Check how the PDF search tool works
* [ ] **Improve PDF market force extraction**
  * [ ] Consider creating a deidicated Marekt_force extraction tool or using another tool better suited to searching PDFs
* [ ] Convert interim files for audit
* [ ] Sort out custom scrape tool llm defaults
* [ ] Check LLM temperature for scrape

#### Improve (new features)

1. [ ] Look at what crew and agent definitions from crewai can be used
2. [ ] Enable continuation of flow if files already exist
3. [ ] check or Enable Youtube extraction

### Priority 2

1. [ ] Improve crew naming
2. [ ] Tools improvement and additions
3. [ ] Think about scaling
4. [ ] See if states can be used better
5. [ ] Think about the endpoint and deployment
6. [ ] Improve or understand virtual environment usage

---

Questions

* How dynamic should we make the market forces, should it be an overall repository that is updated once a year or periodically ?

---

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
