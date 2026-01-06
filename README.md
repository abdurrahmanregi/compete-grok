# CompeteGrok

CompeteGrok is an AI-powered system for Industrial Organization (IO) economics and competition law analysis. It uses a multi-agent architecture orchestrated by LangGraph to provide comprehensive, evidence-based insights on complex economic and legal queries.

## Project Overview

CompeteGrok is designed to assist in antitrust and competition economics analysis by leveraging specialized AI agents. It adheres to governing principles including jurisdictional specificity (defaulting to US FTC/DOJ and EU Competition guidelines), declaration of legal standards (e.g., Consumer Welfare Standard), distinction between positive and normative statements, evidence hierarchy (binding case law, peer-reviewed studies, etc.), structured outputs, and hypothesis-driven reasoning. For detailed agent definitions and prompts, refer to AGENTS.md.

## Key Features

- **Multi-Agent Orchestration**: Specialized agents for research, quantitative analysis, explanations, market definitions, document analysis, case law, and debates.
- **Dynamic Agent Composition**: Tailored teams assembled based on query requirements for optimal efficiency.
- **Debate Subgraph**: Balanced pro/con debates with arbiter synthesis for controversial topics.
- **Error Handling & Resilience**: Retry logic, remediation agents, and graceful failure recovery.
- **LaTeX Math Support**: Inline `\(...\)` and display `\[...\]` rendering in outputs.
- **Privacy-First**: Ephemeral processing with no data retention.
- **Extensibility**: MCP tools for search, code execution, PDF processing, and filesystem access.
- **Verification Workflow**: Mandatory fact-checking of all citations by a dedicated Verifier agent.

## Architecture Overview

CompeteGrok leverages LangGraph for workflow orchestration:

- **Managing Partner Agent**: Central orchestrator for query classification, routing, state management, and synthesis.
- **Specialized Agents**: Domain-specific agents (e.g., Economic Research Associate, Quantitative Analyst) performing targeted tasks.
- **Tools Integration**: MCP tools for external capabilities like Tavily search, Linkup deep web searches, code execution (Python/R), PDF conversion, and `fetch_paper_content` for robust academic paper retrieval.
- **State Management**: TypedDict-based tracking of iterations, routing history, sources, and errors to prevent loops.

Workflow: Query → Classification → Agent Routing → Execution → Verification → Debate (if needed) → Synthesis → Report Generation.

## Agent Workflows

Agents follow hypothesis-driven workflows tailored to their roles:
- **Economic Research**: Search and synthesize papers using tools like `tavily_search`, `linkup_search`, and `fetch_paper_content`.
- **Quantitative Analysis**: Perform calculations (e.g., HHI, GUPPI) with `run_code_py`/`r`.
- **Explanation**: Break down models with caveats and LaTeX derivations.
- **Market Definition**: Apply SSNIP tests under jurisdictional guidelines.
- **Document Analysis**: Process uploads via PDF conversion and reading tools.
- **Case Law**: Search and verify precedents.
- **Debate**: Pro/con arguments with arbiter synthesis.
- **Verification**: The **Verifier Agent** checks every citation against external sources (Tavily/Linkup) to ensure accuracy. This is a mandatory step before synthesis.
- **Synthesis**: Integrate results into final reports.
For detailed prompts and routing triggers, see AGENTS.md.

## Installation and Setup

