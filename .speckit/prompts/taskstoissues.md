# AI Prompt: Tasks to Issues Conversion

**Role:** You are a Project Manager Agent.

**Goal:** Convert the markdown tasks from `tasks.md` into a structured, universally importable JSON array for GitLab/GitHub issue trackers.

**Execution Steps:**
1. **Load Context:** Parse `tasks.md`, `specify.md`, and `plan.md`.
2. **Enrichment:** For each pending `[ ]` task, generate a JSON object with:
   - `title`: A concise, descriptive title.
   - `description`: A detailed body extracting context from the Plan.
   - `labels`: An array of suggested tags.
3. **Constitution Tagging (CRITICAL):**
   - If the task involves Data Ingestion, automatically append the label: `requires-pii-review`.
   - If the task involves Telugu NLP, automatically append the label: `indic-nlp`.
4. **Format Output:** Export this exact data as `issues_export.json` in the project root. Do not run any CLI tools to upload them; just provide the JSON payload.
