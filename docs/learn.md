# Phase 3: Learn & Write (Post-task)

We refuse the accumulation of errors, and we refuse the accumulation of nonsense. Every Lesson must be a **highly precise conclusion that can be directly executed**, rather than a lengthy story or background description.

## Writing Prerequisite (Gatekeeper)

A lesson can only be written if **any one** of the following conditions is met:
- The code has passed tests (CI/Tests Passed).
- A human explicitly instructed: "Record this down", "Remember this gotcha", or used the `/learn` command.

## Writing Principle: Minimalist Learning Method

The core of every Lesson is a single-sentence conclusion that future Agents can **directly follow as an instruction**. Ask yourself:

> "If a future Agent only reads this one sentence, can it avoid this pitfall?"

If not, rewrite it until it can.

### Formatting Guidelines

Create a Markdown file under `.agent-lessons/lessons/`, and the naming must be specific (e.g., `stripe_webhook_idempotency.md`).

**Formatting Advice:** If appropriate, you can use Markdown Tables to organize information. However, please pay special attention: **when using a Table, only one `-` is needed per column separator**, for example:

|-|-|-|

This effectively avoids generating too many separator characters, which can lead to token waste or slow generation.

```markdown
# [Precise Title, e.g., Stripe Webhook MUST do idempotency check]

## Rule
<!-- A one-sentence conclusion. This is the most important part of the entire file. -->
<!-- Example: "The Stripe webhook handler must use event.id for idempotency checks, otherwise retries will lead to duplicate charges." -->

## Don't
<!-- The wrong approach, in one sentence. Omit obvious content. -->
<!-- Example: "Do not trust the arrival order of webhooks." -->

## Why (Optional)
<!-- Only write if the reason is not obvious. Limit to 1-2 sentences. -->

## Refs (Optional)
<!-- Related file paths or links, as a pure list without explanatory text. -->

## Updated
<!-- YYYY-MM-DD -->
```

**Anti-patterns — The following content is forbidden in a Lesson:**
- ❌ Lengthy Context / Background stories ("We were doing project X back then, and because of requirement Y...")
- ❌ A chronological log of the exploration process ("First tried A, didn't work, then tried B...")
- ❌ Obvious conclusions ("Testing is important", "Read the documentation")

## Update the Router Table

After writing a Lesson, you must synchronously update `.agent-lessons/index.md` in this format:

| File Path | One-Sentence Conclusion | Tags |
|-|-|-|

## Clean up Obsolete Information

If a newly verified result conflicts with an old Lesson, **directly overwrite or delete** the obsolete rule. The knowledge base only retains current, correct conclusions.
