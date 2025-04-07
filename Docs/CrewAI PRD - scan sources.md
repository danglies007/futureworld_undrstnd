Okay, here is the complete, updated Product Requirements Document incorporating the 3-crew structure, external orchestration, Markdown summaries for review, updated data models, specific naming, and other refinements discussed.

---

**CrewAI - PRD - Product Requirements Document: Tsunami's of Change - Scan Sources**

**Version:** 1.1
**Date:** 2025-04-07 (Updated based on discussion)
**Target Framework:** CrewAI
**Project Context:** For internal use and client projects at **Futureworld** consulting.

**1. Introduction**

This document outlines the requirements for a modular, CrewAI-based workflow named "Tsunami's of Change - Scan Sources". Its primary objective is to automate the scanning of reputable sources, identification, analysis, and reporting of market forces, trends, and signals to provide actionable intelligence for Futureworld's growth consulting activities. The system utilizes a multi-crew architecture for clarity and reusability, emphasizes user configurability and interaction via review checkpoints, and produces structured outputs in both Pydantic (for system integration) and human-readable Markdown formats.

**2. Goals**

* **Automate Market Scanning:** Efficiently scan diverse, reputable sources for predefined and user-defined keywords related to market dynamics.
* **Identify Key Forces:** Extract, synthesize, and identify significant market forces, trends, mega-trends, signals, and structural shifts, maintaining clear linkage to source evidence.
* **Contextualize Findings:** Analyze findings within user-specified scope (Global, Market, Industry) and time horizon.
* **Provide Structured Outputs:** Deliver findings in easily digestible formats: detailed Markdown table, structured Markdown report, and Pydantic objects.
* **User Configurability:** Allow users to define/modify keywords, sources, industry, market scope, time horizon, and upload custom source files.
* **User Interaction:** Implement checkpoints with clear Markdown summaries for user review and approval/modification (configuration validation, optional preliminary findings review).
* **Modularity & Reusability:** Design agents and tasks logically across separate crews (Configuration, Research & Synthesis, Output Packaging) for maintainability and potential reuse.

**3. User Personas & Stories**

* **Persona:** Growth Consultant / Market Analyst (at Futureworld)
* **User Stories:**
  * "As a Market Analyst, I want to configure a scan for 'AI Mega Trends' impacting the 'Global' 'Healthcare' industry over '5+ years', using McKinsey, WEF, and Wired, to identify strategic opportunities."
  * "As a Consultant, I want to add 'Quantum Computing Signals' to keywords and specific journals to sources for a deep-dive project."
  * "As an Analyst, I want to upload a proprietary PDF report for the crew to analyze alongside public sources."
  * "As a Consultant, I want a structured table summarizing trends, descriptions, and sources for my client presentation."
  * "As an Analyst, I want the output data as Pydantic objects to feed into our internal knowledge management system."
  * "As a Consultant, I want to review the proposed research plan and the preliminary findings list in a readable format before the final report generation to ensure relevance."

**4. Functional Requirements (FRs)**

* **FR1: Input Configuration:** *(Responsibility: Crew 1)*

  * Accept user inputs: `Target Market`, `Target Industry`, `Keywords`, `Time Horizon`, `Sources`, `Uploaded Files`. Provide sensible defaults where applicable.
  * Allow users to review/modify default `Keywords` and `Sources` (grouped by type, supporting custom additions).
  * Allow users to specify local file paths (PDF, DOCX, TXT) as custom sources.
* **FR2: Source Scanning:** *(Responsibility: Crew 2)*

  * Iterate through configured `Keywords` from the `ValidatedResearchPlan`.
  * For each `Keyword`, search across configured `Sources` within the context of `Target Market` and `Target Industry`.
  * *(Optional Capability)* Allow agents (e.g., `WebSourceAnalyst`) to suggest/scan *additional highly relevant* sources discovered during the primary search, based on strong contextual clues (controlled by a flag/setting).
  * Utilize appropriate CrewAI Tools: Web Search (`SerperDevTool`), Web Scraping/Browsing (`WebsiteSearchTool`, `BrowserbaseTool`, `ScrapingTool`), PDF Text Extraction (Custom `PDFSearchTool`), File Reading (`FileReadTool`).
  * Construct intelligent search queries.
