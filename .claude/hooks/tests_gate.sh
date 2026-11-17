#!/bin/bash
# Stop gate: Claude may not finish while the tests fail.
# Exit 2 sends stderr back to Claude and keeps it working. Exit 0 lets it stop.

input=$(cat)

# If this hook already sent Claude back once, let it stop, or it would loop forever.
if echo "$input" | grep -Eq '"stop_hook_active"[[:space:]]*:[[:space:]]*true'; then
  exit 0
fi

cd "${CLAUDE_PROJECT_DIR:-.}" || exit 0

if [ -x .venv/bin/pytest ]; then
  output=$(.venv/bin/pytest -q 2>&1)
else
  output=$(python3 -m pytest -q 2>&1)
fi
status=$?

if [ "$status" -ne 0 ]; then
  echo "Tests are failing, so the work is not done. Fix them before finishing:" >&2
  echo "$output" | tail -n 20 >&2
  exit 2
fi
exit 0
