#!/usr/bin/env python3
"""
Activity Logger — PostToolUse hook for Claude Code.
Logs Write, Edit, Bash actions to claude-activity.log.
Fast append-only, never blocks Claude.
"""

import json
import os
import sys
from datetime import datetime

# Configure your log file path
LOG_FILE = os.path.expanduser(
    "~/.claude/memory/claude-activity.log"
)


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        print(json.dumps({"continue": True}))
        return

    tool_name = data.get("tool_name", "")
    tool_input = data.get("tool_input", {})
    tool_result = data.get("tool_result", {})
    session_id = data.get("session_id", "unknown")

    # Only log Write, Edit, Bash
    if tool_name not in ("Write", "Edit", "Bash"):
        print(json.dumps({"continue": True}))
        return

    timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    # Extract target and detail based on tool type
    if tool_name == "Write":
        target = tool_input.get("file_path", "?")
        detail = "created"
    elif tool_name == "Edit":
        target = tool_input.get("file_path", "?")
        detail = "modified"
    elif tool_name == "Bash":
        command = tool_input.get("command", "")
        # Truncate long commands
        target = command[:120] if len(command) > 120 else command
        # Sanitize pipe chars in command to avoid breaking log format
        target = target.replace("|", "\u00a6")
        exit_code = ""
        if isinstance(tool_result, dict):
            exit_code = tool_result.get("exitCode", tool_result.get("exit_code", ""))
        detail = f"exit_code={exit_code}" if exit_code != "" else "executed"
    else:
        print(json.dumps({"continue": True}))
        return

    line = f"{timestamp}|{session_id}|{tool_name}|{target}|{detail}\n"

    try:
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "a") as f:
            f.write(line)
    except Exception:
        pass  # Never block Claude

    print(json.dumps({"continue": True}))


if __name__ == "__main__":
    main()
