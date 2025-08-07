import pytest
import sys
from pathlib import Path

import builtins

import crowler.util.session_util as session_util


@pytest.fixture(autouse=True)
def patch_cache_dir(tmp_path, monkeypatch):
    # Patch CACHE_DIR to use a temp directory for all tests
    monkeypatch.setattr(session_util, "CACHE_DIR", tmp_path)
    # Ensure directory exists
    tmp_path.mkdir(parents=True, exist_ok=True)


def test_create_session_file_uses_cache_dir(monkeypatch):
    # Patch get_session_id to return a fixed value
    monkeypatch.setattr(session_util, "get_session_id", lambda: "abc12345")
    name = "mysession"
    expected = session_util.CACHE_DIR / "mysession.abc12345.json"
    result = session_util.create_session_file(name)
    assert result == expected


@pytest.mark.parametrize(
    "input_text,expected_hash",
    [
        ("hello", session_util.hashlib.md5("hello".encode()).hexdigest()[:8]),
        ("", session_util.hashlib.md5("".encode()).hexdigest()[:8]),
        ("1234567890", session_util.hashlib.md5("1234567890".encode()).hexdigest()[:8]),
    ],
)
def test__hash_returns_truncated_md5(input_text, expected_hash):
    assert session_util._hash(input_text) == expected_hash


def test_get_session_id_prefers_history_session_id(monkeypatch):
    monkeypatch.setenv("HISTORY_SESSION_ID", "mytestsession")
    monkeypatch.setattr(session_util, "_try_pty", lambda: None)
    monkeypatch.delenv("WT_SESSION", raising=False)
    monkeypatch.setattr(session_util.os, "getppid", lambda: 12345)
    result = session_util.get_session_id()
    assert result == session_util._hash("mytestsession")


def test_get_session_id_uses_try_pty(monkeypatch):
    monkeypatch.delenv("HISTORY_SESSION_ID", raising=False)
    monkeypatch.setattr(session_util, "_try_pty", lambda: "/dev/pts/7")
    monkeypatch.delenv("WT_SESSION", raising=False)
    monkeypatch.setattr(session_util.os, "getppid", lambda: 12345)
    result = session_util.get_session_id()
    assert result == session_util._hash("/dev/pts/7")


def test_get_session_id_uses_wt_session(monkeypatch):
    monkeypatch.delenv("HISTORY_SESSION_ID", raising=False)
    monkeypatch.setattr(session_util, "_try_pty", lambda: None)
    monkeypatch.setenv("WT_SESSION", "windows-terminal-session")
    monkeypatch.setattr(session_util.os, "getppid", lambda: 12345)
    result = session_util.get_session_id()
    assert result == session_util._hash("windows-terminal-session")


def test_get_session_id_fallbacks_to_parent_pid(monkeypatch):
    monkeypatch.delenv("HISTORY_SESSION_ID", raising=False)
    monkeypatch.setattr(session_util, "_try_pty", lambda: None)
    monkeypatch.delenv("WT_SESSION", raising=False)
    monkeypatch.setattr(session_util.os, "getppid", lambda: 54321)
    result = session_util.get_session_id()
    assert result == session_util._hash("54321")


def test__try_pty_success(monkeypatch):
    class DummyStdin:
        def fileno(self):
            return 42

    def fake_ttyname(fd):
        assert fd == 42
        return "/dev/pts/9"

    monkeypatch.setattr(session_util.sys, "stdin", DummyStdin())
    monkeypatch.setattr(session_util.os, "ttyname", fake_ttyname)
    assert session_util._try_pty() == "/dev/pts/9"


def test__try_pty_failure(monkeypatch):
    class DummyStdin:
        def fileno(self):
            raise OSError("no fileno")

    monkeypatch.setattr(session_util.sys, "stdin", DummyStdin())
    # Even if os.ttyname is called, it should not matter
    monkeypatch.setattr(
        session_util.os, "ttyname", lambda fd: "/dev/pts/shouldnotbecalled"
    )
    assert session_util._try_pty() is None


def test__try_pty_ttyname_exception(monkeypatch):
    """Test that _try_pty handles exceptions from os.ttyname."""

    class DummyStdin:
        def fileno(self):
            return 42

    def fake_ttyname(fd):
        raise OSError("ttyname error")

    monkeypatch.setattr(session_util.sys, "stdin", DummyStdin())
    monkeypatch.setattr(session_util.os, "ttyname", fake_ttyname)

    # Should catch the exception and return None
    assert session_util._try_pty() is None


def test_get_session_id_exception_handling(monkeypatch):
    """Test exception handling in get_session_id when all methods fail."""

    def raise_exception(*args, **kwargs):
        raise Exception("Test exception")

    monkeypatch.setattr(session_util, "_try_pty", raise_exception)
    monkeypatch.setattr(session_util.os, "getenv", raise_exception)
    monkeypatch.setattr(session_util.os, "getppid", raise_exception)

    # The function should raise an exception after logging
    with pytest.raises(Exception, match="Test exception"):
        session_util.get_session_id()
