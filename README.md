# inception-kit

`inception-kit` turns a one-line product intent into units of work, user stories and testable acceptance criteria. A reviewer subagent then challenges any criterion that can't be tested, and a hook gates code changes so nothing gets built without an approved spec. A small evaluation harness scores the output on a fixed set of intents and logs time and cost per run, so the before/after number is measured rather than claimed.

It is tooling built around [Claude Code](https://code.claude.com/docs): one skill, one subagent, two hooks and an eval script. Each piece is small enough to read in a few minutes.

## How it fits together

```
/inception "Export monthly invoices as CSV"
      │
      ▼
 skill (SKILL.md)          restates the intent, lists assumptions and open questions,
      │                    writes units → stories → Given/When/Then criteria
      ▼
 validate_spec.py          structural checks; the skill fixes what it flags
      │
      ▼
 ac-reviewer subagent      sceptical QA lead: rewrites weak criteria, adds edge cases,
      │                    sets status: approved only if every criterion is testable
      ▼
 specs/<slug>.md           status: draft | approved | blocked
      │
      ▼
 spec_gate.py (hook)       blocks any edit under src/ until a spec is approved
 tests_gate.sh (hook)      sends Claude back to work if the tests fail when it tries to stop
```

| Piece | File | What it does |
| --- | --- | --- |
| Skill | [.claude/skills/inception/SKILL.md](.claude/skills/inception/SKILL.md) | The `/inception` workflow, in nine steps |
| Template | [.claude/skills/inception/template.md](.claude/skills/inception/template.md) | The spec format the skill fills in |
| Validator | [.claude/skills/inception/scripts/validate_spec.py](.claude/skills/inception/scripts/validate_spec.py) | Every unit has a story, every story has at least 2 criteria and an edge case, every criterion is Given/When/Then with no vague words |
| Subagent | [.claude/agents/ac-reviewer.md](.claude/agents/ac-reviewer.md) | Reviews for testability; the only thing allowed to approve a spec |
| Spec gate | [.claude/hooks/spec_gate.py](.claude/hooks/spec_gate.py) | `PreToolUse` hook on `Edit`, `Write`, `MultiEdit`, `NotebookEdit` |
| Tests gate | [.claude/hooks/tests_gate.sh](.claude/hooks/tests_gate.sh) | `Stop` hook that runs `pytest` |
| Wiring | [.claude/settings.json](.claude/settings.json) | Connects the two hooks |
| Eval | [evals/run_eval.py](evals/run_eval.py) | Runs the fixed intents headless, with and without the kit |
| Demo app | [src/booking.py](src/booking.py), [tests/](tests/) | A 20-line rule and 3 tests, so the gates have something to guard |

## Try it

Needs Python 3.10 or later and Claude Code.

```bash
python3 -m venv .venv
```

```bash
.venv/bin/pip install -r requirements-dev.txt
```

```bash
.venv/bin/pytest -q
```

Then open Claude Code in this folder and run:

```
/inception Let customers reschedule a booked appointment up to 24 hours before it starts
```

The spec lands in `specs/`. To check any spec by hand:

```bash
python3 .claude/skills/inception/scripts/validate_spec.py specs/reschedule-booking.md
```

## The gates, proven

Real transcripts are in [docs/gates-proof.md](docs/gates-proof.md). In short:

- With no approved spec, Claude was asked to edit `src/booking.py`. The hook refused the edit and Claude reported the reason back, word for word.
- With one test broken, Claude was asked only to reply "done". The hook ran the tests, sent the failure back, and Claude repaired the test before it could finish.

## The honest number

Six fixed intents, each run once with the kit and once with a plain prompt, both on Sonnet and both scored by the same code.

| Measure (mean of 5 clear intents) | Plain prompt | With the kit |
| --- | --- | --- |
| Structural score | 1.00 | 1.00 |
| Edge-case criteria per spec | 10.4 | 16.8 |
| Specs approved by the reviewer | 0 of 5 | 0 of 5 |
| Time per spec | 20 s | 63 s |
| Cost per spec | $0.11 | $0.24 |

- **Better:** 62% more edge-case criteria. On the vague intent ("Make the dashboard better") the plain prompt invented 12 criteria for a dashboard nobody had described; the kit wrote none and asked 7 questions.
- **No different:** the structural score. Given the same template, the plain prompt fills it in correctly too.
- **Not yet:** no spec was approved. The reviewer held every one at `draft` because criteria rested on product decisions nobody had made. Approval needs a person to answer the open questions, and I have not yet measured how many rounds that takes.
- **Worse:** about three times slower and twice the cost per spec.

Method, full table and what did not work: [docs/before-after.md](docs/before-after.md). Raw rows: [evals/results.csv](evals/results.csv).

To rerun it (this spends real API or plan usage, a few dollars on Sonnet):

```bash
.venv/bin/python evals/run_eval.py --jobs 3
```

## Known limits

- The spec gate opens when *any* spec is approved. It does not check that the edit belongs to that spec.
- The gate covers the file-editing tools. A shell command such as `sed` can still change `src/`.
- The tests gate forces one repair attempt and then lets Claude stop, so it cannot loop forever. It is not a guarantee of a green suite; CI should be.
- The validator checks structure, not sense. A criterion can be well-formed and still wrong. That is the reviewer's job, and after it a human's.
- The eval is one run per intent on six intents. It shows direction, not a statistically firm effect.

## What I'd build next

- **An MCP server** with `list_specs` and `get_spec`, so other agents and tools can read approved specs.
- **A cost dashboard** over `results.csv`: cost and time per intent across runs and models.
- **A tighter gate**: each spec names the paths it covers, and the hook checks the edit against them.
- **Repeat runs** in the eval (3 to 5 per intent) to report a range in place of a single figure.
