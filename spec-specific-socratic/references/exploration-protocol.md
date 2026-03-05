# Codebase Exploration Protocol

Systematic approach to understanding a codebase before interviewing about a feature. Use Glob, Read, and Grep for static exploration. Bash may also be used to run frameworks, simulators, or target applications when the codebase includes them (see SKILL.md rule 10).

## Decision Tree

```
Start
  │
  ├─ 1. Map structure (Glob)
  │    └─ Is it large (>200 files)?
  │         ├─ Yes → Use Explore agent for deep investigation
  │         └─ No  → Continue manually
  │
  ├─ 2. Read bootstrapping files
  │    └─ Found README/CLAUDE.md/config?
  │         ├─ Yes → Extract build commands, conventions, architecture
  │         └─ No  → Infer from directory names and file extensions
  │
  ├─ 3. Identify layers
  │    └─ Which layers are present?
  │         (entry points, core logic, data, config, tests, build, docs)
  │
  ├─ 4. Trace closest feature
  │    └─ Found something similar to the proposed feature?
  │         ├─ Yes → Trace it end-to-end through layers
  │         └─ No  → Trace any representative feature for patterns
  │
  └─ 5. Write exploration document
```

## Step 1: Map Structure

```
Glob: **/*           → top-level overview (limit depth if huge)
Glob: **/README*     → documentation files
Glob: **/CLAUDE.md   → Claude Code instructions
Glob: **/*.config.*  → configuration files
Glob: **/test*/**    → test structure
```

**Identify:**
- Primary language(s) and framework(s)
- Directory organization pattern (by feature? by layer? hybrid?)
- Approximate size (file count, key directories)

## Step 2: Read Bootstrapping Files

**Priority order:**
1. `CLAUDE.md` — if present, this is the most authoritative source
2. `README.md` / `README.rst` — setup, architecture overview
3. `pyproject.toml` / `package.json` / `Cargo.toml` — dependencies, scripts, entry points
4. `Makefile` / `justfile` / `taskfile.yml` — build commands
5. `.env.example` / `config/` — configuration patterns
6. `src/*//__init__.py` or `src/index.*` — entry points

**Extract:**
- How to build and run
- Key dependencies
- Architecture overview (if documented)
- Coding conventions

## Step 3: Identify Layers

Map the codebase to these standard layers (not all will be present):

| Layer | What to look for |
|-------|-----------------|
| **Entry points** | CLI commands, API routes, main files, event handlers |
| **Application logic** | Orchestrators, services, use cases, controllers |
| **Domain/core** | Models, entities, value objects, business rules |
| **Data access** | Repositories, ORM models, database clients, file I/O |
| **Infrastructure** | External service clients, message queues, caches |
| **Configuration** | Config files, env vars, feature flags |
| **Tests** | Test directories, fixtures, factories, mocks |
| **Build/deploy** | CI/CD, Docker, scripts, package manifests |
| **Documentation** | Docs directory, API specs, architecture decision records |

**For each layer found:**
- Note the directory path
- Identify 1-2 key files
- Note any conventions (naming, patterns, base classes)

## Step 4: Trace Closest Feature

Find the existing feature most similar to what the user wants to build, then trace it through the codebase.

**Finding the closest feature:**
```
Grep: keywords related to the proposed feature
Grep: similar domain concepts (e.g., if adding "caching", search for existing cache usage)
Read: files that appear in multiple grep results
```

**Tracing the feature:**
1. Start at the entry point (route, CLI command, event handler)
2. Follow the call chain through each layer
3. Note at each step:
   - File and function/class name
   - What it does
   - What patterns it follows (dependency injection, repository pattern, etc.)
   - How it handles errors
4. End at the deepest layer (database, external service, file system)

**If no similar feature exists:**
- Pick any representative feature and trace it
- The goal is to understand the codebase's patterns, not the specific domain

## Step 5: Write Exploration Document

Write `exploration_{codebase_name}.md` with this structure:

```markdown
# Codebase Exploration: {name}

**Path:** {absolute path}
**Language:** {primary language}
**Framework:** {if any}
**Size:** ~{N} files across {M} directories

## Layers Identified

| Layer | Directory | Key Files | Conventions |
|-------|-----------|-----------|-------------|
| ... | ... | ... | ... |

## Key Files & Entry Points

- `{file}` — {purpose}
- ...

## Feature Traces

### {Feature Name} (closest to proposed feature)
1. `{file}:{function}` — {what it does}
2. → `{file}:{function}` — {what it does}
3. → ...

### Patterns Observed
- {pattern}: {where it's used, how}
- ...

## Configuration & Build

- Build: {command}
- Test: {command}
- Key config: {files/env vars}

## Conventions & Patterns

- {convention}: {description}
- ...

## Gotchas & Constraints

- {gotcha}: {why it matters for the proposed feature}
- ...
```

## Sizing Heuristic

| Codebase size | Exploration time | Approach |
|---------------|-----------------|----------|
| Small (<50 files) | 1-2 minutes | Read key files directly |
| Medium (50-200 files) | 3-5 minutes | Glob + targeted reads |
| Large (200+ files) | 5-10 minutes | Explore agent + targeted deep-dives |

Don't over-explore. The goal is enough context to ask informed questions, not to understand every file.
