#!/usr/bin/env python3
"""PreToolUse gate: no edits under src/ until a spec in specs/ is approved.

Claude Code sends the tool call as JSON on stdin. Exit 0 lets the edit through.
Exit 2 blocks it, and whatever is written to stderr is shown to Claude as the reason.
"""
import json
import os
import re
import sys
from pathlib import Path

call = json.load(sys.stdin)
root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or call.get("cwd") or ".").resolve()
tool_input = call.get("tool_input", {})
target = tool_input.get("file_path") or tool_input.get("notebook_path") or ""
if not target:
    sys.exit(0)

try:
    relative = (root / target).resolve().relative_to(root)  # an absolute target replaces root
except ValueError:
    sys.exit(0)  # outside this project: not ours to guard

if relative.parts[:1] != ("src",):
    sys.exit(0)  # only code under src/ is gated

approved = [
    spec.name for spec in (root / "specs").glob("*.md")
    if re.search(r"^status:\s*approved\b", spec.read_text(encoding="utf-8"), re.M)
]
if approved:
    sys.exit(0)

print(
    f"Blocked: {relative} is under src/ and no spec in specs/ has 'status: approved'. "
    "Run /inception <intent> first, and let the ac-reviewer subagent approve the spec.",
    file=sys.stderr,
)
sys.exit(2)
