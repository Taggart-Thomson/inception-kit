#!/usr/bin/env python3
"""Structural checks for an inception spec.

Usage: validate_spec.py specs/<slug>.md [--json]
Exits 0 when every check passes, 1 when any fails, 2 when the file can't be read.
"""
import json
import re
import sys

VAGUE = ["fast", "quickly", "easy", "easily", "user-friendly", "intuitive",
         "seamless", "appropriate", "etc"]
VAGUE_RE = re.compile(r"\b(" + "|".join(map(re.escape, VAGUE)) + r")\b", re.I)
GWT_RE = re.compile(r"\bgiven\b.+\bwhen\b.+\bthen\b", re.I)
STATUS_RE = re.compile(r"^status:\s*([\w-]+)", re.M)


def parse(text):
    """Turn the markdown into units -> stories -> criteria."""
    units = []
    for line in (raw.strip() for raw in text.splitlines()):
        if line.startswith("## Unit"):
            units.append({"name": line[3:], "stories": []})
        elif line.startswith("### Story") and units:
            units[-1]["stories"].append({"name": line[4:], "criteria": []})
        elif line.startswith("- **AC") and units and units[-1]["stories"]:
            units[-1]["stories"][-1]["criteria"].append(line)
    return units


def check(text):
    """Run every check. Each one adds to `checks`; each failure adds a message."""
    units, problems, checks = parse(text), [], 0

    def expect(ok, message):
        nonlocal checks
        checks += 1
        if not ok:
            problems.append(message)

    expect(units, "No units of work found (expected '## Unit N: ...' headings).")
    stories = [s for u in units for s in u["stories"]]
    criteria = [c for s in stories for c in s["criteria"]]
    for unit in units:
        expect(unit["stories"], f"{unit['name']}: has no user story.")
    for story in stories:
        expect(len(story["criteria"]) >= 2, f"{story['name']}: needs at least 2 acceptance criteria.")
        expect(any("[edge]" in c for c in story["criteria"]), f"{story['name']}: no [edge] criterion.")
    for crit in criteria:
        label = crit.split("**")[1] if crit.count("**") >= 2 else crit[:30]
        expect(GWT_RE.search(crit), f"{label}: not in Given / When / Then form.")
        vague = VAGUE_RE.search(crit)
        expect(not vague, f"{label}: vague word '{vague.group(1) if vague else ''}' can't be tested.")

    status = STATUS_RE.search(text)
    return {
        "status": status.group(1) if status else "missing",
        "units": len(units), "stories": len(stories), "criteria": len(criteria),
        "edge_cases": sum("[edge]" in c for c in criteria),
        "checks": checks, "problems": problems,
        "score": round((checks - len(problems)) / checks, 2),
    }


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if a != "--json"]
    try:
        report = check(open(args[0], encoding="utf-8").read())
    except (IndexError, OSError) as err:
        print(f"Usage: validate_spec.py <spec.md> [--json]  ({err})", file=sys.stderr)
        sys.exit(2)
    if "--json" in sys.argv:
        print(json.dumps(report))
    else:
        for problem in report["problems"]:
            print(f"FAIL  {problem}")
        print(f"{report['checks'] - len(report['problems'])}/{report['checks']} checks passed "
              f"({report['stories']} stories, {report['criteria']} criteria, {report['edge_cases']} edge cases)")
    sys.exit(1 if report["problems"] else 0)