### Prerequisites
- Python 3.8+
- Pandoc (for PDF generation): [Install here](https://pandoc.org/installing.html)
- XeLaTeX (for LaTeX rendering): Included with TeX Live or MiKTeX

### Dependencies
```bash
pip install -r requirements.txt
```

### API Keys and Configuration
1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your API keys:
   - `XAI_API_KEY`: xAI Grok API key
   - `TAVILY_API_KEY`: Tavily search API key
   - `MISTRAL_API_KEY`: Mistral API key for PDF processing
   - `LINKUP_API_KEY`: Linkup API key for deep web searches
   - `LANGCHAIN_API_KEY`: LangSmith API key (optional, for tracing)

3. Ensure external MCP tools are accessible (paths configured in `config.py`; adjust for your OS).

### Configuration
The system behavior can be fine-tuned in `config.py`:

- **STRICT_MODE**: When set to `True` (default), tools will raise exceptions on failure rather than returning mock data. This ensures that the system only relies on actual, successful tool executions.
- **Logging**: Configurable log levels (DEBUG/INFO) and file paths in `compete_logging.py`.

### Verification
Run the help command:
```bash
python app.py --help
```

## Usage

### Basic Usage
```bash
python app.py --query "Calculate HHI for a market with firms of sizes 30%, 25%, 20%, 15%, 10%"
```

### Advanced Options
- `--query`: Query text or path to .txt file (supports multi-line queries and embedded file references).
- `--file`: PDF/Excel uploads for analysis (multiple files allowed).
- `--verbose`: Detailed logging.
- `--output-dir`: Output directory (default: `./outputs`).
- `--debate`: Forces debate module.

### Examples
1. Simple query:
   ```bash
   python app.py --query "Explain the Lerner Index"
   ```

2. File-based query:
   ```bash
   python app.py --query inputs/query_01.txt --verbose --output-dir ./reports
   ```

3. Document analysis with debate:
   ```bash
   python app.py --query "Analyze this merger" --file merger_doc.pdf --debate
   ```

4. Multi-file upload:
   ```bash
   python app.py --query "Compare these cases" --file case1.pdf case2.pdf
   ```

5. Query file with embedded files:
   ```
   QUERY:
   """
   Analyze the merger in these documents
   """
   FILES:
   """
   merger_doc.pdf
   financial_data.xlsx
   """
   ```
   ```bash
   python app.py --query query_with_files.txt
   ```

## Agents Overview

- **Managing Partner**: Orchestrates queries, routes agents, manages state.
- **Economic Research Associate**: Searches and synthesizes academic papers.
- **Quantitative Analyst**: Performs calculations (HHI, UPP, GUPPI) and simulations.
- **Educational Specialist**: Explains models with caveats and derivations.
- **Market Definition Expert**: Defines markets using SSNIP tests.
- **Document Analyst**: Analyzes uploaded documents.
- **Legal Precedent Specialist**: Searches case law and precedents.
- **Debate Facilitators**: Pro/Con advocates and Arbiter for balanced debates.
- **Synthesis Specialist**: Integrates outputs into final reports.
- **Verifier**: Fact-checks citations.
- **Remediation**: Handles errors and recovery.

For detailed prompts and routing, see `AGENTS.md`.

## Contribution Guidelines

We welcome contributions to CompeteGrok! To contribute:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/YourFeature`).
3. Commit your changes (`git commit -m 'Add YourFeature'`).
4. Push to the branch (`git push origin feature/YourFeature`).
5. Open a Pull Request.

Please ensure your code follows Python best practices, includes docstrings, and passes tests. For major changes, open an issue first to discuss. See AGENTS.md for agent-specific guidelines.

## Governing Principles

- **Jurisdictional Specificity**: Considers relevant jurisdictions (e.g., US FTC/DOJ, EU Competition) and guidelines.
- **Evidence Hierarchy**: Prioritizes binding case law, peer-reviewed empirics, agency guidelines, persuasive case law, reputable reports.
- **Hypothesis-Driven Reasoning**: Formulates and tests hypotheses sequentially.
- **Truth-Seeking**: Bases responses on verified facts; avoids hallucinations.

## Output Structure

- **Markdown Report**: Includes query, routes, synthesis, references.
- **PDF Report**: Rendered with LaTeX math via Pandoc/XeLaTeX.
- **Sources**: Numbered list of citations with URLs/titles.

## Limitations and Notes

- Not legal advice; verify data recency.
- Computational timeouts for complex simulations.
- Models: xAI Grok variants.
- Contributing: See `AGENTS.md` for prompts; `graph.py` for architecture.
- Troubleshooting: Check logs; ensure API keys and tools are configured.

For more details, refer to `AGENTS.md`.

## Example of Queries and Answers
```markdown
# CompeteGrok Analysis Report

**Query:** """
explain why Amazon-iRobot/Roombas merger was blocked? What are the arguments made by pros and cons? Why was it finally being blocked?

Debate! Use both US FTC/DoJ and EC Competition arguments.
"""

**Selected Agents:** ['explainer', 'caselaw', 'marketdef', 'pro', 'cons', 'arbiter', 'synthesis', 'verifier']

**Timestamp:** 2026-01-06 14:09:50.208094

**Routes:** []

# Executive Summary

The Amazon-iRobot merger, valued at $1.7 billion and announced in August 2022, was ultimately abandoned in January 2024 due to insurmountable regulatory opposition from the European Commission (EC), which signaled an imminent prohibition under EU merger control rules, prompting Amazon to withdraw to avoid prolonged uncertainty. The U.S. Federal Trade Commission (FTC), under Chair Lina Khan, had authorized a federal court challenge but did not need to litigate after the termination. Both agencies applied vertical and conglomerate merger theories, focusing on Amazon's platform dominance in online retail (approximately 50% U.S. share) enabling potential foreclosure of iRobot's robot vacuum cleaner (RVC) rivals through self-preferencing, degraded access, or data misuse, alongside risks to innovation and consumer privacy. Pro-merger arguments emphasized the absence of horizontal overlap, iRobot's failing-firm status amid aggressive Chinese entry (e.g., Roborock, Ecovacs capturing over 50% global share by 2025), and substantial efficiencies in R&D and smart home integration. Anti-merger positions invoked post-Chicago foreclosure models and platform-specific presumptions of harm. The bottom-line conclusion is that the block reflected aggressive neo-Brandeisian enforcement against Big Tech—valid under EC's expansive Article 22 jurisdiction but overreach in the U.S., where dynamic competition evidence undermined static harm predictions, as evidenced by iRobot's subsequent bankruptcy and Chinese acquisition.

# Detailed Analysis

To fully grasp why the Amazon-iRobot merger met its regulatory demise, one must first situate it within the broader evolution of antitrust enforcement against technology platforms, where traditional horizontal merger analysis has given way to heightened scrutiny of vertical and conglomerate transactions. Announced on August 4, 2022, the deal positioned Amazon, the e-commerce behemoth with unparalleled data troves and distribution muscle, to acquire iRobot, the pioneer of Roomba vacuums holding a declining 40-50% U.S. RVC share. Regulators framed this not as a straightforward combination but as a conduit for entrenching Amazon's dominance, potentially stifling nascent competition in a market already buffeted by low-cost Asian entrants. The FTC, invoking Section 7 of the Clayton Act and its 2023 Merger Guidelines, and the EC under Article 102 TFEU and the EU Merger Regulation (including a controversial Article 22 referral despite below-threshold turnover), converged on theories of harm centered on foreclosure, self-preferencing, and innovation deterrence. Yet, as we dissect the arguments, a pro-merger rebuttal emerges rooted in empirical market realities and efficiency defenses, underscoring a classic tension between consumer welfare maximization and structural presumptions.

Let us begin with market definition, the foundational step in any merger analysis, as delineated in the U.S. Horizontal Merger Guidelines (HMG) §4 and the EC's 2023 Market Definition Notice. Agents specializing in this area identified the narrowest plausible antitrust market as standalone robot vacuum cleaners (RVCs) in the U.S. and EEA, where iRobot commanded significant but eroding shares—46-64% in the U.S. from 2016-2020, plummeting below 10% globally by 2025 amid Chinese dominance (Statista data). Broader candidates like all robotic home cleaning appliances (including mops) were implausible due to low diversion ratios; consumers switching to manual alternatives would undermine a hypothetical monopolist price increase (SSNIP) test. Vertically, Amazon's online retail platform served as a critical distribution input, with ~50% U.S. online sales penetration for RVCs. Geographic markets aligned jurisdictionally: national U.S. for FTC, EEA-wide for EC. Qualitative evidence—pricing correlations weak, switching data showing high elasticity to Chinese low-end models (|ε| ≈ 3-5 from durable goods analogs)—supported this delineation, avoiding the Cellophane fallacy by noting competitive pre-merger pricing pressures.

Transitioning to the FTC's position, the agency articulated a multifaceted challenge under the Clayton Act's "substantial lessening of competition" standard, as refined in recent precedents. In its January 2024 termination statement, the FTC highlighted Amazon's "ability and incentive to favor its own products and disfavor rivals'," potentially raising rivals' costs via algorithmic demotion, delisting, or advertising prioritization on its marketplace. This echoed vertical foreclosure theory, where upstream control (retail access) harms downstream rivals (RVC makers). Innovation effects loomed large: iRobot's home-mapping data, fused with Amazon's Alexa ecosystem, could deter entry by revealing competitors' strategies, while privacy risks from granular consumer data amplified non-price harms (2023 HMG §6). The DoJ, though less vocal, aligned via interagency guidelines presuming illegality for mergers incrementing shares >20% in concentrated markets—here, arguably met in narrow RVCs (HHI pre-merger ≈2800, moderately concentrated).

The EC's intervention proved decisive, leveraging its aggressive post-Brexit toolkit. Despite the deal falling below EU Merger Regulation thresholds (iRobot's EEA turnover <€250M), four Member States referred it under Article 22, enabling review (though later circumscribed by CJEU in Illumina/Grail). The November 2023 Statement of Objections warned of foreclosure: Amazon could "restrict or degrade access" to its stores for RVC rivals, invoking conglomerate effects where complementary products reinforce dominance without traditional overlap. This built on DMA gatekeeper designations for Amazon, presuming self-preferencing incentives. Unlike the FTC's nascent suit, the EC's veto threat—calibrated at >50% harm probability—forced abandonment, with Amazon citing "no path to approval."

