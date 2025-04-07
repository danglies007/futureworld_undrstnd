**CrewAI - PRD - Product Requirements Document: Tsunami's of Change - Scan Sources**

**Version:** 1.0
**Date:** 2025-04-05
**Target Framework:** CrewAI

**1. Introduction**

This document outlines the requirements for a CrewAI-based workflow designed to scan reputable sources, identify, analyze, and report on market forces, trends, and signals. The primary objective is to provide actionable intelligence for a growth consulting company - **Futureworld**, supporting trend analysis, strategic planning, and investment decision-making internally and for their clients. The system emphasizes user configurability, structured outputs (including Pydantic models for integration), and incorporates user review checkpoints.

**2. Goals**

* **Automate Market Scanning:** Efficiently scan diverse, reputable sources for predefined and user-defined keywords related to market dynamics.
* **Identify Key Forces:** Extract, synthesize, and identify significant market forces, trends, mega-trends, signals, and structural shifts.
* **Contextualize Findings:** Analyze findings within user-specified scope (Global, Market, Industry) and time horizon.
* **Provide Structured Outputs:** Deliver findings in Markdown (detailed table, structured report) and Pydantic object formats for easy consumption and downstream use.
* **User Configurability:** Allow users to define/modify keywords, sources, industry, market scope, time horizon, and upload custom source files.
* **User Interaction:** Implement checkpoints for user review and potential redirection of the research process (configuration validation, preliminary findings review).
* **Modularity & Reusability:** Design agents and tasks logically for maintainability and potential reuse (especially reporting).

**3. User Personas & Stories**

* **Persona:** Growth Consultant / Market Analyst
* **User Stories:**
  * "As a Market Analyst, I want to configure a scan for 'AI Mega Trends' impacting the 'Global' 'Healthcare' industry over '5+ years', using McKinsey, WEF, and Wired, to identify strategic opportunities."
  * "As a Consultant, I want to add 'Quantum Computing Signals' to keywords and specific journals to sources for a deep-dive project."
  * "As an Analyst, I want to upload a proprietary PDF report for the crew to analyze alongside public sources."
  * "As a Consultant, I want a structured table summarizing trends, descriptions, and sources for my client presentation."
  * "As an Analyst, I want the output data as Pydantic objects to feed into our internal tools."
  * "As a Consultant, I want to review the preliminary list of identified forces before the final report generation to ensure relevance."

**4. Functional Requirements (FRs)**

* **FR1: Input Configuration:**

  * Accept user inputs: `Target Market` (string, default "Global"), `Target Industry` (string, required), `Keywords` (list of strings, default provided), `Time Horizon` (string, default "5+ years"), `Sources` (structured object/dict, defaults provided), `Uploaded Files` (list of paths/handles).
  * Provide default lists for `Keywords` and `Sources` (grouped by type: Consulting, Gov/Non-Profit, News, Futurists).
  * Allow users to review and modify `Keywords` (add/remove).
  * Allow users to review and modify `Sources` (add/remove URLs/identifiers per type, add custom types).
  * Allow users to specify paths to local files (PDF, DOCX, TXT) to be treated as custom sources.
  * *CrewAI Note:* Initial inputs passed to the first task's context. Modifications handled via `human_input` task.
* **FR2: Source Scanning:**

  * Iterate through configured `Keywords`.
  * For each `Keyword`, search across configured `Sources` within the context of `Target Market` and `Target Industry`.
  * For each `Keyword`, search across other `Sources` you deem relevant, within the context of `Target Market` and `Target Industry`.
  * Utilize appropriate CrewAI Tools for diverse sources: Web Search (e.g., `SerperDevTool`), Website Scraping/Browsing (`WebsiteSearchTool`, `BrowserbaseTool`, `ScrapingTool`), PDF Text Extraction (Custom `PDFSearchTool`), File Reading (`FileReadTool`).
  * Construct intelligent search queries combining keywords, industry, market, and source focus.
  * *CrewAI Note:* Scanning tasks for different source types can potentially run in parallel (`async_execution=True`).