* **FR3: Information Extraction & Initial Processing:** *(Responsibility: Crew 2)*

  * Extract relevant text snippets/sections matching criteria.
  * Capture metadata: Source Name, URL, Source Type, Publication Date, Keyword(s) matched, Scope Context, Extracted Text. (Output: `List[SourceFinding]`).
* **FR4: Synthesis and Analysis:** *(Responsibility: Crew 2)*

  * Aggregate findings from all scanning tasks within Crew 2.
  * Deduplicate redundant information intelligently.
  * Group related findings to identify distinct market forces/trends/signals.
  * Synthesize a concise name and description for each identified item.
  * Ensure clear linkages and references (`SourceReference`) to original source information are maintained within the synthesized output (`IdentifiedForce`).
  * Correlate findings with the specified `Time Horizon`.
* **FR5: Output Generation:** *(Responsibility: Crew 3)*

  * Take the final `SynthesizedFindings` data from Crew 2.
  * Generate outputs in specified formats: Pydantic `PackagedOutputs` object, detailed Markdown table string, structured Markdown report string.
* **FR6: User Interaction Points:**

  * **Checkpoint 1 (Configuration Review):** *(Responsibility: Crew 1)* Use a task with `human_input=True`. Present a readable Markdown summary of the proposed plan for user review/modification before proceeding.
  * **Checkpoint 2 (Findings Review):** *(Responsibility: Crew 2 - Optional Task)* Use a task with `human_input=True`. Present a readable Markdown summary of the preliminary synthesized findings for user review/feedback before finalizing Crew 2's output.

**5. Non-Functional Requirements (NFRs)**

* **NFR1: Source Reliability:** Prioritize predefined reputable sources. Handle unavailable sources gracefully (log error, skip, continue).
* **NFR2: Modularity:** Utilize a multi-crew architecture (Config, Research & Synth, Packaging) for clear separation of concerns and maintainability.
* **NFR3: Scalability (Future):** Design should accommodate potential growth. Leverage parallelism (`async_execution`) for scanning tasks.
* **NFR4: Cost/Rate Limits (Future):** Be mindful of API costs. Implement basic error handling/logging for rate limits. Optimization is a later phase.
* **NFR5: Extensibility:** Architecture should facilitate adding new source types, tools, or analytical capabilities.
* **NFR6: CrewAI Best Practices:** Adhere to CrewAI standards for Agent/Task definition, Tool creation (`BaseTool`), context passing, memory usage.
* **NFR7: Error Handling:** Implement basic error handling for tool failures (e.g., scraping errors, file not found, synthesis issues). Return appropriate status in result objects.
* **NFR8: Feature Isolation:** Implement supporting features/utilities (e.g., complex PDF parsing logic, specific source handling) as standalone utilities/modules where possible, keeping core crew code clean.
* **NFR9: Inter-Crew Data Contracts:** Use clearly defined Pydantic models (`ValidatedResearchPlan`, `SynthesizedFindings`, result objects) for data passed between crews and between the orchestrator and crews.

**6. CrewAI Structure Proposal**

