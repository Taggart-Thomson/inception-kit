# Before and after: what the kit changed, measured

Run on 17 November 2026 with Claude Code 2.1.316, model `sonnet`, one run per intent. Raw rows are in [evals/results.csv](../evals/results.csv). The specs that were scored are in [specs/](../specs/) (with the kit) and [evals/runs/baseline/](../evals/runs/baseline/) (without).

## Method

Six fixed intents from [evals/intents.yaml](../evals/intents.yaml): five clear, one vague on purpose ("Make the dashboard better").

- **After (skill):** `claude -p "/inception <intent>"`. The skill writes the spec, runs the validator, and hands off to the `ac-reviewer` subagent.
- **Before (baseline):** `claude -p "Write units of work, user stories and acceptance criteria for: <intent>"` with skills and subagents switched off.

The baseline was given the same output template as the skill. Without it the scorer could not parse the baseline's output and would score it zero, which would flatter the kit. So this comparison measures the workflow (instructions, validator, reviewer), not the format.

Both are scored by the same code, `check()` in `validate_spec.py`:

- **Structural score:** share of checks passed (each unit has a story; each story has at least 2 criteria and an `[edge]` one; each criterion is Given/When/Then with no vague word).
- **Edge cases:** criteria marked `[edge]`.
- **Approved:** the spec's front matter says `status: approved`.

## Results

Five clear intents, mean per intent:

| Measure | Before (plain prompt) | After (kit) | Change |
| --- | --- | --- | --- |
| Structural score | 1.00 | 1.00 | none |
| Acceptance criteria | 17.8 | 23.2 | +30% |
| Edge-case criteria | 10.4 | 16.8 | +62% |
| Specs approved | 0 of 5 | 0 of 5 | none |
| Time | 20 s | 63 s | 3.2 times longer |
| Cost | $0.11 | $0.24 | 2.2 times more |

The vague intent:

| | Before (plain prompt) | After (kit) |
| --- | --- | --- |
| "Make the dashboard better" | Invented a dashboard: 3 units, 6 stories, 12 criteria, marked `draft` | Wrote no criteria. Saved 7 open questions with `status: blocked` |

Per intent (edge-case criteria, before → after): reschedule-booking 11 → 14, export-invoices 10 → 14, password-reset 8 → 19, low-stock-alert 9 → 16, team-invite 14 → 21.

The whole evaluation (12 runs) cost $1.91.

## What worked

- **The vague intent.** The plain prompt produced 12 well-formed criteria for a dashboard nobody had described. They pass every structural check and are useless. The kit refused, and asked who the user is, what is wrong today and what number would count as success.
- **Edge cases.** The reviewer added between 4 and 13 criteria to each spec and rewrote up to 8, mostly boundaries, invalid input and failures of a dependency.
- **The reviewer did not rubber-stamp.** It approved nothing, and each spec's `## Review` section says why.

## What did not work, or not yet

- **Structural score shows no difference.** Once the plain prompt is given the template, Sonnet fills it in correctly every time. The validator did not separate the two. It still earns its place as a cheap check inside the skill, but it is not evidence the kit is better.
- **Nothing was approved.** In every clear intent the reviewer left `status: draft`, because criteria rested on product decisions nobody had made (8 to 12 open questions per spec, such as which time zone "24 hours before" uses). That is the reviewer doing its job, but it means a headless run never ends in an approved spec, and the spec gate stays shut. Approval needs a person to answer the questions. I have not yet measured how many rounds that takes.
- **The baseline was not approved either, by construction.** Nothing in the baseline can approve a spec, so "0 of 5" on both sides is not a like-for-like result.
- **More edge cases is not the same as better ones.** The `[edge]` tag is applied by the model that wrote the criterion. Nobody has yet checked a sample by hand to see how many are real, distinct and worth testing.
- **It costs more.** About three times the time and twice the money per spec. At these sizes that is 43 seconds and 13 cents, but the ratio would matter at volume.
- **Small sample.** One run per intent, six intents, one model. Runs went three at a time, which slightly inflates the times. The baseline's first run cost $0.21 against about $0.08 for the others, most likely a cold prompt cache, and it pulls the baseline mean up.

## Next measurements

1. Run each intent 3 to 5 times and report a range.
2. Hand-grade a sample of edge-case criteria from both sides, blind to which side wrote them.
3. Answer the open questions for each spec and count the rounds to approval.