* **FR3: Information Extraction & Initial Processing:**

  * Extract relevant text snippets/sections from sources matching criteria.
  * Capture metadata: Source Name, URL (if applicable), Source Type, Publication Date (if available), Keyword(s) matched, Scope Context, Extracted Text.
  * *CrewAI Note:* This data forms the output of scanning tasks, likely as lists of intermediate objects (e.g., `SourceFinding`).
* **FR4: Synthesis and Analysis:**

  * Aggregate findings from all scanning tasks.
  * Deduplicate redundant information.
  * Group related findings to identify distinct market forces/trends/signals.
  * Synthesize a concise name and description for each identified item.
  * Associate relevant supporting evidence (source snippets, metadata).
  * Ensure you keep linkages and references to original source information when synthesizing
  * Correlate findings with the specified `Time Horizon`.
  * *CrewAI Note:* A core analysis task using LLM capabilities, potentially benefiting from agent memory.
* **FR5: Output Generation:**

  * Generate outputs in specified formats:
    * **Pydantic Objects:** List of `IdentifiedForce` objects nested within a main `MarketForceOutput` object.
    * **Markdown Detailed Table:** Summarizing each `IdentifiedForce` (Name, Description, Keywords, Scope, Time Horizon, Sources).
    * **Markdown Structured Report:** Narrative summary, key themes, context, referencing data. Suitable for conversion to slides.
  * *CrewAI Note:* Final task formats data received via `context` using LLM. Pydantic models define `expected_output`.
* **FR6: User Interaction Points:**

  * **Checkpoint 1 (Configuration Review):** Use a task with `human_input=True` after initial plan formulation to allow user review/modification of keywords and sources before scanning begins.
  * **Checkpoint 2 (Findings Review):** Use a task with `human_input=True` after synthesis to allow user review/feedback on the preliminary list of identified forces before final report generation.
  * *CrewAI Note:* Relies on the orchestrating application (CrewAI flows) to handle the pause/interaction triggered by `human_input=True`.

**5. Non-Functional Requirements (NFRs)**

* **NFR1: Source Reliability:** Prioritize predefined reputable sources. Handle unavailable sources gracefully (log error, skip, continue).
* **NFR2: Modularity:** Structure Agents and Tasks logically for maintainability and reuse.
* **NFR3: Scalability (Future):** Design should accommodate potential growth in sources/keywords. Leverage parallelism where feasible (`async_execution`).
* **NFR4: Cost/Rate Limits (Future):** Be mindful of API call costs (Search, LLM). Implement basic error handling for rate limits. Optimization is a later phase.
* **NFR5: Extensibility:** Architecture should facilitate adding new source types, tools, or analytical capabilities.
* **NFR6: CrewAI Best Practices:** Adhere to CrewAI standards whereever possible including for Agent/Task definition, Tool creation (`BaseTool`), context passing, and memory usage.
* **NFR7: Error Handling:** Implement basic error handling for tool failures (e.g., scraping errors, file not found).
* NFR8: Features:  Implement features and additional capabilities as standalone utiltiies (where possible) rather than integrating directly into the crewai code files (e.g main.py and crew.py) in order to keep the crewai code clean and usable

**6. CrewAI Structure Proposal**

