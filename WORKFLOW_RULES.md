# WORKFLOW_RULES.md

## Operating Standard

1. **Plan before execution**
   - For any non-trivial task, define a brief plan before touching files.
   - Clarify assumptions and expected outputs.

2. **Verify before done**
   - Never mark a task complete without verification (render/test/check output).
   - Include validation evidence when reporting completion.

3. **Elegant over hacky**
   - Prefer minimal, coherent fixes that preserve maintainability.
   - Avoid brittle patches unless explicitly requested as temporary.

4. **Autonomous bug fixing**
   - If a fix introduces regressions, immediately diagnose and repair.
   - Do not stop at partial failure; close the loop.

5. **Task tracking discipline**
   - Keep clear status: planned, in progress, blocked, done.
   - Summarize what changed, why, and what remains.

6. **Scope control**
   - Change only what is needed for the requested outcome.
   - Avoid side-effects and unrelated refactors.

7. **Communication quality**
   - Be concise, accurate, and explicit about risks.
   - If uncertain, state uncertainty and next concrete step.

8. **Git hygiene**
   - Commit meaningful units of work.
   - Use descriptive commit messages unless user requests otherwise.
   - Push website-impacting changes immediately when requested.

9. **Safety / privacy first**
   - Never commit secrets, private tokens, or sensitive personal assets.
   - If exposure risk is found, rotate/remove and report.

10. **Continuous improvement**
   - Capture recurring lessons and apply them in future tasks.

---

This file is the default execution protocol for this workspace.
