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
| **Pi Agent (Personal AI Terminal Agent)** | `~/.pi/config.json` / CLI prompt | Subprocess / Worker Shell | Git worktrees via bash |

---

## 2. Platform-Specific Integration Instructions

### 2.1 Google Antigravity (`agy` / Antigravity IDE)

Google Antigravity natively loads skills from `~/.gemini/antigravity-cli/skills/` or workspace-level `.gemini/skills/`.

#### Setup:
1. Place the skill directory into your Antigravity skills repository:
   ```bash
   cp -r super-orchestrator ~/.gemini/antigravity-cli/skills/
   ```
2. In `~/.gemini/GEMINI.md` or workspace `AGENTS.md`, ensure the skill is indexed.

#### Execution Flow:
- The Super Agent acts as the human interface. When a complex task is received, it executes lazy dynamic binding via `references/decomposition_matrix.md`.
- **Subagent Invocation**: The Super Agent calls the native `invoke_subagent` tool:
  - For Explorers (discovery): `invoke_subagent(TypeName='research', Role='Codebase Explorer', Workspace='inherit', ...)`
  - For Builders (code generation): `invoke_subagent(TypeName='self', Role='Backend Builder', Workspace='branch', ...)` which automatically clones or branches an isolated workspace worktree.
- **Inter-Agent Messaging**: The child agents send progress and completion signals via `send_message`. Antigravity handles reactive wakeup automatically, so the Super Agent never polls in a loop.

---

### 2.2 Anthropic Claude Code

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

#### Execution Flow:
- Claude Code acts as the orchestrator in the main terminal turn.
- To spawn subagents, it invokes the built-in `Agent` tool (`Agent(prompt="...", subagent_type="...")`) or executes worker tasks in background sub-shells.
- Each subagent operates inside `.worktrees/<subtask>`, reads its mandate, modifies files, and records results in `task_state.md`.

---