* **Crew:** `MarketForcesResearchCrew`
* **Goal:** To research, analyze, and report on market forces, incorporating user configuration and review checkpoints.
* **Process:** `Process.sequential` (default, managed by task dependencies/context).
* **Memory:** `memory=True` recommended for the Crew or specifically for `DataSynthesizer` and `ReportWriter` agents.
* **Agents:**

  1. **ResearchManager:**
     * `role`: Market Intelligence Process Lead
     * `goal`: Oversee the research workflow, manage user interaction points, ensure task coordination and final quality.
     * `backstory`: An experienced project manager specializing in market intelligence workflows, focused on process rigor and stakeholder communication.
     * `tools`: []
     * `allow_delegation`: True
     * `verbose`: True
  2. **ConfigurationSpecialist:**
     * `role`: Research Setup Planner
     * `goal`: Process initial user inputs, validate parameters, load/manage default keywords and sources, and formulate the final research plan for user review.
     * `backstory`: A meticulous analyst skilled in defining clear parameters for complex research tasks. Ensures all inputs are validated and the plan is comprehensive.
     * `tools`: []
     * `allow_delegation`: False
     * `verbose`: True
  3. **WebSourceAnalyst:**
     * `role`: Digital Information Retriever
     * `goal`: Scan configured web-based sources (consulting firms, news sites, futurist blogs) using search engines and direct browsing/scraping based on the research plan.
     * `backstory`: An expert in online research methodologies, adept at using advanced search operators and navigating diverse web architectures to find relevant information efficiently.
     * `tools`: [SerperDevTool, WebsiteSearchTool/BrowserbaseTool/ScrapingTool] (Specific tool instances passed during crew setup)
     * `allow_delegation`: False
     * `verbose`: True
  4. **DocumentSourceAnalyst:**
     * `role`: Document Intelligence Extractor
     * `goal`: Process structured documents like PDFs from specified URLs or user-uploaded files, extracting relevant text based on the research plan.
     * `backstory`: An analyst experienced in parsing dense reports, academic papers, and official publications to extract key information and data points.
     * `tools`: [Custom `PDFSearchTool`, `FileReadTool`] (Specific tool instances passed during crew setup)
     * `allow_delegation`: False
     * `verbose`: True
  5. **DataSynthesizer:**
     * `role`: Market Insights Analyst
     * `goal`: Aggregate raw findings from all sources, clean, deduplicate, identify patterns, cluster information, and synthesize distinct market forces/trends with supporting evidence.
     * `backstory`: A data-savvy analyst skilled in information synthesis, pattern recognition from unstructured text, and structuring complex information into coherent insights.
     * `tools`: []
     * `allow_delegation`: False
     * `memory`: True
     * `verbose`: True
  6. **ReportWriter:**
     * `role`: Intelligence Report Crafter
     * `goal`: Take the synthesized and reviewed market forces data and generate the final outputs in the required formats: structured Pydantic objects, a detailed Markdown table, and a well-structured Markdown report.
     * `backstory`: A clear and concise technical writer specializing in transforming complex data into actionable market intelligence reports suitable for strategic decision-making.
     * `tools`: []
     * `allow_delegation`: False
     * `memory`: True
     * `verbose`: True
* **Tasks:**

  1. **Task 1: Prepare Research Plan:**
     * `description`: "Process the initial user inputs: `{initial_inputs}`. Load default keywords and sources. Combine with user inputs to formulate a draft research plan including target market, industry, keywords: `{keywords}`, time horizon: `{time_horizon}`, and sources: `{sources_config}`, considering uploaded files: `{uploaded_files}`."
     * `expected_output`: "A structured dictionary or JSON string representing the draft research plan, ready for user review. Include lists of keywords and sources to be used."
     * `agent`: `ConfigurationSpecialist`
  2. **Task 2: Review Research Plan:**
     * `description`: "Present the draft Research Plan from the previous task to the user. The plan includes: {plan_details}. Ask the user to review the keywords, sources, market, industry, and time horizon. Capture their confirmation or requested modifications."
     * `expected_output`: "The final, user-confirmed or modified Research Plan as a structured dictionary or JSON string."
     * `agent`: `ResearchManager`
     * `human_input`: True
     * `context`: [Task 1 output]
  3. **Task 3: Scan Web Sources:**
     * `description`: "Execute web scanning based on the confirmed Research Plan: {confirmed_plan}. Use the configured web search and scraping tools to find information related to the keywords for the specified industry and market across the defined web sources."
     * `expected_output`: "A list of 'SourceFinding' objects (or dictionaries) containing extracted text snippets, source names, URLs, type ('Web'), publication dates (if found), and matched keywords from web sources."
     * `agent`: `WebSourceAnalyst`
     * `tools`: [Web Search/Scrape Tools]
     * `context`: [Task 2 output]
     * `async_execution`: True
  4. **Task 4: Scan Document Sources:**
     * `description`: "Execute document scanning based on the confirmed Research Plan: {confirmed_plan}. Use the configured PDF and file reading tools to find information related to the keywords within the specified PDF URLs and uploaded files."
     * `expected_output`: "A list of 'SourceFinding' objects (or dictionaries) containing extracted text snippets, source names (or filenames), type ('Document' or 'Uploaded'), publication dates (if found), and matched keywords from document sources."
     * `agent`: `DocumentSourceAnalyst`
     * `tools`: [PDF/File Tools]
     * `context`: [Task 2 output]
     * `async_execution`: True
  5. **Task 5: Synthesize Findings:**
     * `description`: "Aggregate and analyze the raw findings from both web scanning ({web_findings}) and document scanning ({doc_findings}). Deduplicate entries, cluster similar points, identify distinct market forces/trends/signals. For each identified force, synthesize a name, description, list associated keywords, scope, time horizon relevance, and link the key supporting source snippets/references."
     * `expected_output`: "A structured list of preliminary 'IdentifiedForce' objects (or dictionaries) representing the synthesized market forces, including names, descriptions, and supporting source references, ready for user review."
     * `agent`: `DataSynthesizer`
     * `context`: [Task 3 output, Task 4 output]
  6. **Task 6: Review Preliminary Findings:**
     * `description`: "Present the Preliminary Findings ({synthesized_data}) to the user. Display the list of identified forces/trends with their descriptions. Ask the user to review for relevance, accuracy, and completeness. Capture feedback or approval."
     * `expected_output`: "The final list of 'IdentifiedForce' objects (or dictionaries), potentially refined based on user feedback, along with a confirmation signal."
     * `agent`: `ResearchManager`
     * `human_input`: True
     * `context`: [Task 5 output]
  7. **Task 7: Generate Outputs:**
     * `description`: "Based on the final, reviewed synthesized findings ({reviewed_data}), generate the required outputs. Create the final list of Pydantic `IdentifiedForce` objects. Format a detailed Markdown table summarizing each force. Compose a structured Markdown narrative report summarizing key themes and insights."
     * `expected_output`: "A final 'MarketForceOutput' Pydantic object containing the list of 'IdentifiedForce' objects, the Markdown table string, and the Markdown report string."
     * `agent`: `ReportWriter`
     * `context`: [Task 6 output]

