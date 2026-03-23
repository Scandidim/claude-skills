"""Shared pytest fixtures and script imports for claude-skills tests."""

import importlib.util
import sys
import textwrap
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"


def _import_script(name: str):
    """Import a hyphenated script by filename using importlib."""
    script_path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), script_path)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


# Pre-import scripts so tests can reference the module objects
validate_skills = _import_script("validate-skills")
validate_markdown = _import_script("validate-markdown")
update_docs = _import_script("update-docs")


# =============================================================================
# Skill fixture helpers
# =============================================================================


def make_skill(tmp_path: Path, name: str, frontmatter: str, body: str = "") -> Path:
    """Create a minimal skill directory with SKILL.md and a reference file."""
    skill_dir = tmp_path / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    refs_dir = skill_dir / "references"
    refs_dir.mkdir(exist_ok=True)
    (refs_dir / "overview.md").write_text("# Overview\n\nReference content.\n")

    skill_md = skill_dir / "SKILL.md"
    skill_md.write_text(f"---\n{frontmatter}\n---\n{body}")
    return skill_dir


VALID_FRONTMATTER = textwrap.dedent("""\
    name: test-skill
    description: Does something useful. Use when you need to test things.
    license: MIT
    metadata:
      author: https://github.com/testuser
      version: "1.0.0"
      domain: backend
      triggers: test, fixture, example
      role: specialist
      scope: implementation
      output-format: code
      related-skills: ""
""")

VALID_BODY = textwrap.dedent("""\

    ## Role Definition

    You are a test specialist.

    ## When to Use This Skill

    - When writing tests
    - When verifying behavior
    - When checking edge cases

    ## Core Workflow

    1. Understand the requirement
    2. Design the test approach
    3. Write the test cases
    4. Run and verify
    5. Iterate as needed

    ## Reference Guide

    See references/ for details.

    ## Constraints

    **MUST DO:**
    - Write meaningful tests

    **MUST NOT DO:**
    - Skip edge cases
""")
