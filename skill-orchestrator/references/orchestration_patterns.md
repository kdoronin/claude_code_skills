# Orchestration Patterns

Common patterns for combining skills effectively in execution plans.

---

## Mode Selection Patterns

### When to Use Manual Mode

| Scenario | Reason |
|----------|--------|
| Security-critical code | Requires careful review at each step |
| Learning new codebase | User wants to understand the process |
| Exploratory work | Requirements may change based on findings |
| Complex decision points | User input needed between steps |
| Small tasks (< 5 steps) | Overhead of delegation not worth it |
| First-time workflows | Build understanding before automating |

### When to Use Delegated Mode

| Scenario | Reason |
|----------|--------|
| Parallelizable work | Multiple independent components |
| Repetitive patterns | Same task across multiple files |
| Large refactoring | Many similar changes needed |
| Well-defined specs | Clear inputs and outputs |
| Time-sensitive | Parallel execution saves time |
| Boilerplate generation | Predictable, low-risk code |

---

## Common Skill Combinations

### Full-Stack Feature Development

```
1. backend-architect       → Design API and data model
2. typescript-pro         → Define types and interfaces
3. nodejs-backend-patterns → Implement backend logic
4. frontend-developer     → Build UI components
5. test-automator         → Write tests
6. code-reviewer          → Review implementation
```

**Parallelization**: Steps 3 and 4 can run in parallel after step 2.

### Bug Fix Workflow

```
1. debugger              → Investigate and locate issue
2. [domain skill]        → Implement fix (frontend/backend/etc)
3. test-automator        → Add regression test
4. code-reviewer         → Verify fix quality
```

**Mode**: Manual recommended - debugging requires iterative investigation.

### API Development

```
1. api-design-principles  → Design API contract
2. backend-architect      → Plan implementation architecture
3. graphql-architect      → (if GraphQL) Schema design
   OR nodejs-backend-patterns → (if REST) Route implementation
4. typescript-pro         → Type definitions
5. api-documenter         → Generate API documentation
6. test-automator         → API integration tests
7. security-auditor       → Security review
```

**Parallelization**: Steps 5, 6, 7 can run in parallel after implementation.

### Performance Optimization

```
1. performance-engineer   → Profile and identify bottlenecks
2. code-reviewer          → Review hot paths
3. [implementation skill] → Apply optimizations
4. performance-engineer   → Verify improvements
5. test-automator         → Ensure no regressions
```

**Mode**: Manual recommended - optimization requires measurement feedback.

### Security Hardening

```
1. security-auditor       → Initial security assessment
2. code-reviewer          → Review security-critical code
3. [fix implementation]   → Apply security fixes
4. security-auditor       → Verify fixes
5. test-automator         → Security test suite
```

**Mode**: Manual required - security decisions need human oversight.

### Documentation Sprint

```
1. docs-architect         → Architecture documentation
2. api-documenter         → API reference documentation
3. tutorial-engineer      → Getting started guides
4. mermaid-expert         → System diagrams
```

**Parallelization**: All steps can run in parallel (independent outputs).

### Code Refactoring

```
1. code-reviewer          → Identify refactoring opportunities
2. architecture-patterns  → Design target architecture
3. typescript-pro         → Update types and interfaces
4. [domain skill]         → Implement refactoring
5. test-automator         → Update and verify tests
6. code-reviewer          → Final review
```

**Mode**: Manual for complex refactoring, delegated for simple patterns.

### New Project Setup

```
1. dx-optimizer           → Configure dev environment
2. deployment-engineer    → Setup CI/CD pipeline
3. backend-architect      → Initial backend structure
4. frontend-developer     → Initial frontend structure
5. test-automator         → Test infrastructure
6. docs-architect         → Initial documentation
```

**Parallelization**: Steps 3, 4, 5, 6 can run after steps 1, 2.

---

## Dependency Patterns

### Linear Dependencies

```
A → B → C → D
```
Each step depends on the previous. Must execute sequentially.

**Example**: Design → Implement → Test → Review

### Parallel with Merge

```
A → B ──┐
        ├→ D
A → C ──┘
```
Steps B and C can run in parallel after A, both needed for D.

**Example**: After architecture design, frontend and backend can be built in parallel, then integrated.

### Diamond Pattern

```
    ┌→ B ─┐
A ──┤     ├→ D
    └→ C ─┘
```
Common in component development where A produces specs, B and C implement independently, D integrates.

### Fork-Join Pattern

```
    ┌→ B ─┐
    │     │
A ──┼→ C ─┼→ E
    │     │
    └→ D ─┘
```
Multiple independent tasks spawned from one source, all joined before proceeding.

**Example**: After API design, multiple endpoint implementations run in parallel, then all get integrated testing.

---

## Error Handling Patterns

### Retry Pattern

When a step fails:
1. Analyze failure cause
2. If transient → retry with same skill
3. If skill mismatch → try alternative skill
4. If fundamental issue → escalate to user

### Fallback Pattern

```
Primary: typescript-pro
Fallback: javascript-pro
Last resort: general-purpose
```

If specialized skill unavailable or fails, fall back to more general option.

### Checkpoint Pattern

For long workflows:
1. Mark completion of each major phase
2. If failure occurs, restart from last checkpoint
3. Report partial progress to user

---

## Optimization Strategies

### Minimize Context Switching

Group related steps together:
```
GOOD: Backend design → Backend implement → Backend test → Frontend design → Frontend implement
BAD: Backend design → Frontend design → Backend implement → Frontend implement
```

### Maximize Parallelism

Identify independent branches early:
```
After requirements:
  Branch 1: Backend (architect → implement → test)
  Branch 2: Frontend (design → implement → test)
  Merge: Integration testing
```

### Skill Reuse

If same skill needed multiple times, batch operations:
```
GOOD:
  typescript-pro: Define all types
  frontend-developer: Build all components

BAD:
  typescript-pro: Type for A
  frontend-developer: Component A
  typescript-pro: Type for B
  frontend-developer: Component B
```

---

## Quality Gates

### Required Reviews

| Change Type | Required Review |
|-------------|-----------------|
| Security-related | `security-auditor` |
| API changes | `code-reviewer` |
| Performance-critical | `performance-engineer` |
| Public-facing | `code-reviewer` + manual |

### Test Requirements

| Change Type | Test Requirement |
|-------------|------------------|
| New feature | Unit + Integration tests |
| Bug fix | Regression test |
| Refactoring | Existing tests must pass |
| Performance | Benchmark comparison |

---

## Communication Templates

### Plan Presentation

```markdown
## Execution Plan: [Name]

### Overview
[Brief description of what will be built]

### Approach
- **Mode**: [Manual/Delegated]
- **Reason**: [Why this mode]
- **Steps**: [Count]
- **Parallelizable**: [Which steps]

### Steps
[Numbered list with skills]

### Quality Gates
[Required reviews/tests]

Ready to proceed?
```

### Progress Report

```markdown
## Progress Update

### Completed
- [x] Step 1: [Name] (skill: X)
- [x] Step 2: [Name] (skill: Y)

### In Progress
- [ ] Step 3: [Name] (skill: Z) - [status details]

### Remaining
- [ ] Step 4: [Name]

### Issues/Blockers
[Any problems encountered]
```

### Completion Report

```markdown
## Execution Complete

### Summary
[What was accomplished]

### Artifacts Produced
- [List of files/outputs]

### Quality Checks
- Tests: [Pass/Fail]
- Review: [Done/Pending]

### Next Steps (if any)
[Recommendations]
```
