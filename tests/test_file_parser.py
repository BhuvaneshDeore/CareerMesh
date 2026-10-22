"""
tests/test_file_parser.py - Unit tests for file parser service
"""

import pytest
from pathlib import Path
from services.file_parser import parse_text_input, parse_file, FileParsingError


def test_parse_text_input_valid():
    text = "  Sample candidate resume text  "
    parsed = parse_text_input(text)
    assert parsed == "Sample candidate resume text"


def test_parse_text_input_empty():
    with pytest.raises(FileParsingError):
        parse_text_input("   \n\t  ")


def test_parse_file_missing(tmp_path):
    missing_file = tmp_path / "non_existent.pdf"
    with pytest.raises(FileParsingError) as exc_info:
        parse_file(missing_file)
    assert "not found" in str(exc_info.value).lower()


def test_parse_file_unsupported_extension(tmp_path):
    bad_file = tmp_path / "image.png"
    bad_file.write_bytes(b"dummy")
    with pytest.raises(FileParsingError) as exc_info:
        parse_file(bad_file)
    assert "unsupported" in str(exc_info.value).lower()


def test_parse_file_empty(tmp_path):
    empty_txt = tmp_path / "empty.txt"
    empty_txt.write_text("", encoding="utf-8")
    with pytest.raises(FileParsingError) as exc_info:
        parse_file(empty_txt)
    assert "empty" in str(exc_info.value).lower()


def test_parse_txt_file_valid(tmp_path):
    txt_file = tmp_path / "resume.txt"
    txt_file.write_text("Valid resume content here", encoding="utf-8")
    content, meta = parse_file(txt_file)
    assert content == "Valid resume content here"
    assert meta["extension"] == ".txt"