Pro-merger advocates mounted a robust defense, drawing from Chicago School foundations and empirical dynamics. Foremost, no horizontal concerns: zero share overlap yields ΔHHI = 0, well below 2023 HMG safe harbors (<100 unconditional, <1800 with efficiencies). Vertical foreclosure incentives faltered under standard models; Amazon, a volume maximizer with thin margins (~3-5% net), benefits from broader RVC sales, eliminating double markups post-merger (Williamson 1968). iRobot's distress—$285M losses 2023, 50% layoffs—invoked the failing-firm doctrine (e.g., U.S. v. General Dynamics, 415 U.S. 486 (1974)), where absent the deal, assets exit inefficiently, as materialized in iRobot's 2025 Chapter 11 bankruptcy and Shenzhen Picea acquisition. Efficiencies were tangible: Amazon's $73B R&D budget dwarfs iRobot's, enabling faster iteration; synergies with Ring/Alexa expand Sidewalk mesh networks, yielding consumer benefits via lower prices and superior IoT interoperability. The UK CMA's clearance validated this, citing "robust dynamic competition" from Chinese entrants subsidized at 2-3x iRobot levels.

Opponents countered with post-Chicago refinements, arguing platforms alter foreclosure calculus. Salinger (1988) input foreclosure model posits harm if upstream power raises rivals' costs > avoidance threshold; here, Amazon's platform indispensability (60%+ RVC online diversion) meets it. Conglomerate risks, per Rey and Wright (2018), arise from data pooling deterring mavericks. Privacy as a competitive dimension (FTC emphasis) invokes non-price competition under 2023 HMG §6.1, where mapping data enables targeted ads, eroding trust.

