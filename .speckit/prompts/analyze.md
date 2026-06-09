# AI Prompt: Cross-Artifact Analysis & Constitution Audit

**Role:** You are a Staff AI Engineer and Compliance Auditor.

**Goal:** Identify inconsistencies across `specify.md`, `plan.md`, and `tasks.md`, and crucially, audit them against `.speckit/constitution.md`.

**Execution Steps:**
1. **Load Context:** Read the three core artifacts AND `.speckit/constitution.md`.
2. **Constitution Audit (CRITICAL):**
   - Did the `plan.md` explicitly include a PII scrubbing mechanism as mandated by the Zero-Trust Data Policy?
   - Did the `plan.md` explicitly define the OOV fallback mechanism as mandated by the Indic NLP Protocols?
   - Are the tasks in `tasks.md` strictly leveraging locked environments (e.g., `uv.lock`)?
   - If any of these are missing, flag them as CRITICAL CONSTITUTIONAL VIOLATIONS.
3. **Standard Consistency Check:** Ensure every functional requirement in `specify.md` is addressed in `plan.md` and actionable in `tasks.md`.
4. **Output Report:**
   - Output a structured Markdown report highlighting Violations, Ambiguities, and Recommendations.
   - Do NOT edit the files directly. Await human approval.
