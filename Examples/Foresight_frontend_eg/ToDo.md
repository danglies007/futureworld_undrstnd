## CrewAI

### Plan

- ~~Make sure that the foresight loks beyond 2025~~

### Interface and cosmetics

- Change the unknown in the temp output files - still a big challenge
- check wether the tools are hardcoded ?
- ensure the start time is correct time zone (process_info.json)
- Number and naming not working properly, not being imported into the research crewcan you check this section in the @crewai/src/foresight/crews/research_crew  - I think its importing the section info for naming etc, but does not seem to be getting applied correctly (as per the attached diagram), it is also very complex, is there not a simpler method, also consider the pydantic models that crewai typically uses ?

  This is an example of a current filename that is being saved
  2.0_analysis_unknown_20250331_143457.md

  This is what I would like
  2.2_analysis_Introduction:_Navigating_the_Future_of_Mining_20250331_143716

  <task_number>.<section_number>_<type_of_work>_`<subtitle>`_`<timestamp>`

  <task_number> and <type_of_work> are hard coded, the other information should come from the pydantic model developed in the plan_crew.py and datetime

### Process and Logging

* CrewAI log is not being correctly updated, when resuming

### Crew Setup

- maybe add an agent and task to take all of the outputs and consolidate it into a single documnent that flows better
- ~~split the plan from the research so the user can provide some input~~
- Try different LLM configurations
- Maybe make a publisher crew to take final outputs

### Content

* test whether the specified sources wre used

Changed to a new main file
