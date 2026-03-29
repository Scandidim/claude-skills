# Test Coverage Analysis

**Date:** 2026-03-23

## Summary

The codebase has effectively zero unit tests. The only test file is
`scripts/test-makefile.sh` — 8 bash integration tests covering the
`dev-link`/`dev-unlink` Makefile targets.

CI validation scripts check end-products (skill files, markdown, doc counts)
but do not test individual functions in isolation.

---

## Current Coverage

| Component | Lines | Test Coverage |
|-----------|-------|---------------|
| `validate-skills.py` | 2,049 | None |
| `validate-markdown.py` | 259 | None |
| `update-docs.py` | 387 | None |
| `migrate-frontmatter.py` | 482 | None |
| `test-makefile.sh` | 158 | 8 bash integration tests |

**Total Python code:** 3,177 lines with zero unit test coverage.

---

## Critical Gaps

### 1. `validate-skills.py` (highest priority)

20+ checker classes with no tests:

- `ManifestDagChecker` — cycle detection algorithm; bugs here could allow
  circular skill dependencies to pass silently
- `CrossRefChecker` — validates `related-skills` links across 66 skills
- `YamlChecker` — custom YAML parsing fallback (no PyYAML dependency)
- `DescriptionFormatChecker` — regex-based "Use when" trigger detection
- `SectionOrderChecker` / `LineCountChecker` — structural validation rules
- `CountConsistencyChecker` — ensures skill/reference counts match docs

Any regression silently passes broken skills through CI.

### 2. `validate-markdown.py`

Pure helper functions (`count_columns`, `is_table_row`, `is_separator_row`,
`is_html_comment`) have no tests. Regex-heavy table validation is fragile.

### 3. `update-docs.py`

- Filesystem traversal functions (`count_skills`, `count_references`,
  `count_workflows`) are untested
- Marker replacement logic touches 8 files on every release
- Dry-run vs. write mode divergence is untested

### 4. `migrate-frontmatter.py`

No tests at all. Used for one-time migrations but could be rerun.

---

## Proposed Improvements

### Priority 1 — Unit tests for `validate-skills.py`

Set up `pytest` with fixture skill directories:

```python
# tests/test_validate_skills.py

def test_name_format_rejects_special_chars():
    checker = NameFormatChecker(...)
    result = checker.check({"name": "my skill (v2)"})
    assert result.has_errors

def test_dag_checker_detects_cycle():
    # Skill A → B → A
    assert checker.has_cycle({"A": ["B"], "B": ["A"]})

def test_description_requires_use_when():
    assert checker.check({"description": "Does stuff."}).has_errors
    assert not checker.check({"description": "Does stuff. Use when X."}).has_errors

def test_description_rejects_process_steps():
    desc = "First investigate root cause, then analyze patterns, then fix."
    assert checker.check({"description": desc}).has_warnings
```

### Priority 2 — Unit tests for `validate-markdown.py`

Pure functions are easy to test with inline fixtures:

```python
def test_count_columns():
    assert count_columns("| a | b | c |") == 3

def test_detects_html_comment_in_table():
    lines = ["| col |", "|---|", "<!-- comment -->", "| val |"]
    issues = validate_table(lines)
    assert any("HTML comment" in i.message for i in issues)

def test_detects_unclosed_code_block():
    lines = ["```python", "x = 1"]  # no closing ```
    issues = validate_code_blocks(lines)
    assert issues
```

### Priority 3 — Snapshot tests for `update-docs.py`

```python
def test_count_skills_returns_correct_count(tmp_path):
    (tmp_path / "skills" / "react-expert").mkdir(parents=True)
    (tmp_path / "skills" / "nestjs-expert").mkdir(parents=True)
    assert count_skills(tmp_path) == 2

def test_marker_replacement_writes_correct_value(tmp_path):
    readme = tmp_path / "README.md"
    readme.write_text("<!-- skill-count -->0<!-- /skill-count -->")
    update_marker(readme, "skill-count", "66")
    assert "66" in readme.read_text()
```

### Priority 4 — Edge case tests

- Malformed YAML in skill frontmatter
- Missing `references/` directory on a valid skill
- Description exactly at 1024 characters (boundary condition)
- Skills with circular `related-skills` references
- Workflow manifest with unreachable nodes
- Empty skill directories

### Priority 5 — Coverage tracking in CI

```yaml
# In validate.yml
- name: Run tests with coverage
  run: pytest tests/ --cov=scripts --cov-report=xml --cov-fail-under=70
```

---

## Missing Infrastructure

| Item | Action Needed |
|------|--------------|
| `pytest` | Add to dev dependencies |
| `tests/` directory | Create with fixture skill files |
| `pyproject.toml` / `pytest.ini` | Add pytest configuration |
| `coverage.py` / `pytest-cov` | Add to dev dependencies |
| Sample fixture skills | Create minimal valid/invalid examples |

---

## Recommended Starting Point

1. Add `pytest` and `pytest-cov` to a `requirements-dev.txt`
2. Create `tests/fixtures/` with minimal valid and invalid skill directories
3. Write unit tests for `NameFormatChecker`, `DescriptionFormatChecker`, and
   `ManifestDagChecker` — the three most logic-dense, least-tested components
4. Add a `make test-unit` target that runs pytest
5. Hook pytest into CI alongside the existing validation steps
