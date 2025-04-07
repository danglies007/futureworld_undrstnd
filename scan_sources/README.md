# Scan Sources CrewAI Project

Welcome to the Scan Sources Crew project, powered by [crewAI](https://crewai.com). This project uses CrewAI to scan reputable sources, identify market forces, trends, and signals, analyze them, and generate structured reports based on user configuration, as outlined in the [PRD](Docs/CrewAI%20PRD%20-%20scan%20sources.md).

## Installation

Ensure you have Python >=3.10 <3.13 installed on your system. This project uses [UV](https://docs.astral.sh/uv/) for dependency management and package handling, offering a seamless setup and execution experience.

First, if you haven't already, install uv:

```bash
pip install uv
```

Next, navigate to your project directory and install the dependencies using uv:

```bash
# Ensure uv is installed (pip install uv)
uv sync
```

(Optional) If you prefer pip:
```bash
pip install -r requirements.txt
```

### Customizing

**Add required API keys to the `.env` file:**

```
SERPER_API_KEY=your_serper_api_key
# OPENAI_API_KEY=your_openai_api_key # Or other LLM provider keys
# BROWSERBASE_API_KEY=your_browserbase_key # If using BrowserbaseTool
# Add others as needed for specific tools
```

- Modify `src/scan_sources/config/agents.yaml` to customize agent roles, goals, backstories, or tools.
- Modify `src/scan_sources/config/tasks.yaml` to adjust task descriptions, expected outputs, or agent assignments.
- Modify `src/scan_sources/crew.py` to change crew logic, tool initialization, or agent/task setup.
- Modify `src/scan_sources/utilities/models.py` to adjust the Pydantic models for inputs or outputs.
- Modify `src/scan_sources/main.py` to change how inputs are gathered or results are presented.

## Running the Project

To kickstart your crew of AI agents and begin task execution, run this from the root folder (`scan_sources`):

```bash
python src/scan_sources/main.py
crewai run
```

This command initializes the Scan Sources Crew, gathers initial inputs (currently defaults in `main.py`), and starts the process defined in the PRD.

The crew will:
1.  Prepare a research plan based on inputs.
2.  Ask for user confirmation of the plan (via console input).
3.  Scan web and document sources.
4.  Synthesize findings.
5.  Ask for user confirmation of the findings (via console input).
6.  Generate final Pydantic objects and Markdown reports.
7.  Print the Pydantic object output to the console.

## Understanding Your Crew

The Scan Sources Crew is composed of multiple AI agents (defined in `config/agents.yaml`), each with unique roles, goals, and tools. These agents collaborate on a series of tasks (defined in `config/tasks.yaml`), leveraging their collective skills to achieve the goal of identifying and reporting on market forces, trends, and signals.

## Support

For support, questions, or feedback regarding the Scan Sources Crew or crewAI.

- Visit our [documentation](https://docs.crewai.com)
- Reach out to us through our [GitHub repository](https://github.com/joaomdmoura/crewai)
- [Join our Discord](https://discord.com/invite/X4JWnZnxPb)
- [Chat with our docs](https://chatg.pt/DWjSBZn)

Let's create wonders together with the power and simplicity of crewAI.
