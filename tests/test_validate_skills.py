"""Unit tests for scripts/validate-skills.py."""

import textwrap
from pathlib import Path

import pytest

from conftest import (
    VALID_BODY,
    VALID_FRONTMATTER,
    make_skill,
    validate_skills as vs,
)

simple_yaml_parse = vs.simple_yaml_parse
YamlChecker = vs.YamlChecker
RequiredFieldsChecker = vs.RequiredFieldsChecker
NameFormatChecker = vs.NameFormatChecker
DescriptionLengthChecker = vs.DescriptionLengthChecker
DescriptionFormatChecker = vs.DescriptionFormatChecker
MetadataFieldsChecker = vs.MetadataFieldsChecker
ReferencesDirectoryChecker = vs.ReferencesDirectoryChecker
ReferenceFileCountChecker = vs.ReferenceFileCountChecker
ScopeEnumChecker = vs.ScopeEnumChecker
CoreWorkflowStepCountChecker = vs.CoreWorkflowStepCountChecker
LineCountChecker = vs.LineCountChecker
SectionOrderChecker = vs.SectionOrderChecker
ManifestDagChecker = vs.ManifestDagChecker
Severity = vs.Severity


# =============================================================================
# simple_yaml_parse tests
# =============================================================================


class TestSimpleYamlParse:
    def test_parses_simple_key_value(self):
        result = simple_yaml_parse("name: my-skill\nlicense: MIT")
        assert result["name"] == "my-skill"
        assert result["license"] == "MIT"

    def test_strips_quoted_values(self):
        result = simple_yaml_parse('version: "1.0.0"')
        assert result["version"] == "1.0.0"

    def test_parses_nested_dict(self):
        yaml = "metadata:\n  author: alice\n  domain: backend"
        result = simple_yaml_parse(yaml)
        assert result["metadata"] == {"author": "alice", "domain": "backend"}

    def test_parses_list(self):
        yaml = "tags:\n  - one\n  - two"
        result = simple_yaml_parse(yaml)
        assert result["tags"] == ["one", "two"]

    def test_empty_string_returns_empty_dict(self):
        assert simple_yaml_parse("") == {}

    def test_key_with_no_value_yields_empty_dict(self):
        result = simple_yaml_parse("metadata:")
        assert result["metadata"] == {}

    def test_ignores_blank_lines(self):
        result = simple_yaml_parse("\nname: foo\n\nlicense: MIT\n")
        assert result["name"] == "foo"


# =============================================================================
# YamlChecker tests
# =============================================================================


