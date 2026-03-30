---
name: skill-orchestrator
description: "Breaks complex coding tasks into subtasks, assigns each to the best available Claude Code skill, and coordinates execution sequentially or via sub-agents. Use when the user asks to plan a multi-step project, decompose a feature into tasks, coordinate 3+ skills, or wants a structured build plan before coding."
---

# Skill Orchestrator

Decomposes complex programming tasks into structured execution plans, assigns the optimal skill to each step, and coordinates execution in manual (step-by-step) or delegated (parallel sub-agent) mode.

## Workflow

### 1. Analyze Task

Parse the request to identify:
- Core objective, technical domains (frontend, backend, database, etc.)
- Complexity (simple / moderate / complex)
- Dependencies between subtasks

Load [references/skills_catalog.md](references/skills_catalog.md) and match subtasks to available skills.

### 2. Create Plan File

Save to `EXECUTION_PLAN.md` (or `EXECUTION_PLAN_[feature].md`) using this format:

```markdown
# Execution Plan: [Task Name]

## Overview
- **Objective**: [Goal]
- **Complexity**: [Simple/Moderate/Complex]
- **Execution Mode**: [Manual/Delegated] — [reason]

## Steps

### Step 1: [Name]
- [ ] **Skill**: `[skill-name]` — [reason]
- **Action**: [What to do]
- **Inputs/Outputs**: [What it needs → what it produces]
- **Dependencies**: None

### Step 2: [Name]
- [ ] **Skill**: `[skill-name]`
- **Action**: [What to do]
- **Dependencies**: Step 1
```

Mark steps `[x]` as they complete. Add notes on issues encountered.

### 3. Select Execution Mode

Ask the user:
> "Plan ready. Execute in **manual mode** (step-by-step with review) or **delegated mode** (sub-agents in parallel)?"

See [references/orchestration_patterns.md](references/orchestration_patterns.md) for mode selection guidance.

### 4. Execute

**Manual mode:** For each step, read the plan, activate the **exact skill name** listed, execute, mark `[x]`, report outputs. If a skill is unavailable, notify the user — do not substitute.

**Delegated mode:** Identify parallelizable steps (no mutual dependencies), launch sub-agents with explicit instructions including the exact skill name. Collect results, update plan.

**CRITICAL:** Always use the exact skill name from the plan. The plan file is the source of truth for skill selection.

### 5. Validate

After all steps complete, verify:
- All plan checkboxes marked `[x]`
- Outputs exist and meet success criteria
- Quality assurance steps (testing, review) passed

If a step fails: report details, propose a fix or alternative, get user confirmation before continuing.

## Skill Selection Quick Reference

| Task Type | Primary Skills | Supporting Skills |
|-----------|---------------|-------------------|
| New feature | `frontend-developer`, `backend-architect` | `typescript-pro`, `test-automator` |
| Bug fix | `debugger` | `code-reviewer` |
| Refactoring | `code-reviewer` | `typescript-pro`, `performance-engineer` |
| API development | `backend-architect`, `api-design-principles` | `graphql-architect` |
| Testing | `test-automator`, `tdd-orchestrator` | `javascript-testing-patterns` |
| Security | `security-auditor` | `code-reviewer` |

Full catalog: [references/skills_catalog.md](references/skills_catalog.md)
