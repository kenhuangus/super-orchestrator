#!/usr/bin/env python3
"""Task Planning & Workspace Disjointness Utility for Super Orchestrator.

Provides CLI helpers to inspect workspace coupling, check for overlapping file paths
across planned subtasks, and manage worktree branches cleanly.
"""

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys


def parse_args():
    parser = argparse.ArgumentParser(description="Super Orchestrator Task Planner Helper")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Coupling / Overlap Check
    overlap = subparsers.add_parser("check-overlap", help="Check if planned file lists overlap")
    overlap.add_argument("--plan-json", type=str, required=True, help="Path to JSON file defining planned subagent file targets")

    # Worktree Status
    branches = subparsers.add_parser("list-worktrees", help="List active git worktrees")

    return parser.parse_args()


def check_overlap(plan_path: str):
    """Check whether planned subagent file paths conflict."""
    path = Path(plan_path)
    if not path.exists():
        print(json.dumps({"error": f"Plan file not found: {plan_path}"}))
        sys.exit(1)

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        print(json.dumps({"error": f"Invalid JSON in plan file: {e}"}))
        sys.exit(1)

    subtasks = data.get("subtasks", [])
    seen_files = {}
    conflicts = []

    for task in subtasks:
        name = task.get("name", "unnamed")
        targets = task.get("target_files", [])
        for file in targets:
            norm_file = os.path.normpath(file)
            if norm_file in seen_files:
                conflicts.append({
                    "file": norm_file,
                    "task1": seen_files[norm_file],
                    "task2": name
                })
            else:
                seen_files[norm_file] = name

    if conflicts:
        print(json.dumps({
            "status": "conflict",
            "message": "Overlapping files detected. Parallel write agents cannot touch identical files.",
            "conflicts": conflicts
        }, indent=2))
        sys.exit(2)
    else:
        print(json.dumps({
            "status": "ok",
            "message": "All subtask targets are disjoint. Safe for parallel branch execution.",
            "subtask_count": len(subtasks)
        }, indent=2))


def list_worktrees():
    """List git worktrees using git worktree list."""
    try:
        result = subprocess.run(["git", "worktree", "list", "--porcelain"], capture_output=True, text=True, check=True)
    except subprocess.CalledProcessError as e:
        print(json.dumps({"error": f"Git command failed: {e.stderr}"}))
        sys.exit(1)
    except FileNotFoundError:
        print(json.dumps({"error": "git executable not found on PATH"}))
        sys.exit(1)

    worktrees = []
    current = {}
    for line in result.stdout.splitlines():
        if line.startswith("worktree "):
            current = {"path": line.split(" ", 1)[1]}
        elif line.startswith("branch "):
            current["branch"] = line.split(" ", 1)[1]
            worktrees.append(current)
            current = {}
        elif not line.strip() and current:
            worktrees.append(current)
            current = {}

    if current:
        worktrees.append(current)

    print(json.dumps({"status": "ok", "worktrees": worktrees}, indent=2))


def main():
    args = parse_args()
    if args.command == "check-overlap":
        check_overlap(args.plan_json)
    elif args.command == "list-worktrees":
        list_worktrees()


if __name__ == "__main__":
    main()