class TestYamlChecker:
    checker = YamlChecker()

    def test_valid_skill_has_no_issues(self, tmp_path):
        skill_dir = make_skill(tmp_path, "my-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "my-skill")
        assert issues == []

    def test_missing_skill_md_is_error(self, tmp_path):
        skill_dir = tmp_path / "bare-skill"
        skill_dir.mkdir()
        issues = self.checker.check(skill_dir, "bare-skill")
        assert any(i.severity == Severity.ERROR for i in issues)
        assert any("Missing SKILL.md" in i.message for i in issues)

    def test_missing_opening_fence_is_error(self, tmp_path):
        skill_dir = tmp_path / "bad-skill"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("name: bad\n")
        issues = self.checker.check(skill_dir, "bad-skill")
        assert any("does not start with YAML frontmatter" in i.message for i in issues)

    def test_unclosed_frontmatter_is_error(self, tmp_path):
        skill_dir = tmp_path / "unclosed"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text("---\nname: unclosed\n")
        issues = self.checker.check(skill_dir, "unclosed")
        assert any("missing closing ---" in i.message for i in issues)


# =============================================================================
# RequiredFieldsChecker tests
# =============================================================================


class TestRequiredFieldsChecker:
    checker = RequiredFieldsChecker()

    def test_valid_skill_has_no_issues(self, tmp_path):
        skill_dir = make_skill(tmp_path, "my-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "my-skill")
        assert issues == []

    def test_missing_name_is_error(self, tmp_path):
        fm = VALID_FRONTMATTER.replace("name: test-skill\n", "")
        skill_dir = make_skill(tmp_path, "my-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "my-skill")
        assert any("Missing required field: name" in i.message for i in issues)

    def test_missing_description_is_error(self, tmp_path):
        lines = [ln for ln in VALID_FRONTMATTER.splitlines() if not ln.startswith("description:")]
        fm = "\n".join(lines)
        skill_dir = make_skill(tmp_path, "my-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "my-skill")
        assert any("Missing required field: description" in i.message for i in issues)


# =============================================================================
# NameFormatChecker tests
# =============================================================================


class TestNameFormatChecker:
    checker = NameFormatChecker()

    def test_valid_name_has_no_issues(self, tmp_path):
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert issues == []

    def test_name_with_spaces_is_error(self, tmp_path):
        fm = VALID_FRONTMATTER.replace("name: test-skill", "name: my skill")
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any(i.severity == Severity.ERROR for i in issues)
        assert any("Invalid name format" in i.message for i in issues)

    def test_name_with_parentheses_is_error(self, tmp_path):
        fm = VALID_FRONTMATTER.replace("name: test-skill", "name: my-skill(v2)")
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any("Invalid name format" in i.message for i in issues)

    def test_name_mismatch_with_directory_is_warning(self, tmp_path):
        fm = VALID_FRONTMATTER.replace("name: test-skill", "name: other-name")
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any(i.severity == Severity.WARNING for i in issues)
        assert any("doesn't match skill name" in i.message for i in issues)

    def test_alphanumeric_with_hyphens_is_valid(self, tmp_path):
        fm = VALID_FRONTMATTER.replace("name: test-skill", "name: react-expert-v2")
        skill_dir = make_skill(tmp_path, "react-expert-v2", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "react-expert-v2")
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert errors == []


# =============================================================================
# DescriptionLengthChecker tests
# =============================================================================


class TestDescriptionLengthChecker:
    checker = DescriptionLengthChecker()

    def test_short_description_is_fine(self, tmp_path):
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert issues == []

    def test_description_over_1024_chars_is_warning(self, tmp_path):
        long_desc = "x" * 1025
        fm = VALID_FRONTMATTER.replace(
            "description: Does something useful. Use when you need to test things.",
            f"description: {long_desc}",
        )
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any("exceeds" in i.message for i in issues)
        assert any(i.severity == Severity.WARNING for i in issues)

    def test_description_exactly_1024_chars_is_fine(self, tmp_path):
        exact_desc = "Use when " + "x" * (1024 - len("Use when "))
        fm = VALID_FRONTMATTER.replace(
            "description: Does something useful. Use when you need to test things.",
            f"description: {exact_desc}",
        )
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert not any("exceeds" in i.message for i in issues)


# =============================================================================
# DescriptionFormatChecker tests
# =============================================================================


class TestDescriptionFormatChecker:
    checker = DescriptionFormatChecker()

    def test_description_with_use_when_is_fine(self, tmp_path):
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert issues == []

    def test_description_without_use_when_is_warning(self, tmp_path):
        fm = VALID_FRONTMATTER.replace(
            "description: Does something useful. Use when you need to test things.",
            "description: Does something useful without any trigger clause.",
        )
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any(i.severity == Severity.WARNING for i in issues)
        assert any("trigger clause" in i.message for i in issues)


# =============================================================================
# MetadataFieldsChecker tests
# =============================================================================


class TestMetadataFieldsChecker:
    checker = MetadataFieldsChecker()

    def test_valid_metadata_has_no_errors(self, tmp_path):
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert errors == []

    def test_missing_metadata_key_is_error(self, tmp_path):
        lines = [
            ln
            for ln in VALID_FRONTMATTER.splitlines()
            if not ln.startswith("metadata") and not ln.startswith("  ")
        ]
        fm = "\n".join(lines)
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any("Missing 'metadata' key" in i.message for i in issues)

    def test_unknown_domain_is_warning(self, tmp_path):
        fm = VALID_FRONTMATTER.replace("domain: backend", "domain: unknown-domain-xyz")
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any(i.severity == Severity.WARNING for i in issues)
        assert any("Unknown domain" in i.message for i in issues)

    def test_missing_triggers_field_is_error(self, tmp_path):
        fm = VALID_FRONTMATTER.replace("  triggers: test, fixture, example\n", "")
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any("Missing required metadata field: triggers" in i.message for i in issues)


# =============================================================================
# ReferencesDirectoryChecker tests
# =============================================================================


class TestReferencesDirectoryChecker:
    checker = ReferencesDirectoryChecker()

    def test_valid_skill_with_references_dir_has_no_issues(self, tmp_path):
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert issues == []

    def test_missing_references_dir_is_error(self, tmp_path):
        skill_dir = tmp_path / "no-refs"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"---\n{VALID_FRONTMATTER}\n---\n{VALID_BODY}")
        issues = self.checker.check(skill_dir, "no-refs")
        assert any("Missing references/ directory" in i.message for i in issues)


# =============================================================================
# ReferenceFileCountChecker tests
# =============================================================================


class TestReferenceFileCountChecker:
    checker = ReferenceFileCountChecker()

    def test_skill_with_reference_files_has_no_issues(self, tmp_path):
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert issues == []

    def test_empty_references_dir_is_warning(self, tmp_path):
        skill_dir = tmp_path / "empty-refs"
        skill_dir.mkdir()
        (skill_dir / "SKILL.md").write_text(f"---\n{VALID_FRONTMATTER}\n---\n{VALID_BODY}")
        (skill_dir / "references").mkdir()
        issues = self.checker.check(skill_dir, "empty-refs")
        assert any(i.severity == Severity.WARNING for i in issues)
        assert any("No reference files" in i.message for i in issues)


# =============================================================================
# ScopeEnumChecker tests
# =============================================================================


class TestScopeEnumChecker:
    checker = ScopeEnumChecker()

    def test_valid_scope_has_no_issues(self, tmp_path):
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert issues == []

    def test_unknown_scope_is_warning(self, tmp_path):
        fm = VALID_FRONTMATTER.replace("scope: implementation", "scope: invalid-scope")
        skill_dir = make_skill(tmp_path, "test-skill", fm, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any(i.severity == Severity.WARNING for i in issues)
        assert any("Unknown scope" in i.message for i in issues)


# =============================================================================
# CoreWorkflowStepCountChecker tests
# =============================================================================


class TestCoreWorkflowStepCountChecker:
    checker = CoreWorkflowStepCountChecker()

    def test_five_steps_is_valid(self, tmp_path):
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert issues == []

    def test_three_steps_is_warning(self, tmp_path):
        body = textwrap.dedent("""\

            ## Core Workflow

            1. Step one
            2. Step two
            3. Step three
        """)
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, body)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any("3 steps" in i.message for i in issues)

    def test_missing_core_workflow_section_is_warning(self, tmp_path):
        body = "\n## Role Definition\n\nSome content.\n"
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, body)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any("Missing '## Core Workflow'" in i.message for i in issues)


# =============================================================================
# LineCountChecker tests
# =============================================================================


class TestLineCountChecker:
    checker = LineCountChecker()

    def test_body_with_too_few_lines_is_warning(self, tmp_path):
        body = "\n".join([f"line {i}" for i in range(10)])
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, body)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any("minimum" in i.message for i in issues)

    def test_body_with_too_many_lines_is_warning(self, tmp_path):
        body = "\n".join([f"line {i}" for i in range(200)])
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, body)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any("maximum" in i.message for i in issues)

    def test_no_errors_for_any_line_count(self, tmp_path):
        body = "\n".join([f"line {i}" for i in range(10)])
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, body)
        issues = self.checker.check(skill_dir, "test-skill")
        errors = [i for i in issues if i.severity == Severity.ERROR]
        assert errors == []