**7. Data Models (Pydantic)**

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date

class SourceConfig(BaseModel):
    consulting_firms: List[str] = Field(default_factory=lambda: ["https://www.mckinsey.com", "https://www.bain.com", "https://www.bcg.com"])
    gov_non_profit: List[str] = Field(default_factory=lambda: ["https://www.weforum.org", "https://intelligence.weforum.org/", "https://www.imf.org", "https://www.consilium.europa.eu/en/"])
    news_sources: List[str] = Field(default_factory=lambda: ["https://www.economist.com", "https://www.wired.com", "https://www.technologyreview.com", "https://www.forbes.com", "https://www.newscientist.com", "https://www.bloomberg.com", "https://www.cbinsights.com"])
    futurists: List[str] = Field(default_factory=lambda: ["https://futuristspeaker.com/", "https://www.futuristgerd.com/", "https://burrus.com/", "https://www.diamandis.com/", "https://www.pearson.uk.com/", "https://www.matthewgriffin.info/", "https://www.kurzweilai.net/", "https://richardvanhooijdonk.com/en/"])
    custom: Dict[str, List[str]] = Field(default_factory=dict)

class MarketForceInput(BaseModel):
    target_market: str = "Global"
    target_industry: str
    keywords: List[str] = Field(default_factory=lambda: ["Forces", "Trends", "Mega trends", "Future of", "Signals", "Structural shifts"])
    time_horizon: str = "5+ years"
    sources_config: SourceConfig = Field(default_factory=SourceConfig)
    uploaded_files: List[str] = Field(default_factory=list) # List of file paths

class SourceReference(BaseModel):
    source_name: str
    source_type: str # e.g., Consulting, News, Gov, Futurist, Uploaded
    url: Optional[str] = None
    publication_date: Optional[str] = None # Keep as string for flexibility
    relevant_snippet: str

class IdentifiedForce(BaseModel):
    force_id: str # Consider generating a unique ID (e.g., UUID)
    force_name: str
    description: str
    associated_keywords: List[str]
    scope_tags: List[str] # e.g., [Global, Healthcare]
    time_horizon_relevance: str
    potential_impact: Optional[str] = None # LLM assessed? (e.g., High, Medium, Low)
    supporting_sources: List[SourceReference]

