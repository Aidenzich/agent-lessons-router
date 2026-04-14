# Deep Reflection Protocol (Infinite Loop Recovery)

This document is ONLY to be read when an Agent is trapped in an **Infinite Loop** (detected via the 8-action heuristic) during High-Autonomy mode. 

## 🧠 The First-Principle Reset

When your actions are yielding zero progress for 8 consecutive steps, you have reached a "Cognitive Deadlock". Do not stop; instead, perform a total reset of your reasoning chain.

### 1. Dynamic Confidence Re-evaluation
Discard your existing plan. It has failed. Ask:
- "What if my core assumption about this technical stack is 100% wrong?"
- "Is there a physical hard-blocker I am pretending doesn't exist?"
- "What is the most 'Geek-Correct' path that I am avoiding because it looks too difficult?"

### 2. Radical Skepticism
Force a pivot:
- **If you were grepping code**: Switch to investigating documentation or environment variables.
- **If you were reviewing adapters**: Switch to investigating the database schema or raw logs.
- **The Knowledge Boundary**: If you are repeating searches, you are blind. You must change your sensory input (tool choice).

### 3. Knowledge Delta Reconstruction
Instead of "Conclusion", perform a **Synthesis of the Blockage**:
- Clearly define the "Gap" that cannot be bridged.
- If the knowledge is truly unreachable, the mission hasn't ended—it has **evolved**. You must present the evolution of the problem to the user as a new engineering challenge, not a failure report.

## 🚀 The Breakthrough Mandate

1. **Self-Activation**: Explicitly state: "Infinite Loop detected at 8+ steps. Cognitive Deadlock reached. Initiating Deep Reflection Protocol."
2. **First-Principle Pivot**: Adopt a radically different strategy (e.g., use `run_command` to test a hypothesis instead of just reading more code).
3. **Synthesis**: Present the new, deeper understanding of the "Hard-Block" to the user, proposing a structural change rather than a "Best-effort" summary.

> "The hardest part of any journey is not stopping, but daring to start again from zero."

