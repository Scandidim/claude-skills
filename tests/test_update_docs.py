"""Unit tests for scripts/update-docs.py."""

from pathlib import Path

import pytest

from conftest import update_docs as ud

count_skills = ud.count_skills
count_references = ud.count_references
count_workflows = ud.count_workflows
replace_marker = ud.replace_marker


# =============================================================================
# count_skills
# =============================================================================


class TestCountSkills:
    def test_counts_dirs_with_skill_md(self, tmp_path):
        skills = tmp_path / "skills"
        for name in ("react-expert", "nestjs-expert", "python-expert"):
            d = skills / name
            d.mkdir(parents=True)
            (d / "SKILL.md").write_text("---\nname: x\n---\n")
        assert count_skills(tmp_path) == 3

    def test_ignores_dirs_without_skill_md(self, tmp_path):
        skills = tmp_path / "skills"
        (skills / "with-skill").mkdir(parents=True)
        (skills / "with-skill" / "SKILL.md").write_text("---\nname: x\n---\n")
        (skills / "no-skill").mkdir(parents=True)
        assert count_skills(tmp_path) == 1

    def test_returns_zero_when_skills_dir_missing(self, tmp_path):
        assert count_skills(tmp_path) == 0

    def test_returns_zero_when_skills_dir_empty(self, tmp_path):
        (tmp_path / "skills").mkdir()
        assert count_skills(tmp_path) == 0

    def test_does_not_count_files_as_skills(self, tmp_path):
        skills = tmp_path / "skills"
        skills.mkdir()
        (skills / "some-file.txt").write_text("not a skill")
        assert count_skills(tmp_path) == 0


# =============================================================================
# count_references
# =============================================================================


class TestCountReferences:
    def test_counts_all_reference_files(self, tmp_path):
        skills = tmp_path / "skills"
        for skill_name in ("skill-a", "skill-b"):
            refs = skills / skill_name / "references"
            refs.mkdir(parents=True)
            (refs / "overview.md").write_text("# Overview")
            (refs / "patterns.md").write_text("# Patterns")
        assert count_references(tmp_path) == 4

    def test_returns_zero_when_skills_dir_missing(self, tmp_path):
        assert count_references(tmp_path) == 0

    def test_ignores_non_md_files(self, tmp_path):
        refs = tmp_path / "skills" / "skill-a" / "references"
        refs.mkdir(parents=True)
        (refs / "notes.md").write_text("# Notes")
        (refs / "data.json").write_text("{}")
        assert count_references(tmp_path) == 1


# =============================================================================
# count_workflows
# =============================================================================


class TestCountWorkflows:
    def test_counts_workflow_md_files(self, tmp_path):
        cmds = tmp_path / "commands" / "project"
        cmds.mkdir(parents=True)
        for i in range(3):
            (cmds / f"phase-{i}.md").write_text(f"# Phase {i}")
        assert count_workflows(tmp_path) == 3

    def test_returns_zero_when_commands_dir_missing(self, tmp_path):
        assert count_workflows(tmp_path) == 0

    def test_counts_nested_md_files(self, tmp_path):
        cmds = tmp_path / "commands" / "project"
        sub = cmds / "subdir"
        sub.mkdir(parents=True)
        (cmds / "top.md").write_text("# Top")
        (sub / "nested.md").write_text("# Nested")
        assert count_workflows(tmp_path) == 2


# =============================================================================
# replace_marker
# =============================================================================


class TestReplaceMarker:
    def test_replaces_marker_value(self):
        content = "<!-- SKILL_COUNT -->65<!-- /SKILL_COUNT -->"
        result = replace_marker(content, "SKILL_COUNT", "70")
        assert result == "<!-- SKILL_COUNT -->70<!-- /SKILL_COUNT -->"

    def test_replaces_marker_with_spaces(self):
        content = "<!-- SKILL_COUNT --> 65 <!-- /SKILL_COUNT -->"
        result = replace_marker(content, "SKILL_COUNT", "70")
        assert "70" in result
        assert "65" not in result

    def test_no_match_returns_content_unchanged(self):
        content = "no markers here"
        result = replace_marker(content, "SKILL_COUNT", "70")
        assert result == content

    def test_replaces_multiline_content(self):
        content = "<!-- VERSION -->\n0.4.0\n<!-- /VERSION -->"
        result = replace_marker(content, "VERSION", "0.5.0")
        assert "0.5.0" in result
        assert "0.4.0" not in result

    def test_replaces_only_matching_marker(self):
        content = (
            "<!-- SKILL_COUNT -->65<!-- /SKILL_COUNT --> "
            "<!-- VERSION -->0.4.0<!-- /VERSION -->"
        )
        result = replace_marker(content, "SKILL_COUNT", "70")
        assert "<!-- SKILL_COUNT -->70<!-- /SKILL_COUNT -->" in result
        assert "<!-- VERSION -->0.4.0<!-- /VERSION -->" in result

    def test_version_string_replacement(self):
        content = "<!-- VERSION -->0.1.0<!-- /VERSION -->"
        result = replace_marker(content, "VERSION", "1.0.0")
        assert result == "<!-- VERSION -->1.0.0<!-- /VERSION -->"
