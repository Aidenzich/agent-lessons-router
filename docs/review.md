# Phase 2: Review / Post-execution

To address the common tendency of LLM Agents to overly favor the "Happy Path" while ignoring edge cases or even misinterpreting the user's deep intentions, all modifications entering the finalize stage must first go through this review process.

---

## Core Objectives

1. **Align with True Intentions**: Compare "the user's initial requirements and context" with "the current actual output (code/design)" to identify any potential gaps.
2. **Prevent the Happy Path Trap**: Proactively evaluate whether the current implementation only works under ideal conditions. Are error handling, edge cases, and system dependencies comprehensive?
3. **Resume Work on Findings**: If any discrepancies are found, strictly reject closure and force yourself (or notify the responsible process) to resume work and modify based on the gaps.
4. **Strictly Review and Report**: The task is to focus exclusively on reviewing and identifying errors. Do not proactively attempt to "fix the errors". The core emphasis is solely on reporting.

---

## Standard Operating Procedure (SOP)

1. **Enable Third-party Perspective (Subagent Standby and Execution)**:
   If the system has the capability to initiate a Subagent, **your very first action must be: start a Subagent and put it on standby**. Wait until all implementation details and context are fully organized before asking the Subagent to officially begin the review. This rule forcibly prevents the main Agent from lazily skipping the Subagent and doing a hasty self-check. The main Agent can only switch to a strict "Reviewer role" to perform the check itself if it is absolutely impossible to initiate a Subagent.
   
2. **The Review Checklist (Four Key Questions)**:
   - **Intent Alignment**: Does this implementation "truly" solve the user's core requests, or does it merely scratch the surface?
   - **Edge Case Validation**: If unexpected data is inputted, an API times out, or permissions are lacking, will this code gracefully exit? Will it cause any silent bugs?
   - **Global Perspective (Local Minimum Detection)**: **Review whether you are stuck in a Local Minimum.** If you realize that countless patches have been layered just to fix a minor error, making the logic unusually complex and bloated, you must decisively break away from the current mindset and look for a cleaner, more fundamental underlying solution.
   - **Knowledge Base Compatibility**: Does this change violate any historical lessons or architectural conventions documented in `.agent-lessons`? Is it a genuine solution or just a dirty hack?

3. **Strict Execution Gate & Rework**:
   The review process has extremely strict rules (Gates) to prevent superficial work or perfunctory task closure:
   - **No Vague Suggestions**: The review report strictly forbids meaningless fluff like "can be optimized in the future" or "great job".
   - **Binary Verdict (Findings or PASS)**: The review result **only accepts** specific `Findings` (clear logic flaws or gaps) or an absolute declaration of `PASS`.
   - **Mandatory Rework**: The moment any `Findings` appear, the Agent **is absolutely forbidden from simply closing the task**. The issues must immediately be listed as TODOs for rework and fixing. If a defect involves a gray area, extreme scenarios must be organized and clarified with the user; do not mentally invent a Happy Path.
   - **Iterative Review (Loop Until Pass)**: **After fixing, you must review again!** The end of rework does not mean the end of the task. You must forcibly restart the Phase 2 review process until the audit yields zero Findings and achieves a 100% `PASS`. Only then can you proceed to the next stage (Phase 3).
