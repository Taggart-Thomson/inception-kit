# Proof that the gates work

Both runs below are real headless Claude Code sessions in this repo (`claude -p`, Sonnet), copied from the terminal. To repeat them, use the commands shown.

## 1. The spec gate blocks a code edit

State: `specs/` held no approved spec.

```bash
claude -p "Add a one-line comment '# demo' at the very top of src/booking.py using the Edit tool. If you are blocked, do not work around it; just report exactly what you were told." --permission-mode acceptEdits --model sonnet
```

Claude's reply:

> Blocked, so I didn't make the edit. The Edit tool call on `src/booking.py` was rejected by a PreToolUse hook (`.claude/hooks/spec_gate.py`) with this message:
>
> > Blocked: src/booking.py is under src/ and no spec in specs/ has 'status: approved'. Run /inception <intent> first, and let the ac-reviewer subagent approve the spec.
>
> I haven't tried any workaround. The file is unchanged.

`src/booking.py` was unchanged afterwards. 3 turns, $0.10.

## 2. The tests gate stops Claude finishing on a red suite

State: one test was broken on purpose (the "less than 24 hours" test was given 30 hours), so `pytest` reported `1 failed, 2 passed`.

```bash
claude -p "Reply with the single word: done" --permission-mode acceptEdits --model sonnet
```

Claude was asked only to say "done". The Stop hook ran the tests, exited 2, and sent the failure back. Claude's final reply:

> I fixed the failing test, but I couldn't run the suite to confirm. Both attempts to run `python -m pytest` were blocked pending approval.
>
> The test `test_reschedule_is_refused_with_less_than_24_hours_notice` in `tests/test_booking.py` used a booking starting 30 hours away. That has more than 24 hours' notice, so `reschedule` correctly allowed it and the expected `ValueError` never came. I changed the start time to 10 hours away. I left `src/booking.py` alone because its 24-hour rule is correct.

`pytest` reported `3 passed` afterwards. 6 turns, $0.14.

Two things this run also shows:

- Claude could not run `pytest` itself, because the headless run was not given permission to. The hook is what ran the tests, both times.
- The hook lets Claude stop on the second attempt whatever the result (`stop_hook_active`), so a test Claude cannot fix does not loop forever. That means the gate forces one repair attempt, not a guarantee of green.

## 3. Direct tests of the hook scripts

The hooks are plain scripts that read JSON on stdin, so they can be tested without Claude:

| Input | Script | Exit code |
| --- | --- | --- |
| Edit `src/booking.py`, no approved spec | `spec_gate.py` | 2 (blocked) |
| Edit `README.md`, no approved spec | `spec_gate.py` | 0 |
| Edit `src/booking.py`, one spec approved | `spec_gate.py` | 0 |
| Stop, tests pass | `tests_gate.sh` | 0 |
| Stop, tests fail | `tests_gate.sh` | 2 (sent back) |
| Stop, tests fail, `stop_hook_active: true` | `tests_gate.sh` | 0 |
