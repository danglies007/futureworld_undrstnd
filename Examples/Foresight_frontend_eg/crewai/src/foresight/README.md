# Foresight

A CrewAI-based system for generating foresight reports on market trends and future dynamics for different sectors.

## Structure

- `crews/`: Contains the agent crews that collaborate to produce the reports
  - `plan_crew/`: Creates a structured plan for the report
  - `research_crew/`: Executes detailed research and content creation for each section
- `tools/`: Custom tools for web search, scraping, and file management
- `outputs/`: Generated content and reports
- `reference/`: Reference materials and resources

## Running the Flow

To execute the foresight generation flow:

```python
from foresight.main import kickoff

# Run the flow
kickoff()
```

To visualize the flow structure:

```python
from foresight.main import plot

# Generate a visualization of the flow
plot()
```

## Configuration

Edit the `config.py` file to change the sector focus and other report parameters.