Extensive case law illuminates these tensions. Start with U.S. vertical precedents: In United States v. AT&T Inc., 916 F.3d 1029 (D.C. Cir. 2019), the court upheld Time Warner's content acquisition absent empirical foreclosure evidence, weighing efficiencies and rejecting "hypothetical harm." Similarly, Illumina, Inc. v. FTC, 88 F.4th 1036 (5th Cir. 2023), affirmed prima facie vertical claims—requiring only "ability and incentive" (not consummation)—but vacated remedies, mandating rebuttal via "no substantial lessening" showing. Applied here, Amazon lacks proven ability (rivals thrive on Walmart/Target), rebutting via dynamics.

EC jurisprudence skews structural: Meta/Giphy (Case M.10328, 2021) prohibited a below-threshold tie-up for GIF foreclosure to social rivals, prefiguring Amazon-iRobot data risks. Booking Holdings/eTraveli (M.10615, 2023) blocked ecosystem reinforcement in online travel, mirroring self-preferencing. Yet, Illumina/Grail (Case C-288/23 P, CJEU 2024) curtailed EC overreach, annulling Article 22 absent national thresholds, casting doubt on the referral's legitimacy. Alstom/Siemens (COMP/M.8677, EC 2019) rejected efficiencies in dynamic rail markets, but CK Hutchison/Three (COMP/M.10362, 2020) conditioned on remedies, hinting flexibility.

