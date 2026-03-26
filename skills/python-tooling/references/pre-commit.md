# Pre-commit — Git Hook Framework

Pre-commit manages git hooks that run automatically before each commit, ensuring code quality is enforced locally before code reaches CI.

## Installation

```bash
pip install pre-commit
pre-commit install          # Install hooks into .git/hooks/pre-commit
pre-commit install --hook-type pre-push  # Also install pre-push hooks
```

## .pre-commit-config.yaml Reference

```yaml
# Minimum pre-commit version required
minimum_pre_commit_version: '3.0.0'

# Default language version for all hooks
default_language_version:
  python: python3.11
  node: '22'

# Run hooks on all files (not just staged), useful for CI
# default_stages: [pre-commit]  # default

repos:
  # Ruff — linting and formatting
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.7
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
      - id: ruff-format

  # Pyright — type checking
  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.396
    hooks:
      - id: pyright
        additional_dependencies: []  # Add runtime deps if needed

  # Built-in pre-commit hooks
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-merge-conflict
      - id: check-added-large-files
        args: ['--maxkb=500']
      - id: debug-statements      # Catch forgotten breakpoint() / pdb
      - id: detect-private-key    # Block accidentally committed secrets
      - id: no-commit-to-branch
        args: ['--branch', 'main', '--branch', 'production']

  # Prettier — JS/TS/CSS/YAML/MDX formatting
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, css, yaml, markdown, mdx]
        additional_dependencies:
          - prettier@3.5.0
          - prettier-plugin-astro@0.14.0

  # Commit message format enforcement
  - repo: https://github.com/commitizen-tools/commitizen
    rev: v4.2.1
    hooks:
      - id: commitizen
        stages: [commit-msg]
```

## Common Hook Configurations

### Python Projects (Minimal)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.7
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: debug-statements
```

### Full-Stack Projects (Python + JS)

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.7
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0-alpha.8
    hooks:
      - id: prettier
        types_or: [javascript, jsx, ts, tsx, css, json, yaml, markdown]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v5.0.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-merge-conflict
      - id: detect-private-key
```

### Security-Focused

```yaml
repos:
  - repo: https://github.com/Yelp/detect-secrets
    rev: v1.5.0
    hooks:
      - id: detect-secrets
        args: ['--baseline', '.secrets.baseline']

  - repo: https://github.com/zricethezav/gitleaks
    rev: v8.21.2
    hooks:
      - id: gitleaks
```

## CLI Commands

```bash
# Install hooks (run after cloning a repo)
pre-commit install

# Run all hooks on all files (first setup, or CI)
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
pre-commit run ruff-format --all-files

# Run hooks on staged files only (default behavior on commit)
pre-commit run

# Update all hooks to latest versions
pre-commit autoupdate

# Update specific hook
pre-commit autoupdate --repo https://github.com/astral-sh/ruff-pre-commit

# Skip hooks for a single commit (emergency only)
git commit --no-verify -m "emergency fix"

# Uninstall hooks
pre-commit uninstall

# Clean hook environments (force reinstall)
pre-commit clean
pre-commit install
```

## CI Integration

### GitHub Actions

```yaml
# .github/workflows/pre-commit.yml
name: pre-commit
on:
  pull_request:
  push:
    branches: [main]

jobs:
  pre-commit:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - uses: pre-commit/action@v3.0.1   # Official action — handles caching
```

### GitHub Actions (Manual — More Control)

```yaml
- uses: actions/checkout@v4
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
- name: Cache pre-commit environments
  uses: actions/cache@v4
  with:
    path: ~/.cache/pre-commit
    key: pre-commit-${{ hashFiles('.pre-commit-config.yaml') }}
- name: Run pre-commit
  run: |
    pip install pre-commit
    pre-commit run --all-files
```

## Writing Custom Hooks

### Local Hook (No Separate Repo Required)

```yaml
repos:
  - repo: local
    hooks:
      - id: check-version-sync
        name: Check version.json sync
        entry: python scripts/check-version-sync.py
        language: python
        files: 'version\.json|CHANGELOG\.md'
        pass_filenames: false

      - id: run-tests
        name: Run unit tests
        entry: pytest tests/unit -x -q
        language: python
        pass_filenames: false
        stages: [pre-push]  # Only on push, not every commit

      - id: validate-openapi
        name: Validate OpenAPI schema
        entry: python -c "import yaml, jsonschema; ..."
        language: python
        files: 'openapi\.ya?ml$'
```

### Custom Hook with Dependencies

```yaml
- repo: local
  hooks:
    - id: mypy
      name: mypy type check
      entry: mypy
      language: python
      types: [python]
      additional_dependencies: ['mypy==1.13.0', 'types-requests']
      args: [--ignore-missing-imports]
```

## Hook Stages

```yaml
hooks:
  - id: my-hook
    stages: [pre-commit]     # default — on every commit
    # stages: [pre-push]     # only on git push
    # stages: [commit-msg]   # validate commit message
    # stages: [post-checkout] # after checkout/branch switch
    # stages: [manual]       # only via pre-commit run --hook-stage manual
```

## Pinning Versions (Best Practice)

Always pin `rev:` to a tag or SHA — never use `main` or `HEAD`:

```bash
# Update all to latest tags
pre-commit autoupdate

# Check current versions
pre-commit autoupdate --dry-run
```

Commit `.pre-commit-config.yaml` with pinned versions to ensure everyone on the team runs the same tool versions.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Hook fails in CI but not locally | Check Python/Node version match; run `pre-commit run --all-files` locally |
| `[ERROR] No such file or directory` | Run `pre-commit clean && pre-commit install` |
| Hook slow on large repos | Add `files:` pattern to limit scope; enable caching |
| Prettier conflicts with ruff-format | Remove Prettier from Python files; set `types_or` to JS/TS/CSS only |
| Hook not running on new file types | Add `types_or: [...]` or `types: [...]` to hook config |
| `--no-verify` used by team | Address root cause (slow hooks, false positives) rather than disabling |

## Team Onboarding Script

```bash
#!/usr/bin/env bash
# scripts/setup-dev.sh — run after cloning
set -euo pipefail

echo "Installing pre-commit hooks..."
pip install pre-commit
pre-commit install
pre-commit install --hook-type commit-msg

echo "Running hooks on all files (first-time check)..."
pre-commit run --all-files || true  # Show issues without failing setup

echo "Dev environment ready."
```
