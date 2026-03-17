"""Tests for CLI."""

from click.testing import CliRunner

from feedkit import __version__
from feedkit.__main__ import main

runner = CliRunner()


def test_cli_version():
    result = runner.invoke(main, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_help():
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "search" in result.output
    assert "subscribe" in result.output
    assert "collect" in result.output


def test_cli_search_help():
    result = runner.invoke(main, ["search", "--help"])
    assert result.exit_code == 0
    assert "--category" in result.output
    assert "--language" in result.output


def test_cli_categories():
    result = runner.invoke(main, ["categories"])
    assert result.exit_code == 0
    assert "technology" in result.output


def test_cli_stats():
    result = runner.invoke(main, ["stats"])
    assert result.exit_code == 0
    assert "Catalog" in result.output


def test_cli_search_json():
    result = runner.invoke(main, ["search", "cloud", "-j"])
    assert result.exit_code == 0
    import json
    data = json.loads(result.output)
    assert isinstance(data, list)
