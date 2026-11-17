---
name: inception
description: Turn a product intent into units of work, user stories and Given/When/Then acceptance criteria. Use at the start of any new feature.
argument-hint: "[one-line product intent]"
allowed-tools: Read, Write, Edit, Agent, Bash(python3 ${CLAUDE_SKILL_DIR}/scripts/validate_spec.py *)
---

# Inception

Intent: $ARGUMENTS

Turn the intent above into a spec a team could build and test from. Work through these steps in order.

1. **Restate and question.** Restate the intent in one or two sentences. List the assumptions you are making and the open questions only a product owner could answer.

   **If the intent is too vague to test** (you cannot name who the user is, what they do, or what outcome would count as success), do not invent a spec. Save `specs/<slug>.md` with `status: blocked`, containing only the Intent and Open questions sections of the template, show the questions to the user, and stop here. A guessed spec is worse than no spec.

2. **Split into units of work.** 2 to 5 units, each deliverable on its own.

3. **Write user stories** for each unit: "As a <role>, I want <capability>, so that <benefit>."

4. **Write acceptance criteria** for each story: 2 to 4, each in Given / When / Then form, on one line. At least one per story must be an edge or failure case, marked `[edge]`. Every "then" must be something a tester can observe: a value, a message, a state, a count. Use exact numbers and limits in place of words like "fast" or "easy".

5. **Save the spec.** Read `${CLAUDE_SKILL_DIR}/template.md`, fill it in, and save it to `specs/<slug>.md` with `status: draft`. Keep the heading and `- **AC n.n.n**` formats exactly; the validator parses them.

6. **Validate.** Run:

   ```
   python3 ${CLAUDE_SKILL_DIR}/scripts/validate_spec.py specs/<slug>.md
   ```

   Fix every line it prints as `FAIL` and run it again until it exits clean.

7. **Hand off for review.** Use the `ac-reviewer` subagent on `specs/<slug>.md`. Do not set `status: approved` yourself; only the reviewer may.

8. **Check the reviewer's work.** Run the validator once more. If it fails, fix the flagged lines without weakening the criteria.

9. **Report** in a few lines: the spec path, its status, the counts of units, stories and criteria, and any open questions that still need a human answer.
