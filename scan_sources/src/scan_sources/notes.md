# General Notes

## General Optimisation

1. Always do search with a smarter model - not a mini model e.g. 4_1

## Planning states

1. Sources
   1. have a proposed sources
   2. Have an approved sources
   3. have an additional source
2. Flow
   1. Flow starts
      1. Loads an overview of the key inputs (Topic, Preferred Sources, start time, date)
      2. Stores this in a Flow overview state
   2. Then goes to the Scan sources
      1. If there is a file that starts with "proposed_sources" in the flow_status folder:

         1. Ask the user to review this file
         2. The user can review and save the file with a filename start of "approved_sources" in flow_status folder, here the user will indicate that an approved_sources file has been saved, or
         3. The user can accept the file as is
      2. Once the user has reviewed:

         1. If the user accepts the file, Save the file

         * 1. with a filename start of "approved_sources" in flow_status folder.
           2. Set the sources_result state to sources_result - this is essentially a user approved list of sources to review
         * If there is a file that starts with "additional_sources" in the flow_status folder, then
           1. Take the additional_sources and set them as sources_result so they can be passed onto the market_force extraction.
           2. During this step we must make sure that the existing market_forces file is added as context to the crew and the new additional_sources are appended to the initial file, this iwll ensure the additional sources market forces do not overide the existing forces
      3. 

## Points for discussion

1. Good progress, refining how oututs are developed and the content of the report
2. Moved from a crew to a flow to ensure consistancy of outputs and manage context length issues
   1. Need to work on quality of inputs
   2. Detail in pydantic models
   3. Refining tasks - consider additional splitting tasks to get more refinement
   4. Optimising LLM usage
   5. Enalbe direct inout of a report to be generated in order to refine final outputs
3. Some challenges getting to this point (futurist content quality, PDF extraction) - often quite simple fixes
4. Key next steps
   1. Plan to get an integrated view of all market forces across sources for Steercom (e.g. Global Market Forces across futurists, consulting firms, news sources etc...)
   2. Enhance the Extraction crew with mutiple tasks essentially splitting url and pdf search and extraction
   3. Enhance the Report generating crew to effectivly interprete and package content from market force extraction
   4. Consider an intermediary crew between extraction and reporting to consolidate research prior to reporting
   5. Potentially develop some alternative output formats

## To Do

### Priority 1

#### Optimise (current features)

2. [ ] Make sure that relevant content is passed from one task to the next and then into the final report  - e.g. number of sources used etc.
3. [ ] Improve the agent outputs for the source identification to ensure the date is correct etc.
4. [ ] Conside adding a quality / relevance score to the sources
5. [X] Improve url search
6. [X] Fix agents and tasks
7. [X] Cleanup code base
8. [ ] Optimise LLMs and defnitions
9. [X] Refine report format*sorted this out a bit into a market forces report, need to integrate this with other sources*
1. [ ] Refine pydantic models
1. [X] Update source url models
1. [X] Parameterize inputs
1. [ ] Parameterise LLMs
1. [X] Consider the Market force definitions from Futureworld*captured some context here and have tried to incorporate it into the reports*
1. [ ] Optimise token usage with system prompts and other usefule tools and techniques

     1. [ ] See claude suggestions re:pydantic model optionsisation and optional text
1. [X] Sort out names of agents and tasks in the .yaml files remove futurist references and make them more generic
1. [ ] Linked in posts are causing issues with comments - exclude for now
1. [ ] Try Reader view to read popup blocked sites
1. [ ] Create a table or excel file as an alternative / additional output of the final report

#### Quality

* [ ] Check and develop logs and tracking
* [ ] Improve quality of source links sometimes landing pages are provided not the detailed content - e.g. https://www.fanaticalfuturist.com/2025/03/ambition-power-opportunity-mbp-partners-uk-matthew-griffin-motivational-keynote-speaker/
* [X] Dates still not working 100%
  * [ ] *Dates fixed for most source types*
* [X] Check how the PDF search tool works
* [X] **Improve PDF market force extraction**
  * [X] Consider creating a deidicated Marekt_force extraction tool or using another tool better suited to searching PDFs
* [ ] Convert interim files for audit
* [ ] Sort out custom scrape tool llm defaults
* [ ] Check LLM temperature for scrape
* [ ] Some challenges with Futurists as thier content is a bit patchy and click-bait like

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
