# Claude Code Skills Catalog

This catalog lists all available skills organized by category. Use this reference to select appropriate skills for each step of an execution plan.

---

## Backend Development

### `backend-architect`
Expert backend architect specializing in scalable API design, microservices architecture, and distributed systems. Masters REST/GraphQL/gRPC APIs, event-driven architectures, service mesh patterns.
- **Use for**: Creating new backend services, API design, service boundary definition
- **Agent type**: `backend-development:backend-architect`

### `api-design-principles`
Master REST and GraphQL API design principles for intuitive, scalable APIs.
- **Use for**: Designing new APIs, reviewing API specifications, establishing API standards
- **Skill**: `backend-development:api-design-principles`

### `architecture-patterns`
Implement Clean Architecture, Hexagonal Architecture, and Domain-Driven Design patterns.
- **Use for**: Architecting complex backend systems, refactoring for maintainability
- **Skill**: `backend-development:architecture-patterns`

### `microservices-patterns`
Design microservices with service boundaries, event-driven communication, and resilience patterns.
- **Use for**: Building distributed systems, decomposing monoliths
- **Skill**: `backend-development:microservices-patterns`

### `graphql-architect`
Modern GraphQL with federation, performance optimization, and enterprise security.
- **Use for**: GraphQL architecture, schema design, performance optimization
- **Agent type**: `backend-development:graphql-architect`

### `temporal-python-pro`
Master Temporal workflow orchestration with Python SDK for durable workflows and saga patterns.
- **Use for**: Workflow design, microservice orchestration, long-running processes
- **Agent type**: `backend-development:temporal-python-pro`

### `workflow-orchestration-patterns`
Design durable workflows with Temporal for distributed systems.
- **Use for**: Building long-running processes, distributed transactions
- **Skill**: `backend-development:workflow-orchestration-patterns`

### `temporal-python-testing`
Test Temporal workflows with pytest, time-skipping, and mocking strategies.
- **Use for**: Implementing Temporal workflow tests, debugging test failures
- **Skill**: `backend-development:temporal-python-testing`

---

## Frontend & Mobile Development

### `frontend-developer`
Build React components, responsive layouts, client-side state management. Masters React 19, Next.js 15.
- **Use for**: Creating UI components, fixing frontend issues, implementing features
- **Agent type**: `frontend-mobile-development:frontend-developer`

### `frontend-design`
Create distinctive, production-grade frontend interfaces with high design quality.
- **Use for**: Building polished web components, pages, applications
- **Skill**: `example-skills:frontend-design`

### `mobile-developer`
React Native, Flutter, or native mobile apps with modern architecture patterns.
- **Use for**: Mobile features, cross-platform code, app optimization
- **Agent type**: `frontend-mobile-development:mobile-developer`

---

## JavaScript & TypeScript

### `javascript-pro`
Modern JavaScript with ES6+, async patterns, Node.js APIs.
- **Use for**: JavaScript optimization, async debugging, complex JS patterns
- **Agent type**: `javascript-typescript:javascript-pro`

### `typescript-pro`
Advanced TypeScript with generics, strict type safety, enterprise-grade patterns.
- **Use for**: TypeScript architecture, type inference, advanced typing patterns
- **Agent type**: `javascript-typescript:typescript-pro`

### `javascript-testing-patterns`
Testing with Jest, Vitest, Testing Library for unit, integration, and E2E tests.
- **Use for**: Writing tests, setting up test infrastructure, TDD/BDD workflows
- **Skill**: `javascript-typescript:javascript-testing-patterns`

### `typescript-advanced-types`
Master TypeScript's advanced type system including generics, conditional types, mapped types.
- **Use for**: Complex type logic, reusable type utilities, compile-time type safety
- **Skill**: `javascript-typescript:typescript-advanced-types`

### `modern-javascript-patterns`
ES6+ features: async/await, destructuring, spread, promises, modules, generators.
- **Use for**: Refactoring legacy code, implementing modern patterns
- **Skill**: `javascript-typescript:modern-javascript-patterns`

### `nodejs-backend-patterns`
Production-ready Node.js with Express/Fastify, middleware, error handling, auth.
- **Use for**: Creating Node.js servers, REST APIs, GraphQL backends
- **Skill**: `javascript-typescript:nodejs-backend-patterns`

---

## Quality Assurance & Testing

### `code-reviewer`
Elite code review with AI-powered analysis, security vulnerabilities, performance optimization.
- **Use for**: Code quality assurance, security scanning, configuration review
- **Agent type**: `code-documentation:code-reviewer` or `git-pr-workflows:code-reviewer`

### `test-automator`
AI-powered test automation with modern frameworks, self-healing tests.
- **Use for**: Testing automation, quality assurance, CI/CD integration
- **Agent type**: `full-stack-orchestration:test-automator`

### `tdd-orchestrator`
TDD orchestrator for red-green-refactor discipline and multi-agent workflow coordination.
- **Use for**: TDD implementation, test-driven development governance
- **Agent type**: `backend-development:tdd-orchestrator`

### `debugger`
Debugging specialist for errors, test failures, unexpected behavior.
- **Use for**: Investigating errors, fixing bugs, debugging issues
- **Agent type**: `debugging-toolkit:debugger`

---

## DevOps & Deployment

### `deployment-engineer`
Modern CI/CD pipelines, GitOps workflows, container security, platform engineering.
- **Use for**: CI/CD design, GitOps implementation, deployment automation
- **Agent type**: `full-stack-orchestration:deployment-engineer`