# =============================================================================
# SectionOrderChecker tests
# =============================================================================


class TestSectionOrderChecker:
    checker = SectionOrderChecker()

    def test_canonical_order_has_no_issues(self, tmp_path):
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, VALID_BODY)
        issues = self.checker.check(skill_dir, "test-skill")
        assert issues == []

    def test_out_of_order_sections_is_warning(self, tmp_path):
        body = textwrap.dedent("""\

            ## Core Workflow

            1. Step one
            2. Step two
            3. Step three
            4. Step four
            5. Step five

            ## Role Definition

            Role content here.
        """)
        skill_dir = make_skill(tmp_path, "test-skill", VALID_FRONTMATTER, body)
        issues = self.checker.check(skill_dir, "test-skill")
        assert any(i.severity == Severity.WARNING for i in issues)


# =============================================================================
# ManifestDagChecker._detect_cycles tests
# =============================================================================


class TestManifestDagCycleDetection:
    """Test the DAG cycle detection algorithm directly."""

    def _run_detect(self, phases: dict) -> list:
        checker = ManifestDagChecker()
        return checker._detect_cycles(phases, Path("manifest.yaml"))

    def test_linear_dag_has_no_cycles(self):
        phases = {
            "intake": {"depends_on": []},
            "discovery": {"depends_on": [{"phase": "intake", "strength": "required"}]},
            "planning": {"depends_on": [{"phase": "discovery", "strength": "required"}]},
        }
        issues = self._run_detect(phases)
        assert issues == []

    def test_simple_cycle_is_detected(self):
        phases = {
            "A": {"depends_on": [{"phase": "B"}]},
            "B": {"depends_on": [{"phase": "A"}]},
        }
        issues = self._run_detect(phases)
        assert any("DAG cycle detected" in i.message for i in issues)

    def test_self_cycle_is_detected(self):
        phases = {
            "A": {"depends_on": [{"phase": "A"}]},
        }
        issues = self._run_detect(phases)
        assert any("DAG cycle detected" in i.message for i in issues)

    def test_three_node_cycle_is_detected(self):
        phases = {
            "A": {"depends_on": [{"phase": "B"}]},
            "B": {"depends_on": [{"phase": "C"}]},
            "C": {"depends_on": [{"phase": "A"}]},
        }
        issues = self._run_detect(phases)
        assert any("DAG cycle detected" in i.message for i in issues)

    def test_disconnected_acyclic_graph_has_no_cycles(self):
        phases = {
            "alpha": {"depends_on": []},
            "beta": {"depends_on": []},
            "gamma": {"depends_on": [{"phase": "alpha"}]},
        }
        issues = self._run_detect(phases)
        assert issues == []

    def test_reference_to_undefined_phase_does_not_crash(self):
        phases = {
            "A": {"depends_on": [{"phase": "undefined-phase"}]},
        }
        issues = self._run_detect(phases)
        assert not any("DAG cycle" in i.message for i in issues)
