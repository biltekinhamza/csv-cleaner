import pytest

from csv_cleaner import CleanStats, clean_cell, clean_file, clean_rows, main, normalize_header


def test_normalize_header():
    assert normalize_header("  First   Name ") == "first_name"


def test_clean_cell_trims_and_collapses_spaces():
    assert clean_cell("  John    Smith ") == "John Smith"


def test_clean_rows_removes_empty_and_duplicate_rows():
    rows = [
        ["Name", "City"],
        ["Ann", "Berlin"],
        ["", ""],
        ["  Ann ", "Berlin"],  # duplicate once trimmed
        ["Bob", "Paris"],
    ]

    cleaned, stats = clean_rows(rows)

    assert cleaned == [["name", "city"], ["Ann", "Berlin"], ["Bob", "Paris"]]
    assert stats == CleanStats(rows_in=4, rows_out=2, empty_removed=1, duplicates_removed=1)


def test_short_rows_are_padded():
    cleaned, _ = clean_rows([["a", "b", "c"], ["1"]])

    assert cleaned[1] == ["1", "", ""]


def test_row_with_too_many_columns_raises():
    with pytest.raises(ValueError, match="line 2"):
        clean_rows([["a"], ["1", "2"]])


def test_empty_input_returns_empty_result():
    assert clean_rows([]) == ([], CleanStats())


def test_clean_file_roundtrip_handles_excel_bom(tmp_path):
    source = tmp_path / "in.csv"
    target = tmp_path / "out.csv"
    source.write_text("﻿Name , Email\n Ann ,ann@example.com\n,\n", encoding="utf-8")

    stats = clean_file(source, target)

    assert target.read_text(encoding="utf-8").splitlines() == ["name,email", "Ann,ann@example.com"]
    assert stats.rows_out == 1


def test_cli_reports_missing_file(tmp_path, capsys):
    exit_code = main([str(tmp_path / "nope.csv")])

    assert exit_code == 1
    assert "file not found" in capsys.readouterr().out


def test_cli_default_output_name(tmp_path, capsys):
    source = tmp_path / "data.csv"
    source.write_text("A,B\n1,2\n", encoding="utf-8")

    assert main([str(source)]) == 0
    assert (tmp_path / "data_clean.csv").exists()
