# Inter-Agent Coordination Protocol

This document defines the structured message contracts used for communication between the Super Agent and its subagents.

---

## 1. Protocol Architecture

Communication between the Super Agent and subagents relies on three Antigravity primitives:
1. `invoke_subagent`: Spawns the subagent with its initial mandate and context.
2. `send_message`: Sends steering instructions, clarifications, or cancellation signals.
3. Subagent Final Message / Text Output: Delivers status reports, deliverables, and blockers back to the Super Agent.

---

## 2. Subagent Status Report Format

Every subagent must conclude its turns or send interim progress using the following structured format (rendered as JSON or Markdown block):

```json
{
  "protocol": "super-orchestrator/v1",
  "task_id": "TASK-AUTH-01",
  "state": "progress | ready | blocked | failed | handback",
  "summary": "Implemented JWT token validation in auth middleware; local unit tests passed.",
  "deliverables": [
    "src/middleware/auth.py",
    "tests/test_auth.py"
  ],
  "verification": {
    "command": "pytest tests/test_auth.py",
    "exit_code": 0,
    "passed": 8,
    "failed": 0
  },
  "question": null,
  "handback_reason": null
}
```

### State Definitions

| State | Meaning | Super Agent Action |
| :--- | :--- | :--- |
| **`progress`** | Work is actively running; interim checkpoint reached. | Records progress in `task_state.md`. Turn resumes. |
| **`ready`** | Work completed successfully; local verification passed. | Records completion; stages branch for merge or validation. |
| **`blocked`** | Subagent cannot proceed without external clarification. | Evaluates `question`. Answers directly or prompts human operator. |
| **`failed`** | Execution failed due to unexpected error, build crash, or unrecoverable bug. | Analyzes error trace; decides whether to retry with adjusted mandate or reassign. |
| **`handback`** | Task requires changes outside the subagent's allowed mandate boundary. | Accepts handback; prevents unauthorized scope expansion; re-plans scope. |

---

## 3. Super Agent Steering Message Format

When the Super Agent redirects or clarifies a running subagent via `send_message`:

```json
{
  "protocol": "super-orchestrator/v1",
  "task_id": "TASK-AUTH-01",
  "action": "continue | redirect | abort",
  "clarification": "Use the RS256 algorithm and read public keys from config.jwt_public_key.",
  "mandate_amendment": {
    "add_allowed_files": ["src/config/jwt.py"],
    "remove_allowed_files": []
  }
}
```

---

## 4. Reactive State Tracking (`task_state.md`)

The Super Agent maintains a live markdown artifact in the conversation artifact directory to track running subagents:

```markdown
# Super Orchestrator Live Task State

- **Goal**: Add OAuth2 Authentication
- **Phase**: 2 of 3 (Construction)
- **Status**: Running

## Subagent Fleet

| Subagent ID | Role | Archetype | Workspace | Status | Target Scope |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `conv-101` | Backend Auth | `Builder` | `branch: agent/backend-auth` | `ready` | `src/auth/*` |
| `conv-102` | UI Login | `Builder` | `branch: agent/ui-login` | `running` | `ui/src/login/*` |
| `conv-103` | OAuth Discovery | `Explorer` | `inherit` | `ready` | RFC specs |

## Blockers & Queries
- None pending.
```
