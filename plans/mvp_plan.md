# CompeteGrok MVP Preparation Plan

## 1. Analysis Summary

### Codebase Status
- **Architecture:** Solid LangGraph implementation with Supervisor routing.
- **Agents:** Aligned with `AGENTS.md` specifications.
- **Tools:** Functional wrappers for Tavily, Linkup, PDF conversion.
- **Logging:** Structured JSON logging implemented.

### Identified Gaps
1.  **Mock Data Risks:** Tools (`tavily_search`, `linkup_search`) currently fallback to mock data on error. This is risky for a "rigorous" system intended for economists/lawyers.
2.  **Output Validation:** Agents like `econpaper` and `caselaw` are prompted to return JSON, but there is no code-level validation (e.g., Pydantic) to ensure the output is parseable and conforms to the schema before downstream consumption.
3.  **Fragile PDF Handling:** The `econpaper` agent prompt contains complex logic for handling PDF conversion errors ("If result['success'] == False..."). This logic is better handled in the Python tool wrapper to reduce token usage and increase reliability.
4.  **Verifier Routing:** The `verifier` agent is critical for citations. Currently, its execution depends on `teamformation` selecting it. A safety net in `graph.py` should ensure it *always* runs if research agents are active.
5.  **Debate Logic:** The debate subgraph is linear. Ensuring it can handle dynamic back-and-forth effectively within the round limits is key.

## 2. Implementation Plan

### Phase 1: Robustness & Validation (High Priority)
*   **Task 1.1: Strict Mode for Tools**
    *   Modify `config.py` to add a `STRICT_MODE` flag (default `True` for MVP).
    *   Update `tools/wrappers.py` to raise exceptions instead of returning mocks when `STRICT_MODE` is enabled.
*   **Task 1.2: Output Validation**
    *   Create `schemas.py` to define Pydantic models for:
        *   `EconPaperOutput` (list of papers)
        *   `CaseLawOutput` (list of cases)
        *   `VerifierOutput` (list of verified citations)
    *   Update `agents/` to use `with_structured_output` or a validation step in the node function.
*   **Task 1.3: Refactor PDF Handling**
    *   Update `tools/convert_pdf_url.py` (or wrapper) to handle retries and alternative URL searching internally, or create a new "smart" tool `fetch_paper_content` that handles this logic.
    *   Simplify `econpaper.py` prompt to use this new robust tool.

### Phase 2: Logic & Flow (Medium Priority)
*   **Task 2.1: Enforce Verification**
    *   Modify `graph.py` `supervisor_node` logic: Explicitly force `verifier` into the route if `econpaper` or `caselaw` was in the previous step, regardless of `teamformation` output.
*   **Task 2.2: Debate Logic Review**
    *   Review `debate.py` to ensure the `arbiter` correctly evaluates the `debate_round` and loops back to `pro` if needed.
    *   Add a check to ensure `pro` and `cons` actually respond to each other (context preservation).

### Phase 3: Testing (Medium Priority)
*   **Task 3.1: Unit Tests**
    *   Run existing tests in `tests/`.
    *   Fix any failures.
*   **Task 3.2: Integration Tests**
    *   Create a new test `tests/test_workflow_integration.py` that mocks tool outputs and verifies the graph transitions (Supervisor -> EconPaper -> Verifier -> Synthesis).

### Phase 4: Documentation & Polish (Low Priority)
*   **Task 4.1: Update README**
    *   Document the `STRICT_MODE` flag.
    *   Update setup instructions.
*   **Task 4.2: Logging**
    *   Verify that `sequential_thinking` steps are logged clearly for audit trails.

## 3. Task Ranking (Difficulty vs. Impact)

| Task | Difficulty | Impact | Priority |
|------|------------|--------|----------|
| 1.1 Strict Mode | Low | High | **Critical** |
| 2.1 Enforce Verification | Low | High | **Critical** |
| 1.2 Output Validation | Medium | High | **High** |
| 1.3 Refactor PDF Handling | Medium | Medium | **High** |
| 3.1 Unit Tests | Low | Medium | **Medium** |
| 3.2 Integration Tests | Medium | Medium | **Medium** |
| 2.2 Debate Logic | Medium | Low | **Low** |
| 4.1 Documentation | Low | Low | **Low** |