class MarketForceOutput(BaseModel):
    input_parameters: MarketForceInput # Echo input parameters for context
    identified_forces: List[IdentifiedForce]
    summary_report_markdown: str
    detailed_table_markdown: str

# Intermediate Model (Example - Output of scanning tasks)
class SourceFinding(BaseModel):
      source_name: str
      source_type: str # Web, Document, Uploaded
      url: Optional[str] = None
      publication_date: Optional[str] = None
      keyword_found: str
      scope_matched: str # e.g., "Global Healthcare"
      extracted_text: str
      # Raw context might be too large, focus on concise snippets
```

**8. Tools Required**

* **Search:** `SerperDevTool` (or equivalent integrated search API tool). Requires API key setup.
* **Web Browsing/Scraping:** `WebsiteSearchTool`, `BrowserbaseTool`, `ScrapingTool`. Evaluate best fit for target sites. May require custom `BaseTool` wrappers for complex sites or specific data extraction logic. Requires configuration (e.g., Browserbase API key).
* **File Handling:**
  * `FileReadTool`: For reading text from uploaded TXT, potentially DOCX (needs `python-docx`).
  * Custom `PDFSearchTool` (inheriting `BaseTool`):
    * Input: URL (optional, for direct PDF links) or File Path.
    * Functionality: Download PDF if URL provided. Use `PyMuPDF` (or similar robust library) to extract text content page by page or as a whole. Handle basic text extraction; OCR is out of scope initially.
    * Output: Extracted text content as a string.
* **LLM:** The core CrewAI LLM integration (e.g., OpenAI, Anthropic) configured for the Agents.

**9. Workflow Diagram (Conceptual)**

```mermaid
graph LR
    A[User Input via Orchestrator] --> T1(Task 1: Prepare Plan);
    T1 -- Plan --> T2(Task 2: Review Plan);
    T2 -- Requires Human Input --> UX1(External App: Show Plan to User);
    UX1 -- Confirmed/Modified Plan --> T2;
    T2 -- Confirmed Plan --> D{Delegate Scans};
    subgraph Parallel Scans [async_execution=True]
        direction LR
        D -- Plan --> T3(Task 3: Scan Web);
        D -- Plan --> T4(Task 4: Scan Docs);
    end
    T3 -- Web Findings --> T5(Task 5: Synthesize);
    T4 -- Doc Findings --> T5;
    T5 -- Preliminary Findings --> T6(Task 6: Review Findings);
    T6 -- Requires Human Input --> UX2(External App: Show Findings to User);
    UX2 -- Feedback/Approval --> T6;
    T6 -- Reviewed Data --> T7(Task 7: Generate Outputs);
    T7 -- Final Outputs --> Z[Final Outputs: MarketForceOutput (Pydantic), MD Table, MD Report];

    %% Link Tools
    T3 --> ToolsW[Web Tools: Search, Scrape];
    T4 --> ToolsD[Doc Tools: PDF, FileRead];

    %% External Orchestrator handles A, UX1, UX2, Z
```

**10. Future Considerations / Enhancements**

* **UI/UX:** Front-end for configuration, file upload, interaction, visualization.
* **Advanced Scraping:** Integrate Scrapy or robust scraping services.
* **Knowledge Graph:** Store forces/relationships in Neo4j or similar.
* **Trend Trajectory:** Analyze mentions/sentiment over time (requires historical data).
* **Impact/Probability Assessment:** Add dedicated agent/task for deeper analysis.
* **PowerPoint Export:** Convert Markdown report to basic PPTX structure.
* **Cost/Performance Optimization:** Caching, selective scanning, LLM call optimization.
* **Deployment:** Docker/Cloud function packaging, API key management.
* **CrewAI Router:** Use for dynamic task routing based on findings (e.g., trigger deep dive).
* **Reusable Reporting Crew:** Formalize Agent 6 / Task 7 into a separate crew.
* **OCR for PDFs:** Add capability to handle scanned PDFs.

**11. Open Questions**

* Refinement of criteria for "deduplication" and "clustering" in Task 5.
* Specific error handling logic for tool failures (retry? fallback?).
* Initial complexity level for PDF extraction (text-based only).

---
