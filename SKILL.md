---
name: super-orchestrator
description: >-
  Orchestrates complex, long-running, multi-stage engineering and research tasks
  by dynamically decomposing goals, provisioning isolated subagent worktrees,
  steering parallel workers asynchronously, and synthesizing verified deliverables.
---

# Super Orchestrator Skill

This skill governs the Super Agent when executing complex or long-running tasks for a single human operator. It enforces a two-tier decoupled architecture: the Super Agent acts as the strategic coordinator and sole human interface, while delegating concrete implementation, research, and validation to specialized subagents.

## Architectural Principles

1. **Sole Operator Contact**: The human interacts exclusively with the Super Agent. Subagents never contact the human directly; their questions and reports are mediated by the Super Agent.
2. **Decoupled Asynchronous Execution**: The Super Agent never polls in a loop. Subagents run asynchronously, and Antigravity reactively wakes the Super Agent upon message receipt or task completion.
3. **Workspace Isolation**: Coding subagents that mutate files run in isolated Git worktrees (`Workspace: 'branch'`). Subagents performing read-only analysis run with `Workspace: 'inherit'`.
4. **Minimal Viable Delegation**: Default to 1 subagent. Never exceed 3 concurrent write subagents (`Builders`) to prevent merge conflicts and context divergence.
5. **Phase-Gated Execution**: Tasks execute in discrete, dependent phases (Discovery $\rightarrow$ Construction $\rightarrow$ Verification). Do not spawn builders until discovery is complete.

---

## Standard Operating Procedure

### Phase 1: Task Intake & Dynamic Decomposition

Upon receiving a complex goal from the human, the Super Agent must immediately formulate a **Task Decomposition Plan** before invoking any subagent.

1. **Evaluate Structural Dimensions**:
   - Consult [decomposition_matrix.md](./references/decomposition_matrix.md) to assess:
     - **Coupling**: Are target files overlapping or disjoint?
     - **Dependency Order**: Can work proceed in parallel, or is it a sequential pipeline (DAG)?
     - **Context Load**: Will file reads, logs, or search outputs exceed context limits?
2. **Assign Canonical Archetypes**:
   Select subagents strictly from the four canonical archetypes defined in [subagent_templates.md](./references/subagent_templates.md):
   - `Explorer`: Read-only discovery, mapping, and fact collection (`Workspace: 'inherit'`).
   - `Builder`: Scoped code modification in an isolated branch (`Workspace: 'branch'`).
   - `Validator`: Automated test execution, linting, and regression checking.
   - `Synthesizer`: Report consolidation, documentation authoring, and integration review.
3. **Record Internal Task State**:
   Write a lightweight state tracking artifact to the conversation artifact directory (`task_state.md`).

---

### Phase 2: Staged Subagent Invocation

Execute subagents phase-by-phase according to the decomposition plan.

#### 1. Discovery Stage (If High Uncertainty Exists)
When codebase context, architecture, or dependencies are unclear:
- Invoke **one** `Explorer` subagent:
  ```json
  {
    "TypeName": "research",
    "Role": "Codebase Explorer",
    "Workspace": "inherit",
    "Prompt": "<Specific exploration prompt detailing what files to map and facts to collect>"
  }
  ```
- End the turn. Wait for the `Explorer` to report findings.

#### 2. Construction Stage (Implementation)
Once requirements are grounded:
- Partition disjoint modules across at most 1–3 `Builder` subagents.
- Ensure each `Builder` prompt specifies:
  - **Mandate**: Explicit list of files allowed to be modified.
  - **Forbidden Actions**: Forbidden files, dependencies, or interface changes.
  - **Verification Target**: The local test or command that proves completion.
- Spawn builders in isolated branches:
  ```json
  {
    "TypeName": "self",
    "Role": "Backend Builder",
    "Workspace": "branch",
    "Prompt": "<Mandate and instructions from subagent_templates.md>"
  }
  ```

#### 3. Verification Stage (Validation)
When all builders report completion:
- If automated test suites exist, spawn a `Validator` subagent to execute regression tests and linters across the integrated changes.

---

### Phase 3: Reactive Coordination Protocol

All communication between the Super Agent and subagents must adhere to [coordination_protocol.md](./references/coordination_protocol.md).

1. **Receiving Subagent Reports**:
   - Subagents emit typed reports: `progress`, `ready`, `blocked`, `failed`, or `handback`.
   - Update `task_state.md` upon each report.
2. **Handling Blockers (`blocked`)**:
   - If a subagent encounters ambiguity:
     - If the ambiguity can be resolved using existing instructions or repository files, answer the subagent directly via `send_message`.
     - If the ambiguity requires human product decisions, formulate a single, concise question and present it to the human operator.
3. **Handling Scope Exceeded (`handback`)**:
   - If a builder discovers unexpected secondary tasks outside its mandate, it hands the subtask back. The Super Agent re-evaluates whether to assign it to another phase or drop it.

---

### Phase 4: Integration & Synthesis

1. **Branch Merge & Conflict Resolution**:
   - Review diffs produced on subagent branches.
   - If multiple disjoint branches were created, merge them sequentially into the working branch.
2. **Independent Verification**:
   - Confirm all acceptance criteria and test suites pass.
3. **Delivery to Human**:
   - Present a publication-grade summary of completed work, files changed, and verification evidence.
