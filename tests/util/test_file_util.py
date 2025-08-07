import pytest
from pathlib import Path
from collections import OrderedDict
from typing import Any

import crowler.util.file_util as file_util


@pytest.mark.parametrize(
    "path_part,patterns,expected",
    [
        ("__pycache__", file_util.DEFAULT_IGNORES, True),
        ("foo.pyc", file_util.DEFAULT_IGNORES, True),
        ("foo.txt", file_util.DEFAULT_IGNORES, False),
        ("LICENSE", file_util.DEFAULT_IGNORES, True),
        ("randomfile", [], False),
        ("venv", file_util.DEFAULT_IGNORES, True),
        ("foo/bar.py", ["foo/bar.py"], True),
    ],
)
def test_should_ignore(path_part, patterns, expected):
    assert file_util.should_ignore(path_part, patterns) == expected


@pytest.mark.parametrize(
    "path_part,patterns,expected",
    [
        # Additional edge cases
        ("", file_util.DEFAULT_IGNORES, False),  # Empty path
        (".", file_util.DEFAULT_IGNORES, False),  # Current directory
        ("..", file_util.DEFAULT_IGNORES, False),  # Parent directory
        # Patterns with wildcards at different positions
        (
            "foo.jpg",
            file_util.DEFAULT_IGNORES,
            False,
        ),  # Changed from True to False - ? requires exactly one character
        ("foo.jpeg", file_util.DEFAULT_IGNORES, True),  # This matches *.jpe?g pattern
        ("test.py", ["test.*"], True),
        ("test.anything", ["test.*"], True),
    ],
)
def test_should_ignore_edge_cases(path_part, patterns, expected):
    assert file_util.should_ignore(path_part, patterns) == expected


def test_get_all_files_returns_empty_for_nonexistent(monkeypatch, tmp_path):
    nonexist = tmp_path / "doesnotexist"
    files = file_util.get_all_files(nonexist)
    assert files == []