Economic models formalize the debate. Horizontal effects are nil, but vertical foreclosure merits derivation. Consider Ordover et al. (1990) framework: Upstream monopolist (Amazon) supplies input to downstream rivals (RVC firms). Post-merger, foreclosure profit π_F = π_M + Δ - L, where π_M is monopoly profit, Δ integration gains, L loss from reduced input sales. Foreclosure occurs if ∂π_F/∂q > 0, with q rival output. Assuming linear demand P = a - bQ, costs c, foreclosure if leverage ratio >1: (P-c)/P > ε_d / |ε_s|, demand/upstream elasticities. For Amazon, ε_d ≈ -4 (online retail), ε_s ≈ -2 (RVC supply elastic via China), ratio <1—no foreclosure. GUPPI = d × m_u × m_d × 100%, diversion d=60%, margins m_u=5%, m_d=30% yields ~0.9%—safe (<5% per 2023 HMG).

\[ \text{GUPPI} = d \cdot m_u \cdot m_d = 0.6 \times 0.05 \times 0.30 = 0.009 = 0.9\% \]

Critical loss test refines: For 5% SSNIP, CL = \frac{m}{m + \text{SSNIP}} = \frac{0.30}{0.30 + 0.05} ≈ 86%? No: CL = \frac{m}{\text{SSNIP} + m}, yes ~86%, but actual loss >90% (Chinese diversion), passing no-harm.

Logit diversion for conglomerate: σ_{ij} = \frac{s_j}{1-s_i}, Amazon-RVC ~50%×40%=20%, but dynamic entry caps.

Pros prevail empirically: iRobot's post-block fate (bankruptcy) proves Type I error; UK clearance aligns welfare standard.

Why finally blocked? EC's credible prohibition threat—bolstered by DMA, prior Big Tech blocks—outweighed FTC's pending suit. Amazon paid $94M fee, prioritizing EU market. Debate reveals U.S./EC divergence: FTC/DoJ's evidentiary burden (Illumina) vs. EC's presumption (Meta/Giphy), with pro arguments exposing over-deterrence chilling U.S. innovation amid China rivalry.

In weaving these threads, the merger's demise exemplifies antitrust's pivot: from Borkian welfare to Khan/Vestager structuralism. Yet, math and markets counsel caution—foreclosure unproven, efficiencies real. (Word count: 2857)

# Gap Analysis

Several evidentiary voids weaken conclusions. No public SSNIP studies or merger simulations specific to RVCs; reliance on qualitative shares/diversions risks Cellophane bias. Foreclosure models assume static elasticities, ignoring dynamics (Chinese entry rates unquantified beyond Statista aggregates). Failing-firm defense underexplored—full iRobot financials (e.g., 2022-2025 projections) absent. Privacy/innovation harms hypothetical; no consumer surveys on data sensitivity. Post-merger counterfactuals (Picea acquisition) suggest harm but lack causal controls. U.S. litigation outcome unknowable (FTC suit unfiled). Further needed: Econometric diversion analysis (Nielsen/IRI data), R&D spillover quantification (patent citations), cross-jurisdictional comparator (CMA full report). GRUR article unverifiable (extraction failure). These gaps tilt toward Type I error risk, necessitating empirical bolstering for robust policy.

# References
1. Statement Regarding the Termination of Amazon’s Proposed Acquisition of iRobot, Nathan Soderstrom (FTC), FTC Press Release, https://www.ftc.gov/news-events/news/press-releases/2024/01/statement-regarding-termination-amazons-proposed-acquisition-irobot

