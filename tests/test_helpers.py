"""Tests for qtshadcn helpers."""

from pathlib import Path

from qtshadcn.common.helpers import _atomic_write, _looks_like_jinja


def test_looks_like_jinja():
    assert _looks_like_jinja("{{ foo }}") is True
    assert _looks_like_jinja("{% block %}") is True
    assert _looks_like_jinja("QWidget { color: red; }") is False


def test_atomic_write(tmp_path: Path):
    target_file = tmp_path / "test.json"
    _atomic_write(target_file, '{"test": 123}')

    assert target_file.exists()
    assert target_file.read_text(encoding="utf-8") == '{"test": 123}'
    assert not (tmp_path / "test.json.tmp").exists()
