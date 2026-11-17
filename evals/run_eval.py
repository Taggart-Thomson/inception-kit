#!/usr/bin/env python3
"""Run every intent through Claude Code headless, score the spec, log time and cost.

  .venv/bin/python evals/run_eval.py                 # skill and baseline, all intents
  .venv/bin/python evals/run_eval.py --mode skill --only export-invoices
  .venv/bin/python evals/run_eval.py --jobs 3        # three runs at a time

"skill" runs /inception (skill + validator + ac-reviewer subagent).
"baseline" runs a plain prompt with skills and subagents switched off. It is given the
same output format, so the same scorer can read both.
Each run appends one row to evals/results.csv. This spends real API or plan usage.
"""
import argparse
import csv
import importlib.util
import json
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
SKILL = ROOT / ".claude/skills/inception"
RESULTS = ROOT / "evals/results.csv"
FIELDS = ["run_at", "mode", "model", "slug", "seconds", "cost_usd", "turns", "status",
          "units", "stories", "criteria", "edge_cases", "score", "approved", "error"]

# Load check() from the skill's validator so the eval and the skill score the same way.
_spec = importlib.util.spec_from_file_location("validate_spec", SKILL / "scripts/validate_spec.py")
validator = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validator)


def command(mode, intent, out_path, model):
    """Build the headless Claude Code command for one run."""
    rel = out_path.relative_to(ROOT)
    # The prompt goes straight after -p: --allowedTools takes a list and would swallow it.
    flags = ["--model", model, "--output-format", "json",
             "--permission-mode", "acceptEdits", "--max-budget-usd", "3"]
    if mode == "skill":
        prompt = f"/inception {intent} (save the spec as {rel})"
        tools = "Read,Write,Edit,Agent,Bash(python3 .claude/skills/inception/scripts/validate_spec.py *)"
        return ["claude", "-p", prompt] + flags + ["--allowedTools", tools]
    template = (SKILL / "template.md").read_text(encoding="utf-8")
    prompt = (f"Write units of work, user stories and acceptance criteria for: {intent}\n"
              f"Save the result to {rel} in exactly this format:\n\n{template}")
    return ["claude", "-p", prompt] + flags + ["--disable-slash-commands", "--disallowedTools", "Agent",
                                               "--allowedTools", "Read,Write,Edit"]


def run_one(mode, item, model):
    """Run one intent in one mode and return its results row."""
    folder = ROOT / "specs" if mode == "skill" else ROOT / "evals/runs/baseline"
    folder.mkdir(parents=True, exist_ok=True)
    out_path = folder / f"{item['slug']}.md"
    out_path.unlink(missing_ok=True)  # never score a spec left over from an earlier run

    row = dict.fromkeys(FIELDS, "")
    row.update(run_at=datetime.now(timezone.utc).isoformat(timespec="seconds"),
               mode=mode, model=model, slug=item["slug"])
    started = time.monotonic()
    try:
        done = subprocess.run(command(mode, item["intent"], out_path, model), cwd=ROOT,
                              capture_output=True, text=True, timeout=1200)
        reply = json.loads(done.stdout)
        row.update(cost_usd=round(reply.get("total_cost_usd", 0), 4), turns=reply.get("num_turns", ""))
        if reply.get("is_error"):
            row["error"] = str(reply.get("result", ""))[:200]
    except (subprocess.TimeoutExpired, json.JSONDecodeError) as err:
        row["error"] = f"{type(err).__name__}: {(getattr(err, 'doc', '') or '')[:150]}"
    row["seconds"] = round(time.monotonic() - started)

    if not out_path.exists():
        row.update(status="no-file", score=0, approved=False)
        return row
    report = validator.check(out_path.read_text(encoding="utf-8"))
    row.update({key: report[key] for key in ("status", "units", "stories", "criteria", "edge_cases", "score")})
    row["approved"] = report["status"] == "approved"
    if report["status"] == "blocked":
        row["score"] = ""  # asked questions and wrote no criteria: nothing to score
    return row


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--mode", choices=["skill", "baseline", "both"], default="both")
    parser.add_argument("--only", default="", help="comma-separated slugs")
    parser.add_argument("--model", default="sonnet")
    parser.add_argument("--jobs", type=int, default=1, help="runs in parallel")
    args = parser.parse_args()

    intents = yaml.safe_load((ROOT / "evals/intents.yaml").read_text(encoding="utf-8"))
    if args.only:
        intents = [i for i in intents if i["slug"] in args.only.split(",")]
    modes = ["skill", "baseline"] if args.mode == "both" else [args.mode]
    jobs = [(mode, item) for mode in modes for item in intents]

    new_file = not RESULTS.exists()
    with RESULTS.open("a", newline="", encoding="utf-8") as handle, ThreadPoolExecutor(args.jobs) as pool:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        if new_file:
            writer.writeheader()
        for row in pool.map(lambda job: run_one(job[0], job[1], args.model), jobs):
            writer.writerow(row)
            handle.flush()
            print(f"{row['mode']:9}{row['slug']:20}{row['seconds']:>5}s  ${row['cost_usd']:<8}"
                  f"score={row['score']!s:5} edge={row['edge_cases']!s:3} status={row['status']} {row['error']}")


if __name__ == "__main__":
    main()