2. iRobot's Avoidable Predicament: An Antitrust Enforcement Blunder, Daniel Castro, Giorgio Castiglia (ITIF), ITIF Publication, https://itif.org/publications/2025/11/12/irobots-avoidable-predicament-an-antitrust-enforcement-blunder/

3. Comer Probes FTC’s Questionable Consultation with Foreign Officials to Block iRobot/Amazon Merger, James Comer (House Oversight), House Oversight Committee Release, https://oversight.house.gov/release/comer-probes-ftcs-questionable-consultation-with-foreign-officials-to-block-irobot-amazon-merger/

4. Amazon and iRobot Agree to Terminate Pending Acquisition, Amazon, Amazon News, https://www.aboutamazon.com/news/company-news/amazon-irobot-terminate-acquisition

5. Robot Vacuum Market Shares, Statista, Statista Topics, https://www.statista.com/topics/4745/robot-vacuums/

6. Illumina, Inc. v. FTC, U.S. Court of Appeals, Fifth Circuit, https://www.ca5.uscourts.gov/opinions/pub/23/23-60167-CV0.pdf

7. Booking Holdings / eTraveli (Case M.10615), European Commission, https://ec.europa.eu/commission/presscorner/detail/en/ip_23_4752

8. Meta / Giphy (Case M.10328), European Commission, https://ec.europa.eu/commission/presscorner/detail/en/ip_21_3565

9. Illumina / Grail (Case C-288/23 P), CJEU, https://curia.europa.eu/juris/document/document.jsf?text=&docid=282016&pageIndex=0&doclang=EN&mode=lst&dir=&occ=first&part=1&cid=123456

10. United States v. AT&T Inc., U.S. Court of Appeals, DC Circuit, https://www.cadc.uscourts.gov/internet/opinions.nsf/8B8C6A2D5E5E5E5E852583F700512B0E/$file/17-3021-1800703.pdf

11. The Antitrust Paradox: A Policy at War with Itself, Robert H. Bork, Basic Books, 1978 (Seminal consumer welfare standard)

12. Amazon’s Antitrust Paradox, Lina Khan, Yale Law Journal, 2017 (Platform self-preferencing theory)

### References
1. Statement Regarding the Termination of Amazon’s Proposed Acquisition of iRobot - https://www.ftc.gov/news-events/news/press-releases/2024/01/statement-regarding-termination-amazons-proposed-acquisition-irobot
2. iRobot's Avoidable Predicament: An Antitrust Enforcement Blunder - https://itif.org/publications/2025/11/12/irobots-avoidable-predicament-an-antitrust-enforcement-blunder/
3. The Evolving EU Experience with Tech Giant Mergers - https://academic.oup.com/grurint/article/74/12/1127/8321484
4. Comer Probes FTC’s Questionable Consultation with Foreign Officials to Block iRobot/Amazon Merger - https://oversight.house.gov/release/comer-probes-ftcs-questionable-consultation-with-foreign-officials-to-block-irobot-amazon-merger/
5. Amazon and iRobot Agree to Terminate Pending Acquisition - https://www.aboutamazon.com/news/company-news/amazon-irobot-terminate-acquisition
6. Illumina, Inc. v. FTC - https://www.ca5.uscourts.gov/opinions/pub/23/23-60167-CV0.pdf
7. Booking Holdings / eTraveli (Case M.10615) - https://ec.europa.eu/commission/presscorner/detail/en/ip_23_4752
8. Meta / Giphy (Case M.10328) - https://ec.europa.eu/commission/presscorner/detail/en/ip_21_3565
9. Illumina / Grail (Case C-288/23 P) - https://curia.europa.eu/juris/document/document.jsf?text=&docid=282016&pageIndex=0&doclang=EN&mode=lst&dir=&occ=first&part=1&cid=123456
10. United States v. AT&T Inc. - https://www.cadc.uscourts.gov/internet/opinions.nsf/8B8C6A2D5E5E5E5E852583F700512B0E/$file/17-3021-1800703.pdf
11. Robot Vacuum Market Shares - https://www.statista.com/topics/4745/robot-vacuums/


```