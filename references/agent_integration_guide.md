# Multi-Agent Integration Guide: Using `super-orchestrator` Across Coding Agents

This guide documents how heterogeneous coding agent harnesses and platforms can adopt, ingest, and execute the `super-orchestrator` workflow.

While originally designed for Google Antigravity (`agy`), the orchestration protocol is **agent-agnostic**: it relies on standard Git worktrees, structured Markdown state files (`task_state.md`), and typed JSON inter-agent messages.

---

## 1. Cross-Platform Compatibility Matrix

| Coding Agent / Platform | Integration Hook | Subagent Execution Primitive | Workspace Isolation Method |
| :--- | :--- | :--- | :--- |
| **Google Antigravity (`agy`)** | `skills/super-orchestrator/SKILL.md` | Native `invoke_subagent` | `Workspace: 'branch'` |
| **Anthropic Claude Code** | `.claude/skills/` or `CLAUDE.md` | `Agent` tool / Task Spawning | `git worktree add` via bash |
| **OpenAI Codex / Codex CLI** | `AGENTS.md` / Custom Instructions | Sub-process invocation / Swarm | Git worktrees via terminal |
| **Cline (VS Code Extension)** | `.clinerules` / `.cline/skills/` | Custom Modes (Architect $\rightarrow$ Code) | MCP Worktree Server or Git CLI |
| **VS Code Copilot / Copilot Workspace** | `.github/copilot-instructions.md` | Multi-File Task Planner / Agent Mode | Git branch isolation |
| **OpenCode / OpenCodeInterpreter** | `opencode.json` / System Prompt | Process fork / Sub-shell workers | Git worktrees via shell |
| **Meta Muse / Code Agent** | Tool Manifest / Agent Config | Asynchronous Task Queues | Containerized / Branch workspaces |
| **xAI Grok Bot / Grok CLI** | System Prompt / Runbook markdown | Autonomous background jobs | Worktree branches via shell |

---

## 2. Platform-Specific Integration Instructions

### 2.1 Anthropic Claude Code

Claude Code supports custom skills via its memory and runbook directory structure.

#### Setup:
1. Copy `super-orchestrator` to Claude Code's skill directory:
   ```bash
   mkdir -p ~/.claude/skills/super-orchestrator
   cp -r * ~/.claude/skills/super-orchestrator/
   ```
2. In `~/.claude/CLAUDE.md` (or your project's `CLAUDE.md`), add the directive:
   ```markdown
   When executing multi-stage or long-running tasks, activate the super-orchestrator protocol:
   1. Read ~/.claude/skills/super-orchestrator/SKILL.md.
   2. Maintain task state in task_state.md.
   3. Isolate code modifications using git worktrees: `git worktree add -b agent/<subtask> .worktrees/<subtask>`.
   4. Enforce the Rule of Three: max 3 concurrent worktree branches.
   ```
3. **Execution**:
   Claude Code invokes subagents using its built-in `Agent` tool or runs background shell sessions, communicating via `task_state.md`.

---

### 2.2 OpenAI Codex / Codex CLI

OpenAI Codex and CLI agents read instructions from `AGENTS.md` or repository prompt instructions.

#### Setup:
1. Append the orchestrator runbook to `AGENTS.md`:
   ```markdown
   ## Long-Horizon Multi-Agent Orchestration
   For complex refactoring, multi-module features, or comprehensive test suites:
   - Follow the 3-axis task decomposition matrix in `references/decomposition_matrix.md`.
   - Before executing code edits, generate a structured decomposition plan in `task_state.md`.
   - For every parallel worker, provision a separate Git worktree under `.worktrees/`.
   - Never allow parallel write workers to touch overlapping files.
   ```
2. Codex executes parallel subagents either through API-level agent calls (e.g., OpenAI Swarm / Assistants API) or by spawning parallel terminal sessions using `scripts/plan_task.py`.

---

### 2.3 Cline (VS Code Autonomous Coding Agent)

Cline executes autonomous coding workflows directly within VS Code using custom modes and `.clinerules`.

#### Setup:
1. Add `.clinerules` at the root of your project:
   ```markdown
   # Super Orchestrator Integration for Cline
   When assigned a large or complex task:
   1. Switch to 'Architect' mode to evaluate file coupling and generate `task_state.md`.
   2. Use terminal commands to create isolated worktrees for subtasks:
      `git worktree add -b agent/<feature> .worktrees/<feature>`
   3. Execute implementation within the worktree directory.
   4. Run `python scripts/plan_task.py check-overlap --plan-json <plan.json>` before merging.
   ```
2. If using Model Context Protocol (MCP), connect a Git Worktree MCP server to allow Cline to create and clean up worktree branches via structured tool calls.

---

### 2.4 GitHub Copilot & VS Code Copilot Workspace

GitHub Copilot Agent Mode in VS Code reads instructions from `.github/copilot-instructions.md`.

#### Setup:
1. Create `.github/copilot-instructions.md`:
   ```markdown
   # Task Orchestration Rules
   - When asked to perform complex, multi-file engineering tasks, act as a Super Orchestrator.
   - Decompose tasks into Discovery (Explorer), Construction (Builder), and Verification (Validator).
   - Document active phases in `task_state.md`.
   - Restrict Builders to disjoint directory trees to avoid merge conflicts.
   ```
2. Copilot's `@workspace` agent uses this protocol to plan edits across discrete milestones and run verification commands sequentially.

---

### 2.5 OpenCode, Meta Muse, and Grok Bot

For open-source and frontier CLI agents (such as OpenCode, Meta Muse, or xAI Grok Bot):

1. **System Prompt Injection**: Pass `SKILL.md` as context at initialization:
   ```bash
   opencode --system-prompt "$(cat path/to/super-orchestrator/SKILL.md)"
   ```
2. **Worktree Isolation via Bash**: Because all terminal coding agents have access to shell tools, they can execute the core isolation pattern natively:
   ```bash
   # Provision worktree
   git worktree add -b agent/auth-refactor .worktrees/auth-refactor
   
   # Execute subagent in worktree
   cd .worktrees/auth-refactor && run_task
   
   # Verify and clean up
   cd ../.. && git merge agent/auth-refactor && git worktree remove .worktrees/auth-refactor
   ```

---

## 3. Universal Orchestration Invariants Across All Agents

Regardless of which underlying agent runtime is active, all implementations must uphold five universal invariants:

1. **The State Contract Is Markdown**: Always write to `task_state.md` in the workspace. Any agent capable of reading and writing text can parse and update this contract.
2. **No Synchronous Turn Blocking**: An orchestrator agent must never execute blocking operations that prevent it from receiving human interrupts or steering commands.
3. **Strict Physical Isolation**: Subagents modifying code must work in separate Git branches or worktrees (`.worktrees/<name>`). Never let two concurrent subagents write to the same working directory.
4. **The Rule of Three Ceiling**: Never run more than 3 concurrent write subagents simultaneously.
5. **Phase-Gated Transitions**: Always complete Discovery before launching Construction; always complete Construction before launching Verification.