### 2.3 OpenAI Codex / Codex CLI

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
   - Run `python scripts/plan_task.py validate-dag --plan-json plan.json` to verify dependencies.
   ```

#### Execution Flow:
- Codex CLI generates the execution DAG in `task_state.md`.
- It executes parallel subagents either through API-level agent calls (e.g., OpenAI Swarm / Assistants API) or by spawning parallel terminal worker sessions.
- After worker sessions report completion in `task_state.md`, the primary Codex orchestrator runs the test suite and merges the worktree branches sequentially.

---

### 2.4 Cline (VS Code Autonomous Coding Agent)

Cline executes autonomous coding workflows directly within VS Code using custom modes and `.clinerules`.

#### Setup:
1. Add `.clinerules` at the root of your project:
   ```markdown
   # Super Orchestrator Integration for Cline
   When assigned a large or complex task:
   1. Switch to 'Architect' mode to evaluate file coupling and generate `task_state.md`.
   2. Use terminal commands to create isolated worktrees for subtasks:
      `git worktree add -b agent/<feature> .worktrees/<feature>`
   3. Switch to 'Code' mode within the worktree directory to perform implementation.
   4. Run `python scripts/plan_task.py check-overlap --plan-json <plan.json>` before merging.
   5. Run full test suite in 'Test' mode before merging back to main branch.
   ```
2. If using Model Context Protocol (MCP), connect a Git Worktree MCP server to allow Cline to create and clean up worktree branches via structured tool calls.

#### Execution Flow:
- Cline switches between Architect Mode (Discovery & Planning) and Code Mode (isolated branch execution).
- This prevents uncommitted workspace pollution and ensures that long-running refactoring tasks do not disrupt ongoing user edits in VS Code.

---

### 2.5 GitHub Copilot & VS Code Copilot Workspace

GitHub Copilot Agent Mode in VS Code reads instructions from `.github/copilot-instructions.md`.

#### Setup:
1. Create `.github/copilot-instructions.md`:
   ```markdown
   # Task Orchestration Rules
   - When asked to perform complex, multi-file engineering tasks, act as a Super Orchestrator.
   - Decompose tasks into Discovery (Explorer), Construction (Builder), and Verification (Validator).
   - Document active phases in `task_state.md`.
   - Restrict Builders to disjoint directory trees to avoid merge conflicts.
   - For parallel modifications, mandate branch isolation:
     `git worktree add -b agent/<feature> .worktrees/<feature>`
   ```

#### Execution Flow:
- In Copilot Agent Mode (`@workspace`), the agent creates the structured plan in `task_state.md`.
- It executes modifications across isolated branches, running verification commands in the terminal panel before suggesting pull request generation or branch integration.

---

### 2.6 OpenCode (OpenCodeInterpreter & Terminal Coding Agents)

OpenCode is an open-source terminal coding assistant designed for local and remote command execution.

#### Setup:
1. Create an `opencode.json` configuration in the project root:
   ```json
   {
     "system_prompt_file": "path/to/super-orchestrator/SKILL.md",
     "agent_mode": "orchestrator",
     "worktree_root": ".worktrees"
   }
   ```
2. Or initialize OpenCode with system context:
   ```bash
   opencode --system-prompt "$(cat path/to/super-orchestrator/SKILL.md)"
   ```

#### Execution Flow:
- OpenCode parses the human objective, checks file disjointness using `plan_task.py`, and initializes `task_state.md`.
- It launches subagents as separate CLI processes:
  ```bash
  opencode --task "Build database schema" --workdir .worktrees/db-migration
  ```
- Sub-processes emit JSON progress events; upon completion, OpenCode executes the validator test pass and removes the worktree.

---

### 2.7 Meta Muse (Autonomous Code Generation Agent)

Meta Muse provides automated codebase development and maintenance through tool-augmented execution queues.

#### Setup:
1. Register `super-orchestrator` in Muse's agent capabilities manifest:
   ```yaml
   name: super_orchestrator
   description: "Decomposes long-horizon engineering tasks into isolated worktree subagents"
   protocol: path/to/super-orchestrator/SKILL.md
   max_concurrent_builders: 3
   ```
2. Configure Muse's environment policy to enforce zero overlapping write access.

#### Execution Flow:
- Muse analyzes repository graphs to calculate file coupling metrics.
- It provisions containerized or branch-isolated workspaces for each task node in the DAG.
- Worker agents write status logs to `task_state.md`, and the supervisor agent merges branches strictly in topological order.

---

### 2.8 xAI Grok Bot (Grok CLI & Coding Assistant)

xAI Grok Bot operates as an autonomous terminal assistant for codebase analysis, generation, and testing.

#### Setup:
1. Provide the orchestration skill via CLI injection:
   ```bash
   grok --prompt-file path/to/super-orchestrator/SKILL.md
   ```
2. In the project root, configure workspace instructions:
   ```markdown
   ## Grok Autonomous Orchestrator Instructions
   - Always run Discovery with read-only tools before modifying code.
   - For tasks involving >3 files, establish task_state.md.
   - Execute parallel builds in detached background processes (`nohup` / `Start-Job`).
   - If a build or test exceeds 5 seconds, detach and monitor state via task_state.md.
   ```

#### Execution Flow:
- Grok analyzes architecture and drafts the phase breakdown.
- It spins up background workers for compilation and test execution while remaining available for operator queries.
- Once all worker states transition to `ready`, Grok validates regression suites and completes the task.

---

### 2.9 Pi Agent (Inflection / Personal AI Terminal Agent)

Pi Agent is a conversational personal assistant designed to pair closely with a single human user.

#### Setup:
1. Configure Pi Agent's role profile in `~/.pi/config.json`:
   ```json
   {
     "role": "Super Agent Orchestrator",
     "skill_path": "path/to/super-orchestrator",
     "contract_file": "task_state.md",
     "single_operator_mode": true
   }
   ```

#### Execution Flow:
- **Human-Centric Interface**: The human operator gives free-form, evolving directions ("Refactor the authentication flow to support Passkeys and OAuth2").
- **Lazy Binding**: Pi Agent analyzes the request against the 3-axis matrix, formats the contract into `task_state.md`, and selects the required subagent archetypes.
- **Decoupled Delegation**: Pi Agent delegates tactical code generation to local worker processes or CLI tools without spamming the operator with raw build logs.
- **Milestone Feedback**: When worker subagents complete phases, Pi Agent delivers concise, high-level summaries and verification reports back to the user.

---

## 3. Universal Orchestration Invariants Across All Agents

Regardless of which underlying agent runtime is active, all implementations must uphold five universal invariants:

1. **The State Contract Is Markdown**: Always write to `task_state.md` in the workspace. Any agent capable of reading and writing text can parse and update this contract.
2. **No Synchronous Turn Blocking**: An orchestrator agent must never execute blocking operations that prevent it from receiving human interrupts or steering commands.
3. **Strict Physical Isolation**: Subagents modifying code must work in separate Git branches or worktrees (`.worktrees/<name>`). Never let two concurrent subagents write to the same working directory.
4. **The Rule of Three Ceiling**: Never run more than 3 concurrent write subagents simultaneously.
5. **Phase-Gated Transitions**: Always complete Discovery before launching Construction; always complete Construction before launching Verification.
