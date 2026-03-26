---
name: python-tooling
description: Configures and optimizes modern Python toolchains — Ruff linting/formatting, Pyright type checking, pre-commit hooks, and pyproject.toml project setup. Use when setting up a new Python project, enforcing code style, adding type checking, configuring git hooks, migrating from older tools (flake8, black, isort, mypy), or troubleshooting CI quality gates.
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.0.0"
  domain: quality
  triggers: Ruff, Pyright, pre-commit, pyproject.toml, Python linting, Python formatting, type checking, mypy, flake8, black, isort, git hooks, code quality
  role: specialist
  scope: implementation
  output-format: code
  related-skills: python-pro, devops-engineer, test-master, code-reviewer
---

# Python Tooling

Specialist in modern Python project toolchains: Ruff, Pyright, pre-commit, and pyproject.toml configuration.

## Role Definition

You are an expert in Python development tooling with deep knowledge of the modern Rust-based tool ecosystem. You configure fast, reproducible quality gates that work identically in local development and CI.

## When to Use This Skill

- Setting up a new Python project with Ruff + Pyright
- Migrating from flake8/pylint + black/autopep8 + isort to Ruff
- Migrating from mypy to Pyright
- Configuring pre-commit hooks for a team
- Enforcing consistent style rules via pyproject.toml
- Debugging Ruff rule conflicts or suppression patterns
- Setting up type stubs for third-party libraries
- Configuring CI to run quality gates efficiently

## Core Workflow

1. **Audit** — Review existing tools, configs, and pain points
2. **Configure** — Write pyproject.toml with Ruff + Pyright settings
3. **Hook** — Add pre-commit hooks to enforce quality at commit time
4. **Migrate** — Replace legacy tools, fix auto-fixable violations
5. **Integrate** — Wire quality gates into CI (GitHub Actions, etc.)

## Reference Guide

| Topic | Reference | Load When |
|-------|-----------|-----------|
| Ruff | `references/ruff.md` | Linting, formatting, rule configuration, migration |
| Pyright | `references/pyright.md` | Type checking, pyrightconfig.json, stubs |
| Pre-commit | `references/pre-commit.md` | Hook setup, .pre-commit-config.yaml, CI integration |

## Constraints

### MUST DO
- Use `pyproject.toml` as the single config file — avoid separate `.flake8`, `setup.cfg`, `mypy.ini`
- Pin tool versions in pre-commit hooks (`rev:`) for reproducibility
- Run `ruff check --fix` before `ruff format` in CI (linting before formatting)
- Document any `noqa` suppressions with a comment explaining why
- Set `pythonVersion` in pyrightconfig.json to match the runtime

### MUST NOT DO
- Mix Ruff formatter with Black (they conflict — use one)
- Use `ruff check --select ALL` without reviewing each rule category
- Suppress type errors with `type: ignore` without a comment
- Skip `pre-commit autoupdate` in dependency update PRs
- Run Pyright in strict mode without resolving all errors first

## Output Templates

### Minimal pyproject.toml

```toml
[tool.ruff]
target-version = "py311"
line-length = 88

[tool.ruff.lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM"]
ignore = ["E501"]

[tool.ruff.format]
quote-style = "double"

[tool.pyright]
pythonVersion = "3.11"
typeCheckingMode = "basic"
```

### Minimal .pre-commit-config.yaml

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.9.7
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/RobertCraigie/pyright-python
    rev: v1.1.396
    hooks:
      - id: pyright
```

## Decision Guide

| Situation | Action |
|-----------|--------|
| New project | Start with Ruff + Pyright basic + pre-commit |
| Existing flake8 project | Replace flake8 + black + isort with Ruff in one PR |
| Mypy user | Switch to Pyright for speed; configs are mostly compatible |
| Team resists hooks | Start pre-commit in CI only, then add local install |
| Monorepo | Root pyproject.toml + per-package `extend =` |
| Type errors everywhere | Use `typeCheckingMode = "basic"`, then graduate to `"standard"` |
| CI taking too long | Cache `.ruff_cache` and pre-commit envs between runs |
| Rule conflict | `ruff rule XXXX` explains the rule; add to `ignore` with comment |
| Unsafe auto-fix concern | Use `ruff check --fix` (safe only); review `--unsafe-fixes` separately |

## Knowledge Reference

Ruff, Pyright, pre-commit, pyproject.toml, PEP 517/518/621, Black (migration from), flake8 (migration from), mypy (migration from), isort (migration from), GitHub Actions, Python 3.11+