### `security-auditor`
DevSecOps, cybersecurity, compliance (GDPR/HIPAA/SOC2), vulnerability assessment.
- **Use for**: Security audits, DevSecOps, compliance implementation
- **Agent type**: `full-stack-orchestration:security-auditor`

### `performance-engineer`
Observability, optimization, OpenTelemetry, distributed tracing, Core Web Vitals.
- **Use for**: Performance optimization, observability, scalability
- **Agent type**: `full-stack-orchestration:performance-engineer`

### `dx-optimizer`
Developer Experience specialist for tooling, setup, and workflows.
- **Use for**: Setting up new projects, improving development friction
- **Agent type**: `debugging-toolkit:dx-optimizer`

---

## Documentation

### `docs-architect`
Comprehensive technical documentation from existing codebases.
- **Use for**: System documentation, architecture guides, technical deep-dives
- **Agent type**: `code-documentation:docs-architect` or `documentation-generation:docs-architect`

### `tutorial-engineer`
Step-by-step tutorials and educational content from code.
- **Use for**: Onboarding guides, feature tutorials, concept explanations
- **Agent type**: `code-documentation:tutorial-engineer` or `documentation-generation:tutorial-engineer`

### `api-documenter`
Master API documentation with OpenAPI 3.1, interactive docs, SDK generation.
- **Use for**: API documentation, developer portal creation
- **Agent type**: `documentation-generation:api-documenter`

### `reference-builder`
Exhaustive technical references and API documentation.
- **Use for**: API docs, configuration references, technical specifications
- **Agent type**: `documentation-generation:reference-builder`

### `mermaid-expert`
Mermaid diagrams for flowcharts, sequences, ERDs, architectures.
- **Use for**: Visual documentation, system diagrams, process flows
- **Agent type**: `documentation-generation:mermaid-expert`

---

## Document Processing

### `xlsx`
Spreadsheet creation, editing, analysis with formulas, formatting, visualization.
- **Use for**: Working with Excel files, data analysis in spreadsheets
- **Skill**: `document-skills:xlsx`

### `docx`
Document creation, editing with tracked changes, comments, formatting.
- **Use for**: Working with Word documents, professional document editing
- **Skill**: `document-skills:docx`

### `pptx`
Presentation creation, editing, layouts, speaker notes.
- **Use for**: Working with PowerPoint presentations
- **Skill**: `document-skills:pptx`

### `pdf`
PDF manipulation: extract text/tables, create, merge/split, handle forms.
- **Use for**: Processing PDF documents, filling forms
- **Skill**: `document-skills:pdf`

---

## Creative & Design

### `algorithmic-art`
Generative art using p5.js with seeded randomness.
- **Use for**: Creating algorithmic art, flow fields, particle systems
- **Skill**: `example-skills:algorithmic-art`

### `canvas-design`
Visual art in .png and .pdf using design philosophy.
- **Use for**: Creating posters, art, static design pieces
- **Skill**: `example-skills:canvas-design`

### `brand-guidelines`
Anthropic's official brand colors and typography.
- **Use for**: Applying brand styles, visual formatting
- **Skill**: `example-skills:brand-guidelines`

### `theme-factory`
Styling artifacts with preset themes or custom theme generation.
- **Use for**: Theming slides, docs, reports, landing pages
- **Skill**: `example-skills:theme-factory`

### `slack-gif-creator`
Animated GIFs optimized for Slack with size constraints.
- **Use for**: Creating GIF or emoji animations for Slack
- **Skill**: `example-skills:slack-gif-creator`

---

## Utilities & Tools

### `artifacts-builder`
Multi-component React artifacts for claude.ai using modern frontend technologies.
- **Use for**: Complex artifacts with state management, routing, shadcn/ui
- **Skill**: `example-skills:artifacts-builder`

### `mcp-builder`
Guide for creating MCP servers for LLM-external service integration.
- **Use for**: Building MCP servers for APIs in Python or TypeScript
- **Skill**: `example-skills:mcp-builder`

### `skill-creator`
Guide for creating effective skills for Claude Code.
- **Use for**: Creating or updating skills
- **Skill**: `example-skills:skill-creator`

### `internal-comms`
Resources for internal communications (status reports, updates, newsletters).
- **Use for**: Writing internal communications, reports, FAQs
- **Skill**: `example-skills:internal-comms`

### `webapp-testing`
Interacting with and testing local web applications using Playwright.
- **Use for**: Verifying frontend, debugging UI, capturing screenshots
- **Skill**: `example-skills:webapp-testing`

---

## General Purpose Agents

### `general-purpose`
General-purpose agent for complex, multi-step tasks.
- **Use for**: Research, code searching, when unsure which specific agent to use
- **Agent type**: `general-purpose`

### `Explore`
Fast agent for codebase exploration.
- **Use for**: Finding files by patterns, searching code, understanding codebase structure
- **Agent type**: `Explore`

### `Plan`
Fast agent for planning and exploration.
- **Use for**: Planning implementation, exploring codebase
- **Agent type**: `Plan`

---

## Quick Reference by Task

| Need | Primary Skill/Agent |
|------|---------------------|
| Build React component | `frontend-developer` |
| Create REST API | `backend-architect` |
| Write tests | `test-automator` |
| Fix bugs | `debugger` |
| Review code | `code-reviewer` |
| Optimize performance | `performance-engineer` |
| Security audit | `security-auditor` |
| Deploy application | `deployment-engineer` |
| Write documentation | `docs-architect` |
| Create diagrams | `mermaid-expert` |
| TypeScript types | `typescript-pro` |
| GraphQL API | `graphql-architect` |
