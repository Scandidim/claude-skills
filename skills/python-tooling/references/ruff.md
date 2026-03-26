# Ruff — Python Linter and Formatter

Ruff is a Rust-based Python linter and formatter that replaces flake8, black, isort, and dozens of plugins with a single tool. It runs 10–100× faster than the tools it replaces.

## Installation

```bash
pip install ruff           # project dependency
uv add --dev ruff          # with uv
pipx install ruff          # global install
```

## pyproject.toml Configuration

### Full Reference

```toml
[tool.ruff]
# Python version for syntax targeting
target-version = "py311"    # py38 | py39 | py310 | py311 | py312 | py313

# Line length (matches Black default)
line-length = 88

# Files to exclude from all checks
exclude = [
  ".git", ".venv", "__pycache__", "dist", "build",
  "migrations",          # Django/Alembic migrations — often auto-generated
  "*.pyi",               # Type stubs — skip if using separate stub packages
]

[tool.ruff.lint]
# Rule selection — add categories incrementally
select = [
  "E",     # pycodestyle errors
  "W",     # pycodestyle warnings
  "F",     # Pyflakes (undefined names, unused imports)
  "I",     # isort (import sorting)
  "UP",    # pyupgrade (modern syntax)
  "B",     # flake8-bugbear (common bugs)
  "SIM",   # flake8-simplify (simplifiable code)
  "RUF",   # Ruff-specific rules
]

# Rules to ignore (document WHY for team clarity)
ignore = [
  "E501",  # Line too long — handled by formatter
  "B008",  # Function call in default argument — common in FastAPI/Typer
  "SIM108", # Ternary — sometimes hurts readability
]

# Per-file ignores
[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101"]      # Allow assert in tests
"scripts/**" = ["T201"]    # Allow print in scripts
"src/migrations/**" = ["E501", "F401"]  # Generated migration files

# isort settings
[tool.ruff.lint.isort]
known-first-party = ["mypackage"]
force-sort-within-sections = true
split-on-trailing-comma = true

# flake8-bugbear settings
[tool.ruff.lint.flake8-bugbear]
extend-immutable-calls = ["fastapi.Depends", "fastapi.Query"]

[tool.ruff.format]
quote-style = "double"         # "double" | "single"
indent-style = "space"         # "space" | "tab"
magic-trailing-comma = true    # Respect trailing commas (Black-compatible)
line-ending = "auto"           # "auto" | "lf" | "crlf" | "native"
```

### Recommended Rule Sets by Project Type

```toml
# General Python project
select = ["E", "W", "F", "I", "UP", "B", "SIM", "RUF"]

# API / web service (add security + type checks)
select = ["E", "W", "F", "I", "UP", "B", "SIM", "RUF", "S", "ANN", "PT"]
ignore = ["ANN101", "ANN102", "ANN401"]  # Common ANN exceptions

# Data science / notebooks (more relaxed)
select = ["E", "W", "F", "I"]
ignore = ["E501", "B008"]

# Strict — production library
select = ["ALL"]
ignore = [
  "D",     # Docstring rules — add separately when ready
  "ANN",   # Annotations — add when fully typed
  "COM812", # Trailing comma — conflicts with formatter
  "ISC001", # Implicit string concat — conflicts with formatter
]
```

## Common Rule Categories

| Code | Tool Replaced | Description |
|------|--------------|-------------|
| `E`, `W` | flake8 | PEP 8 style |
| `F` | Pyflakes | Undefined names, unused imports |
| `I` | isort | Import ordering |
| `UP` | pyupgrade | Modern Python syntax (f-strings, `dict \| dict`) |
| `B` | flake8-bugbear | Probable bugs |
| `S` | bandit | Security issues |
| `ANN` | flake8-annotations | Type annotation enforcement |
| `PT` | flake8-pytest-style | Pytest style |
| `SIM` | flake8-simplify | Code simplification |
| `RUF` | (Ruff-specific) | Ruff's own rules |
| `D` | pydocstyle | Docstring style |
| `N` | pep8-naming | Naming conventions |
| `C90` | mccabe | Cyclomatic complexity |

## CLI Usage

```bash
# Lint and show violations
ruff check src/

# Lint and auto-fix safe fixes
ruff check --fix src/

# Lint with unsafe fixes (use with caution)
ruff check --fix --unsafe-fixes src/

# Format code (like Black)
ruff format src/

# Check formatting without modifying (CI mode)
ruff format --check src/

# Show what would be fixed
ruff check --diff src/

# Run on single file
ruff check src/mymodule/utils.py

# Show rule explanation
ruff rule B006

# Generate config from existing setup
ruff check --select ALL --statistics src/  # See which rules fire
```

## Inline Suppressions

```python
import os  # noqa: F401 — re-exported for public API

x = 1+2  # noqa: E225 — temporary, see issue #123

# Suppress entire file from a rule
# ruff: noqa: E501

def connect(password="admin"):  # noqa: S106 — test fixture only
    ...
```

## Migration from Legacy Tools

### From flake8 + black + isort

```bash
# 1. Install Ruff
pip install ruff

# 2. Remove old tools from requirements/pyproject
# Remove: flake8, black, isort, and their plugins

# 3. Create initial Ruff config (auto-detect from existing)
ruff check --select E,W,F,I,B . --statistics   # See scope

# 4. Run Ruff format (replaces Black)
ruff format .

# 5. Run Ruff check with fixes (replaces flake8 + isort)
ruff check --fix .

# 6. Fix remaining violations manually or add to ignore
```

### Equivalent Rule Mappings

| Old Tool | Ruff Code |
|----------|-----------|
| flake8 E1xx | `E1xx` |
| flake8 E2xx | `E2xx` |
| black | `ruff format` |
| isort | `I` rules |
| flake8-bugbear | `B` rules |
| bandit | `S` rules |
| pyupgrade | `UP` rules |
| pydocstyle | `D` rules |

## CI Integration

```yaml
# .github/workflows/lint.yml
- name: Ruff lint
  run: ruff check --output-format=github .

- name: Ruff format check
  run: ruff format --check .
```

The `--output-format=github` flag produces GitHub Actions annotations directly in the PR diff.

## ruff.toml (Alternative to pyproject.toml)

```toml
# ruff.toml — use when pyproject.toml is not available
target-version = "py311"
line-length = 88

[lint]
select = ["E", "W", "F", "I", "UP", "B", "SIM", "RUF"]
ignore = ["E501"]

[format]
quote-style = "double"
```

## Performance

Ruff caches results in `.ruff_cache/`. Add to `.gitignore`:

```gitignore
.ruff_cache/
```

For monorepos, configure per-package:

```toml
# packages/api/pyproject.toml
[tool.ruff]
extend = "../../pyproject.toml"   # Inherit root config
src = ["src"]

[tool.ruff.lint.per-file-ignores]
"tests/**" = ["S101", "ANN"]
```
