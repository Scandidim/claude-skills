# Claude Skills Project Configuration

> This file governs Claude's behavior when working on the claude-skills repository.

---

## Repository Overview

**claude-skills** (published as `fullstack-dev-skills@jeffallan`) is a Claude Code plugin providing 66 specialist skills and 9 workflow commands for full-stack developers. Current version: see `version.json`.

### Directory Structure

```
claude-skills/
├── skills/               # 66 skill directories (e.g. react-expert/, nestjs-expert/)
│   └── <skill-name>/
│       ├── SKILL.md      # Tier-1 entry point (~80-100 lines)
│       └── references/   # Tier-2 deep-dive files (100-600 lines each)
├── commands/             # Workflow slash commands
│   ├── project/          # Phase commands: discovery, planning, execution, retrospectives
│   ├── common-ground/    # /common-ground context-engineering command
│   └── workflow-manifest.yaml  # Workflow phase definitions and dependencies
├── scripts/              # Python tooling
│   ├── validate-skills.py   # Validates frontmatter, descriptions, references
│   ├── validate-markdown.py # Validates markdown syntax
│   ├── update-docs.py       # Updates version counts across all docs
│   └── migrate-frontmatter.py
├── docs/                 # Extended documentation
│   ├── WORKFLOW_COMMANDS.md
│   ├── ATLASSIAN_MCP_SETUP.md
│   ├── COMMON_GROUND.md
│   ├── SUPPORTED_AGENTS.md
│   ├── local_skill_development.md
│   └── workflow/         # Phase workflow descriptions
├── specs/                # Feature specification documents
├── research/             # Research notes and findings
├── site/                 # Astro documentation site (jeffallan.github.io/claude-skills)
├── assets/               # Social preview images
├── MODELCLAUDE.md        # Template users copy to their own projects' CLAUDE.md
├── SKILLS_GUIDE.md       # Full skill listing with decision trees
├── QUICKSTART.md         # Installation guide
├── CHANGELOG.md          # Version history (Keep a Changelog format)
├── version.json          # Single source of truth for version + counts
├── Makefile              # Dev workflow targets
├── ruff.toml             # Python linting config
└── pyrightconfig.json    # Python type-checking config
```

### Key Files

- **`version.json`** — Single source of truth for `version`, `skillCount`, `workflowCount`, `referenceFileCount`. Always update via `python scripts/update-docs.py`.
- **`MODELCLAUDE.md`** — Template for end users to copy into their own projects. Contains AI behavioral guardrails (skill activation, verification discipline, debugging threshold). Do **not** confuse with this file.
- **`commands/workflow-manifest.yaml`** — Defines the 5-phase project workflow (intake → discovery → planning → execution → retrospectives) and command dependencies.

---

## Development Setup

### Local Testing

Use Makefile targets to link your working copy to the plugin cache for live testing:

```bash
make dev-link    # Symlink cache dir → working copy (restart Claude Code after)
make dev-unlink  # Restore the released cache snapshot
```

See `docs/local_skill_development.md` for the full symlink workflow.

### Validation Commands

Run these before committing:

```bash
python scripts/validate-skills.py          # Validate all skills
python scripts/validate-skills.py --skill react-expert  # Single skill
python scripts/validate-markdown.py       # Check markdown syntax
python scripts/update-docs.py --check     # Verify counts are in sync
```

### Linting

```bash
make lint        # Check Python (ruff + pyright) and site (prettier)
make format      # Auto-fix Python and site formatting
make validate    # validate-skills + update-docs --check
make test        # Run Makefile self-tests
```

### Commit Message Format

- `Add:` — new features, skills, commands
- `Fix:` — bug fixes
- `Update:` — improvements to existing content
- `Docs:` — documentation-only changes

---

## GitHub & CI/CD

### Branch Strategy

- **`main`** — stable, released code. CI runs on every push and PR.
- **`dev`** — integration branch for work-in-progress. CI runs here too.
- Feature branches: `feature/your-feature-name` or `fix/your-bug-fix`.

### CI Workflows (`.github/workflows/`)

| File | Trigger | What it does |
|------|---------|--------------|
| `ci.yml` | push/PR → `main`, `dev` | Runs `validate.yml` as a reusable job |
| `validate.yml` | Called by CI & Release | Validates skills, markdown, doc counts, lints Python & Astro |
| `release.yml` | Push of `v*` tag or manual dispatch | Runs validate, builds docs site, deploys to GitHub Pages, creates GitHub Release |

**Validate job steps:**
1. `python scripts/validate-skills.py` — YAML frontmatter, description format, reference links
2. `python scripts/validate-markdown.py --check` — table syntax, unclosed code blocks
3. `python scripts/update-docs.py --check` — skill/reference counts in sync across all docs
4. `pre-commit` hooks — ruff lint/format on Python scripts
5. Prettier check on `site/src/**/*.astro`

