"""Unit tests for scripts/validate-markdown.py."""

import textwrap
from pathlib import Path

import pytest

from conftest import validate_markdown as vm

count_columns = vm.count_columns
is_html_comment = vm.is_html_comment
is_separator_row = vm.is_separator_row
is_table_row = vm.is_table_row
validate_file = vm.validate_file
IssueType = vm.IssueType


# =============================================================================
# count_columns
# =============================================================================


class TestCountColumns:
    def test_three_columns(self):
        assert count_columns("| a | b | c |") == 3

    def test_one_column(self):
        assert count_columns("| a |") == 1

    def test_two_columns(self):
        assert count_columns("| foo | bar |") == 2

    def test_escaped_pipe_is_not_counted(self):
        # "| a \| b | c |" — escaped pipe is inside col 1, so still 2 cols
        assert count_columns("| a \\| b | c |") == 2

    def test_separator_row(self):
        assert count_columns("|---|---|---|") == 3


# =============================================================================
# is_table_row
# =============================================================================


class TestIsTableRow:
    def test_standard_row(self):
        assert is_table_row("| col1 | col2 |")

    def test_separator_row(self):
        assert is_table_row("|---|---|")

    def test_plain_text_is_not_table(self):
        assert not is_table_row("just some text")

    def test_single_pipe_is_not_table(self):
        assert not is_table_row("|")

    def test_row_with_leading_spaces(self):
        assert is_table_row("  | a | b |")


# =============================================================================
# is_separator_row
# =============================================================================


class TestIsSeparatorRow:
    def test_simple_separator(self):
        assert is_separator_row("|---|")

    def test_multi_column_separator(self):
        assert is_separator_row("|---|---|---|")

    def test_separator_with_colons(self):
        assert is_separator_row("|:--|:--:|--:|")

    def test_data_row_is_not_separator(self):
        assert not is_separator_row("| hello | world |")

    def test_empty_row_is_not_separator(self):
        assert not is_separator_row("||")


# =============================================================================
# is_html_comment
# =============================================================================


class TestIsHtmlComment:
    def test_detects_html_comment(self):
        assert is_html_comment("<!-- this is a comment -->")

    def test_detects_inline_comment(self):
        assert is_html_comment("some text <!-- comment --> more text")

    def test_regular_line_is_not_comment(self):
        assert not is_html_comment("| col | value |")

    def test_code_block_fence_is_not_comment(self):
        assert not is_html_comment("```python")


# =============================================================================
# validate_file — integration-style tests using tmp files
# =============================================================================


class TestValidateFile:
    def _write(self, tmp_path: Path, content: str) -> Path:
        f = tmp_path / "test.md"
        f.write_text(textwrap.dedent(content))
        return f

    def test_clean_file_has_no_issues(self, tmp_path):
        f = self._write(tmp_path, """\
            # Title

            | Name | Value |
            |------|-------|
            | foo  | bar   |
        """)
        issues = validate_file(f)
        assert issues == []

    def test_detects_html_comment_between_header_and_separator(self, tmp_path):
        f = self._write(tmp_path, """\
            | col |
            <!-- comment -->
            |-----|
            | val |
        """)
        issues = validate_file(f)
        assert any(i.issue_type == IssueType.HTML_IN_TABLE for i in issues)

    def test_detects_html_comment_in_table_body(self, tmp_path):
        f = self._write(tmp_path, """\
            | col |
            |-----|
            | val |
            <!-- comment -->
            | val2 |
        """)
        issues = validate_file(f)
        assert any(i.issue_type == IssueType.HTML_IN_TABLE for i in issues)

    def test_detects_missing_table_separator(self, tmp_path):
        f = self._write(tmp_path, """\
            | col |
            | val |
        """)
        issues = validate_file(f)
        assert any(i.issue_type == IssueType.MISSING_SEPARATOR for i in issues)

    def test_detects_column_count_mismatch(self, tmp_path):
        f = self._write(tmp_path, """\
            | a | b |
            |---|---|
            | x | y | z |
        """)
        issues = validate_file(f)
        assert any(i.issue_type == IssueType.COLUMN_MISMATCH for i in issues)

    def test_detects_unclosed_code_block(self, tmp_path):
        f = self._write(tmp_path, """\
            Some text.

            ```python
            x = 1
        """)
        issues = validate_file(f)
        assert any(i.issue_type == IssueType.UNCLOSED_CODE_BLOCK for i in issues)

    def test_closed_code_block_is_fine(self, tmp_path):
        f = self._write(tmp_path, """\
            ```python
            x = 1
            ```
        """)
        issues = validate_file(f)
        assert not any(i.issue_type == IssueType.UNCLOSED_CODE_BLOCK for i in issues)

    def test_table_inside_code_block_is_ignored(self, tmp_path):
        f = self._write(tmp_path, """\
            ```
            | col |
            | val |
            ```
        """)
        issues = validate_file(f)
        assert not any(i.issue_type == IssueType.MISSING_SEPARATOR for i in issues)

    def test_issue_contains_correct_file_path(self, tmp_path):
        f = self._write(tmp_path, """\
            ```python
            x = 1
        """)
        issues = validate_file(f)
        assert all(i.file == f for i in issues)

    def test_issue_line_number_is_positive(self, tmp_path):
        f = self._write(tmp_path, """\
            ```python
            x = 1
        """)
        issues = validate_file(f)
        assert all(i.line > 0 for i in issues)