def test_get_all_files_returns_file_for_file(monkeypatch, tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hi")
    files = file_util.get_all_files(f)
    assert files == [str(f)]


def test_get_all_files_ignores_patterns(tmp_path):
    (tmp_path / "__pycache__").mkdir()
    (tmp_path / "foo.pyc").write_text("x")
    (tmp_path / "bar.txt").write_text("y")
    (tmp_path / "baz.py").write_text("z")
    files = file_util.get_all_files(tmp_path)
    assert str(tmp_path / "bar.txt") in files
    assert str(tmp_path / "baz.py") in files
    assert all("__pycache__" not in f and not f.endswith(".pyc") for f in files)


def test_stringify_file_contents_empty(monkeypatch):
    assert file_util.stringify_file_contents([]) == []


def test_stringify_file_contents_reads_files(tmp_path, monkeypatch):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("foo")
    f2.write_text("bar")
    files = [str(f1), str(f2)]
    result = file_util.stringify_file_contents(files, label="Test")
    assert result[0] == "📁 Test:"
    assert any("foo" in s for s in result)
    assert any("bar" in s for s in result)


def test_stringify_file_contents_checks_exact_content(tmp_path):
    f1 = tmp_path / "a.txt"
    f2 = tmp_path / "b.txt"
    f1.write_text("foo")
    f2.write_text("bar")
    files = [str(f1), str(f2)]
    result = file_util.stringify_file_contents(files, label="Test")

    # Check exact content
    assert len(result) == 3  # Header + 2 files
    assert result[0] == "📁 Test:"
    assert f"File: {f1}\n```\nfoo\n```" in result
    assert f"File: {f2}\n```\nbar\n```" in result


def test_stringify_file_contents_handles_exception(monkeypatch, tmp_path):
    def bad_read(*a: Any, **k: Any) -> str:
        raise Exception("fail")

    monkeypatch.setattr(file_util, "stringify_file_content", bad_read)
    f = tmp_path / "bad.txt"
    f.write_text("x")
    result = file_util.stringify_file_contents([str(f)])
    assert result == ["📁 Files:"]


def test_stringify_file_content_reads_file(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello\n")
    out = file_util.stringify_file_content(f)
    assert out == "hello"


def test_stringify_file_content_too_big(tmp_path):
    f = tmp_path / "big.txt"
    f.write_bytes(b"x" * (file_util._MAX_MB * 1024 * 1024 + 1))
    out = file_util.stringify_file_content(f)
    assert out == ""


def test_stringify_file_content_handles_exception(monkeypatch):
    class DummyPath:
        def stat(self) -> Any:
            raise Exception("fail")

        def __fspath__(self) -> str:
            return "dummy"

    # Provide a type hint to satisfy mypy: str | Path
    dummy_path: "str | Path" = DummyPath()  # type: ignore
    out = file_util.stringify_file_content(dummy_path)
    assert out == ""


def test_rewrite_files_force_true(monkeypatch, tmp_path):
    called = []

    def fake_rewrite_file(path, content):
        called.append((path, content))

    monkeypatch.setattr(file_util, "rewrite_file", fake_rewrite_file)
    monkeypatch.setattr(file_util.typer, "secho", lambda *a, **k: None)
    files = OrderedDict([("foo.txt", "abc"), ("bar.txt", "def")])
    file_util.rewrite_files(files, force=True)
    assert ("foo.txt", "abc") in called and ("bar.txt", "def") in called


def test_rewrite_files_force_false_confirm(monkeypatch):
    called = []
    monkeypatch.setattr(file_util, "rewrite_file", lambda p, c: called.append((p, c)))
    monkeypatch.setattr(file_util.typer, "secho", lambda *a, **k: None)
    confirms = iter([True, False])
    monkeypatch.setattr(file_util.typer, "confirm", lambda msg: next(confirms))
    files = OrderedDict([("foo.txt", "abc"), ("bar.txt", "def")])
    file_util.rewrite_files(files, force=False)
    assert ("foo.txt", "abc") in called
    assert ("bar.txt", "def") not in called


def test_rewrite_file_writes(tmp_path):
    f = tmp_path / "x/y/z.txt"
    content = "hello"
    file_util.rewrite_file(str(f), content)
    assert f.read_text() == content


def test_rewrite_file_handles_exception(monkeypatch, tmp_path):
    class DummyPath:
        parent = type("P", (), {"mkdir": staticmethod(lambda **k: None)})

        def expanduser(self):
            return self

        def write_text(self, *a, **k):
            raise Exception("fail")

    monkeypatch.setattr(file_util, "Path", lambda x: DummyPath())
    file_util.rewrite_file("foo.txt", "abc")  # Should not raise


def test_find_repo_root_git(monkeypatch, tmp_path):
    # Simplified version of the test, removing unused code
    monkeypatch.setattr(
        file_util.subprocess,
        "check_output",
        lambda *a, **k: bytes(str(tmp_path), "utf-8"),
    )
    out = file_util.find_repo_root()
    assert out == tmp_path


def test_find_repo_root_fallback(monkeypatch):
    monkeypatch.setattr(
        file_util.subprocess,
        "check_output",
        lambda *a, **k: (_ for _ in ()).throw(Exception("fail")),
    )
    cwd = Path.cwd()
    out = file_util.find_repo_root()
    assert out == cwd


def test_source_to_test_path_success(tmp_path):
    repo_root = tmp_path
    src = tmp_path / "crowler" / "cli" / "app.py"
    (tmp_path / "crowler" / "cli").mkdir(parents=True)
    src.write_text("x")
    out = file_util.source_to_test_path(src, repo_root)

    # Check the exact expected path structure
    expected_path = repo_root / "tests" / "cli" / "test_app.py"
    assert out == expected_path


def test_source_to_test_path_custom_tests_dir(tmp_path):
    repo_root = tmp_path
    src = tmp_path / "crowler" / "cli" / "app.py"
    (tmp_path / "crowler" / "cli").mkdir(parents=True)
    src.write_text("x")
    out = file_util.source_to_test_path(src, repo_root, tests_dir="custom_tests")

    # Check the expected path with custom tests directory
    expected_path = repo_root / "custom_tests" / "cli" / "test_app.py"
    assert out == expected_path


def test_source_to_test_path_too_short(tmp_path):
    repo_root = tmp_path
    src = tmp_path / "foo.py"
    src.write_text("x")
    with pytest.raises(Exception):
        file_util.source_to_test_path(src, repo_root)