* **Overall Orchestration:** The sequence and conditional execution of crews (Crew 1 -> Crew 2 -> Crew 3) will be managed by the main Python script (`main.py` or equivalent orchestrator). This script initiates each crew's `kickoff`, inspects the returned status (e.g., from `ConfigurationResult`, `SynthesisResult`), and passes the required data payload to the next crew if conditions are met. Routing logic resides primarily in the orchestrator.
* **Crews Definition:**

  ---

  **Crew 1: Research Configuration Crew**


  * **Goal:** Interactively gather, validate, and finalize research parameters with user approval, presenting them clearly for review.
  * **Agents:**
    1. `ConfiguratorAgent`: (`role`: Research Setup Planner, `goal`: Process inputs, manage defaults, propose plan, generate plan summary, `backstory`: Meticulous analyst...).
    2. `UserInteractionAgent`: (`role`: User Liaison, `goal`: Present plan summary to user, capture feedback, manage approval flow, `backstory`: Clear communicator...).
  * **Tasks:**
    1. `Task 1.1: ProcessInitialInput` (Agent: `ConfiguratorAgent`).
    2. `Task 1.2: ProposeResearchPlan`
       * `description`: "Formulate the draft research plan based on inputs and defaults. Generate both the structured plan object AND a human-readable Markdown summary."
       * `expected_output`: "Object containing 'draft_plan' (Pydantic/dict) and 'plan_markdown_summary' (string)."
       * `agent`: `ConfiguratorAgent`.
    3. `Task 1.3: GetUserApproval`
       * `description`: "Present the Markdown summary (`plan_markdown_summary`) of the proposed research plan to the user. Ask for confirmation or specific modifications (e.g., add/remove keywords/sources)."
       * `human_input`: True
       * `context`: [Task 1.2 output (`plan_markdown_summary` needed)].
       * `expected_output`: "A `ConfigurationResult` object containing 'status' ('approved'/'rejected') and, if approved, the final 'validated_plan' (Pydantic)."
       * `agent`: `UserInteractionAgent`.
  * **Input:** Raw user request (`MarketForceInput` or simpler dict).
  * **Output:** `ConfigurationResult` (Pydantic Model).

  ---

  **Crew 2: Market Research & Synthesis Crew**

  * **Goal:** Execute the validated research plan, scan sources (including potentially relevant discoveries), extract information, synthesize findings with clear source linkage, generate a readable summary, and optionally allow user review of preliminary results.
  * **Agents:**
    1. `WebSourceAnalyst`: (Handles web search/scraping; *may optionally suggest additional sources*).
    2. `DocumentSourceAnalyst`: (Handles PDF/document processing).
    3. `DataSynthesizer`: (Aggregates, deduplicates, synthesizes findings, ensures source linkage, generates summary).
    4. *(Optional)* `ReviewCoordinatorAgent`: (Manages optional user review step).
  * **Tasks:**
    1. `Task 2.1: ScanWebSources` (`async_execution`: True) - Context: `ValidatedResearchPlan`. Output: `List[SourceFinding]`. Agent: `WebSourceAnalyst`.
    2. `Task 2.2: ScanDocumentSources` (`async_execution`: True) - Context: `ValidatedResearchPlan`. Output: `List[SourceFinding]`. Agent: `DocumentSourceAnalyst`.
    3. `Task 2.3: SynthesizeFindings`
       * `description`: "Aggregate and analyze raw findings from web and document scans. Deduplicate, cluster, identify distinct forces. For each, synthesize name, description, scope, time horizon, and link supporting `SourceReference`s. Generate both the structured list (`List[IdentifiedForce]`) AND a human-readable Markdown summary (e.g., bullet points/table) of these preliminary synthesized forces."
       * `expected_output`: "Object containing 'preliminary_synthesized_findings' (`List[IdentifiedForce]`) and 'preliminary_findings_markdown' (string)."
       * `agent`: `DataSynthesizer`.
       * `context`: [Task 2.1 output, Task 2.2 output].
    4. *(Optional)* `Task 2.4: ReviewPreliminaryFindings`
       * `description`: "Present the preliminary findings Markdown summary (`preliminary_findings_markdown`) to the user for review of relevance, accuracy, and completeness. Capture feedback or approval."
       * `human_input`: True
       * `context`: [Task 2.3 output (`preliminary_findings_markdown` needed)].
       * `expected_output`: "A result object indicating status ('approved'/'rejected_by_review') and the final `List[IdentifiedForce]` (potentially refined based on feedback)."
       * `agent`: `ReviewCoordinatorAgent`.
  * **Input:** `ValidatedResearchPlan` (from Crew 1's output).
  * **Output:** `SynthesisResult` (Pydantic Model).

  ---

  **Crew 3: Output Packaging Crew**

  * **Goal:** To take the final, approved synthesized research findings and format them into polished, publishable Markdown table and report outputs.
  * **Agents:**
    1. `MarkdownReportFormatter`: (`role`: Narrative Report Specialist).
    2. `MarkdownTableFormatter`: (`role`: Data Table Specialist).
    3. *(Optional)* `OutputCoordinator`: (`role`: Packaging Manager).
  * **Tasks:**
    1. `Task 3.1: GenerateMarkdownReport`
       * `description`: "Compose a structured Markdown narrative report summarizing key themes, insights, and providing context based on the final synthesized findings ({findings}). Ensure clear structure suitable for conversion to slides."
       * `expected_output`: "A string containing the formatted Markdown report."
       * `agent`: `MarkdownReportFormatter`.
       * `context`: [`SynthesizedFindings` payload].
    2. `Task 3.2: GenerateMarkdownTable`
       * `description`: "Format a detailed Markdown table summarizing each identified force from the final synthesized findings ({findings}), including Name, Description, Keywords, Scope, Time Horizon, and key Supporting Sources/Snippets."
       * `expected_output`: "A string containing the formatted Markdown table."
       * `agent`: `MarkdownTableFormatter`.
       * `context`: [`SynthesizedFindings` payload].
    3. `Task 3.3: PackageOutputs`
       * `description`: "Consolidate the generated Markdown report and table strings, along with the source synthesized findings data, into the final output object."
       * `expected_output`: "The final `PackagedOutputs` Pydantic object."
       * `agent`: `OutputCoordinator` (or one of the formatters).
       * `context`: [Task 3.1 output, Task 3.2 output, `SynthesizedFindings` payload].
  * **Input:** `SynthesizedFindings` payload (extracted from Crew 2's output).
  * **Output:** `PackagedOutputs` (Pydantic Model).

  ---

**7. Data Models (Pydantic)**

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import date

# --- Core Data Structures ---

class SourceConfig(BaseModel):
    consulting_firms: List[str] = Field(default_factory=lambda: ["https://www.mckinsey.com", "https://www.bain.com", "https://www.bcg.com"])
    gov_non_profit: List[str] = Field(default_factory=lambda: ["https://www.weforum.org", "https://intelligence.weforum.org/", "https://www.imf.org", "https://www.consilium.europa.eu/en/"])
    news_sources: List[str] = Field(default_factory=lambda: ["https://www.economist.com", "https://www.wired.com", "https://www.technologyreview.com", "https://www.forbes.com", "https://www.newscientist.com", "https://www.bloomberg.com", "https://www.cbinsights.com"])
    futurists: List[str] = Field(default_factory=lambda: ["https://futuristspeaker.com/", "https://www.futuristgerd.com/", "https://burrus.com/", "https://www.diamandis.com/", "https://www.pearson.uk.com/", "https://www.matthewgriffin.info/", "https://www.kurzweilai.net/", "https://richardvanhooijdonk.com/en/"])
    custom: Dict[str, List[str]] = Field(default_factory=dict)

class MarketForceInput(BaseModel):
    # Initial inputs from user to start Crew 1
    target_market: str = "Global"
    target_industry: str
    keywords: Optional[List[str]] = None # User can provide list or use default
    time_horizon: Optional[str] = None # User can provide or use default
    sources_config: Optional[SourceConfig] = None # User can provide or use default
    uploaded_files: List[str] = Field(default_factory=list) # List of file paths

class ValidatedResearchPlan(BaseModel):
    # Output of Crew 1 (if approved), Input to Crew 2
    target_market: str
    target_industry: str
    keywords: List[str]
    time_horizon: str
    sources_config: SourceConfig
    uploaded_files: List[str]
    # Optional: Add flag for dynamic source discovery?
    # allow_dynamic_source_discovery: bool = False

class SourceReference(BaseModel):
    # Used within IdentifiedForce to link back to evidence
    source_name: str
    source_type: str # e.g., Consulting, News, Gov, Futurist, Uploaded, Discovered
    url: Optional[str] = None
    publication_date: Optional[str] = None
    relevant_snippet: str # Key piece of text supporting the force

class IdentifiedForce(BaseModel):
    # Core unit of synthesized finding
    force_id: str # Unique identifier (e.g., UUID generated during synthesis)
    force_name: str # Concise name of the trend/force
    description: str # Synthesized description
    associated_keywords: List[str] # Keywords leading to this finding
    scope_tags: List[str] # e.g., [Global, Healthcare]
    time_horizon_relevance: str # e.g., "5+ years", "Near-term"
    potential_impact: Optional[str] = None # LLM assessed? (e.g., High, Medium, Low)
    supporting_sources: List[SourceReference] # Evidence linkage

class SynthesizedFindings(BaseModel):
    # Payload output of Crew 2 (if approved), Input to Crew 3
    validated_plan_used: ValidatedResearchPlan # Traceability
    identified_forces: List[IdentifiedForce] # The core synthesized data
    # Optional summary stats for context
    # num_sources_scanned: Optional[int] = None
    # num_raw_findings: Optional[int] = None

# --- Intermediate Data Structures ---

class SourceFinding(BaseModel):
    # Output of scanning tasks (Task 2.1, 2.2)
    source_name: str
    source_type: str # Web, Document, Uploaded
    url: Optional[str] = None
    publication_date: Optional[str] = None
    keyword_found: str
    scope_matched: str # e.g., "Global Healthcare"
    extracted_text: str # Raw snippet found

# --- Crew Result Wrappers ---

class ConfigurationResult(BaseModel):
    # Output wrapper for Crew 1
    status: str # 'approved', 'rejected', 'error'
    validated_plan: Optional[ValidatedResearchPlan] = None # Populated if status is 'approved'
    plan_summary_markdown: Optional[str] = None # The summary shown to user (for logging)
    message: Optional[str] = None # Error message or rejection reason

class SynthesisResult(BaseModel):
    # Output wrapper for Crew 2
    status: str # 'approved', 'rejected_by_review', 'error'
    findings_payload: Optional[SynthesizedFindings] = None # Pydantic payload if status is 'approved'
    preliminary_summary_markdown: Optional[str] = None # MD shown during optional review (for logging)
    message: Optional[str] = None

class PackagedOutputs(BaseModel):
    # Final output wrapper for Crew 3 (and the overall process)
    source_findings_summary: SynthesizedFindings # The core synthesized data used for reporting
    summary_report_markdown: str # The generated narrative report
    detailed_table_markdown: str # The generated summary table
    status: str = 'completed' # Final status
```

**8. Tools Required**

* **Crew 1:** Primarily relies on LLM capabilities for processing input and generating summaries. No external tools needed.
* **Crew 2:**
  * `SerperDevTool` (or equivalent Search API tool). Requires API key.
  * `WebsiteSearchTool`, `BrowserbaseTool`, `ScrapingTool` (evaluate best fit; may need custom `BaseTool`). Requires configuration/keys.
  * `FileReadTool` (for TXT, DOCX - needs `python-docx`).
  * Custom `PDFSearchTool` (inheriting `BaseTool`): Needs robust text extraction (e.g., `PyMuPDF`), optional URL download.
  * Core LLM integration for synthesis agent.
* **Crew 3:** Primarily relies on LLM capabilities for formatting Markdown. No external tools needed.

**9. Workflow Diagram (Conceptual)**

```mermaid
graph LR
    Orchestrator(main.py / Orchestrator);

    subgraph Orchestrator Logic
        A[User Input: MarketForceInput] --> Init1(Initiate Crew 1);
        Result1(Crew 1 Result: ConfigurationResult) --> Check1{Check Status == 'approved'?};
        Check1 -- Yes --> Prep2(Extract ValidatedPlan);
        Prep2 --> Init2(Initiate Crew 2);
        Check1 -- No --> Reject1(Handle Config Reject/Error);

        Result2(Crew 2 Result: SynthesisResult) --> Check2{Check Status == 'approved'?};
        Check2 -- Yes --> Prep3(Extract SynthesizedFindings Payload);
        Prep3 --> Init3(Initiate Crew 3);
        Check2 -- No --> Reject2(Handle Synthesis Reject/Error);

        Result3(Crew 3 Result: PackagedOutputs) --> Final(Present Final Outputs);

    end

    subgraph Crews Execution
        C1[Crew 1: Config];
        C2[Crew 2: Research & Synth];
        C3[Crew 3: Packaging];
    end

    Init1 -- MarketForceInput --> C1;
    C1 -- Task 1.2 generates MD Plan --> C1;
    C1 -- Task 1.3 uses MD Plan --> C1;
    C1 --> Result1;

    Init2 -- ValidatedPlan --> C2;
    C2 -- Task 2.3 generates MD Findings --> C2;
    C2 -- Optional Task 2.4 uses MD Findings --> C2;
    C2 --> Result2;

     Init3 -- SynthesizedFindings Payload --> C3;
     C3 -- Tasks generate final MD Table/Report --> C3;
     C3 --> Result3;


    %% User Interactions Triggered by Crews using generated Markdown
    C1 -- Task 1.3 presents MD --> UX1(External App: Show MD Plan);
    UX1 -- Feedback --> C1; %% Crew 1 waits for human_input task

    C2 -- Optional Task 2.4 presents MD --> UX2(External App: Show MD Findings);
    UX2 -- Feedback --> C2; %% Crew 2 waits for human_input task

```

**10. Future Considerations / Enhancements**

* **UI/UX:** Develop a front-end for configuration, file upload, interaction, and visualization.
* **Advanced Scraping:** Integrate Scrapy or robust scraping services for complex sites.
* **Knowledge Graph:** Store `IdentifiedForce` entities and relationships (e.g., Neo4j).
* **Trend Trajectory/Sentiment:** Analyze mentions over time (requires historical data/repeated runs).
* **Impact/Probability Assessment:** Add dedicated agent/task/crew for deeper analysis.
* **PowerPoint Export:** Convert Markdown report to basic PPTX structure (potentially Crew 4).
* **Cost/Performance Optimization:** Caching (especially for web requests/raw findings), selective scanning, LLM call optimization.
* **Deployment:** Docker/Cloud function packaging, API key management, scaling considerations.
* **CrewAI Router (Internal):** Explore if internal task routing within a crew simplifies any logic (less likely needed with external orchestration).
* **Reusable Reporting Crew:** Formally package Crew 3 for use in other Futureworld projects.
* **OCR for PDFs:** Add capability to handle image-based/scanned PDFs.
* **Dynamic Source Discovery Refinement:** Improve logic for suggesting/vetting additional sources in Crew 2.

**11. Open Questions**

* Refinement of criteria/prompting for "deduplication" and "clustering" in Task 2.3 (DataSynthesizer).
* Specific error handling logic/retry mechanisms for tool failures (e.g., temporary website unavailability).
* Initial complexity level for PDF extraction (text-based only confirmed).
* How should feedback from Task 2.4 (Findings Review) be incorporated? (e.g., re-run synthesis, flag items, simple pass/fail?). Define the interaction model.
* Implementation details for the optional dynamic source discovery (how are sources vetted?).

---
