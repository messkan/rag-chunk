"""Bare invocation (no subcommand) must fail instead of exiting 0."""

import pytest

from src.cli import main


def test_bare_invocation_exits_nonzero(monkeypatch, capsys):
    """Running `rag-chunk` with no subcommand prints help and exits 2."""
    monkeypatch.setattr("sys.argv", ["rag-chunk"])
    with pytest.raises(SystemExit) as excinfo:
        main()
    assert excinfo.value.code == 2
    assert "analyze" in capsys.readouterr().out