**Release job steps (tag `v*`):**
1. Extracts release notes from `CHANGELOG.md` for the tagged version
2. Builds the Astro documentation site (`site/`)
3. Deploys to GitHub Pages
4. Creates a GitHub Release with the extracted changelog notes

### Issue Templates (`.github/ISSUE_TEMPLATE/`)

| Template | Use for |
|----------|---------|
| `new-skill.yml` | Proposing a new skill — collects name, domain, trigger conditions, keywords, overlapping skills, reference topics |
| `claude-issue.yml` | Claude-filed issues — collects issue type, overview, implementation plan, acceptance criteria |

### PR Checklist (implied by CI)

Before opening a PR, ensure locally:

```bash
python scripts/validate-skills.py   # must exit 0
python scripts/validate-markdown.py # must exit 0
python scripts/update-docs.py --check  # counts must match
make lint                           # ruff + pyright + prettier
```

CI will block merge if any of these fail.

---

## Skill Authorship Standards

Skills follow the [Agent Skills specification](https://agentskills.io/specification). This section covers project-specific conventions that go beyond the base spec.

### The Description Trap

**Critical:** Never put process steps or workflow sequences in descriptions. When descriptions contain step-by-step instructions, agents follow the brief description instead of reading the full skill content. This defeats the purpose of detailed skills.

Brief capability statements (what it does) and trigger conditions (when to use it) are both appropriate. Process steps (how it works) are not.

**BAD - Process steps in description:**
```yaml
description: Use for debugging. First investigate root cause, then analyze
patterns, test hypotheses, and implement fixes with tests.
```

**GOOD - Capability + trigger:**
```yaml
description: Diagnoses bugs through root cause analysis and pattern matching.
Use when encountering errors or unexpected behavior requiring investigation.
```

**Format:** `[Brief capability statement]. Use when [triggering conditions].`

Descriptions tell WHAT the skill does and WHEN to use it. The SKILL.md body tells HOW.

---

### Frontmatter Requirements

Per the [Agent Skills specification](https://agentskills.io/specification), only `name` and `description` are top-level required fields. Custom fields go under `metadata`.

```yaml
---
name: skill-name-with-hyphens
description: [Brief capability statement]. Use when [triggering conditions] - max 1024 chars
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.0.0"
  domain: frontend
  triggers: keyword1, keyword2, keyword3
  role: specialist
  scope: implementation
  output-format: code
  related-skills: fullstack-guardian, test-master, devops-engineer
---
```

**Top-level fields (spec-defined):**
- `name`: Letters, numbers, and hyphens only (no parentheses or special characters)
- `description`: Maximum 1024 characters. Capability statement + trigger conditions. No process steps.
- `license`: Always `MIT` for this project
- `allowed-tools`: Space-delimited tool list (only on skills that restrict tools)

**Metadata fields (project-specific):**
- `author`: GitHub profile URL of the skill author
- `version`: Semantic version string (quoted, e.g., `"1.0.0"`)
- `domain`: Category from the domain list below
- `triggers`: Comma-separated searchable keywords
- `role`: `specialist` | `expert` | `architect` | `engineer`
- `scope`: `implementation` | `review` | `design` | `system-design` | `testing` | `analysis` | `infrastructure` | `optimization` | `architecture`
- `output-format`: `code` | `document` | `report` | `architecture` | `specification` | `schema` | `manifests` | `analysis` | `analysis-and-code` | `code+analysis`
- `related-skills`: Comma-separated skill directory names (e.g., `fullstack-guardian, test-master`). Must resolve to existing skill directories.

**Domain values:**
`language` · `backend` · `frontend` · `infrastructure` · `api-architecture` · `quality` · `devops` · `security` · `data-ml` · `platform` · `specialized` · `workflow`

---

### Reference File Standards

Reference files follow the [Agent Skills specification](https://agentskills.io/specification). No specific headers are required.

**Guidelines:**
- 100-600 lines per reference file
- Keep files focused on a single topic
- Complete, working code examples with TypeScript types
- Cross-reference related skills where relevant
- Include "when to use" and "when not to use" guidance
- Practical patterns over theoretical explanations

### Framework Idiom Principle

Reference files for framework-specific skills must reflect the idiomatic best practices of that framework, not generic patterns applied uniformly across all skills. If a framework provides a built-in mechanism (e.g., global error handling, middleware, dependency injection), reference examples should use it rather than duplicating that behavior manually. Each framework's conventions for error handling, architecture, and code organization take precedence over cross-project consistency.

---

### Progressive Disclosure Architecture

**Tier 1 - SKILL.md (~80-100 lines)**
- Role definition and expertise level
- When-to-use guidance (triggers)
- Core workflow (5 steps)
- Constraints (MUST DO / MUST NOT DO)
- Routing table to references

**Tier 2 - Reference Files (100-600 lines each)**
- Deep technical content
- Complete code examples
- Edge cases and anti-patterns
- Loaded only when context requires

**Goal:** 50% token reduction through selective loading.

---

## Project Workflow

### When Creating New Skills

1. Check existing skills for overlap
2. Write SKILL.md with capability + trigger description (no process steps)
3. Create reference files for deep content (100+ lines)
4. Add routing table linking topics to references
5. Test skill triggers with realistic prompts
6. Update SKILLS_GUIDE.md if adding new domain

### When Modifying Skills

1. Read the full current skill before editing
2. Maintain capability + trigger description format (no process steps)
3. Preserve progressive disclosure structure
4. Update related cross-references
5. Verify routing table accuracy

---

## Release Checklist

When releasing a new version, follow these steps.

### 1. Update Version and Counts

Version and counts are managed through `version.json`:

```json
{
  "version": "0.4.2",
  "skillCount": 65,
  "workflowCount": 9,
  "referenceFileCount": 355
}
```

**To release a new version:**

1. Update the `version` field in `version.json`
2. Run the update script:

```bash
python scripts/update-docs.py
```

The script will:
- Compute counts from the filesystem (skills, references, workflows)
- Update `version.json` with computed counts
- Update all documentation files (README.md, plugin.json, etc.)

**Options:**
```bash
python scripts/update-docs.py --check    # Verify files are in sync (CI use)
python scripts/update-docs.py --dry-run  # Preview changes without writing
```

### 2. Update CHANGELOG.md

Add new version entry at the top following Keep a Changelog format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features, skills, commands

### Changed
- Modified functionality, updated skills

### Fixed
- Bug fixes
```

Add version comparison link at bottom:
```markdown
[X.Y.Z]: https://github.com/jeffallan/claude-skills/compare/vPREVIOUS...vX.Y.Z
```

### 3. Update Documentation for New/Modified Content

**For new skills:**
- Add to `SKILLS_GUIDE.md` in appropriate category
- Add to decision trees if applicable
- Run `python scripts/update-docs.py` to update counts

**For new commands:**
- Add to `docs/WORKFLOW_COMMANDS.md`
- Add to `README.md` Project Workflow Commands table
- Run `python scripts/update-docs.py` to update counts

**For modified skills/commands:**
- Update any cross-references
- Update SKILLS_GUIDE.md if triggers changed

### 4. Generate Social Preview

After all updates, regenerate the social preview image:

```bash
npm install --no-save puppeteer && node ./assets/capture-screenshot.js
```

This creates `assets/social-preview.png` from `assets/social-preview.html`.

### 5. Validate Skills Integrity

**Critical:** Run validation before release to prevent broken skills from being published.

```bash
python scripts/validate-skills.py
```

The script validates:
- **YAML frontmatter** - Parsing, required fields (name, description, triggers), format
- **Name format** - Letters, numbers, hyphens only
- **Description** - Max 1024 chars, must contain "Use when" trigger clause
- **References** - Directory exists, has files, proper headers
- **Count consistency** - Skills/reference counts match across documentation

**Options:**
```bash
python scripts/validate-skills.py --check yaml       # YAML checks only
python scripts/validate-skills.py --check references # Reference checks only
python scripts/validate-skills.py --skill react-expert  # Single skill
python scripts/validate-skills.py --format json      # JSON output for CI
python scripts/validate-skills.py --help             # Full usage
```

**Exit codes:** 0 = success (warnings OK), 1 = errors found

### 6. Validate Markdown Syntax

**Critical:** Run markdown validation to catch parsing errors.

```bash
python scripts/validate-markdown.py
```

The script validates:
- **HTML comments in tables** - Comments between table rows break parsing
- **Unclosed code blocks** - Ensures all code fences are properly closed
- **Missing table separators** - Tables require `|---|` row after header
- **Column count consistency** - All table rows must have same column count

**Options:**
```bash
python scripts/validate-markdown.py --check       # CI mode (exit code only)
python scripts/validate-markdown.py --path FILE   # Single file
python scripts/validate-markdown.py --format json # JSON output for CI
```

**Exit codes:** 0 = no issues, 1 = issues found

### 7. Final Verification

After running validation, manually verify:

```bash
# Check no old version references remain (except historical changelog)
grep -r "OLD_VERSION" --include="*.md" --include="*.json" --include="*.html"
```

---

## Attribution

Behavioral patterns and process discipline adapted from:
- **[obra/superpowers](https://github.com/obra/superpowers)** by Jesse Vincent (@obra)
- License: MIT

Research documented in: `research/superpowers.md`
