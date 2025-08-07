from crowler.instruction.instruction_model import Instruction
import pytest
from collections import OrderedDict

import crowler.util.string_util as string_util


@pytest.fixture(autouse=True)
def patch_print(monkeypatch):
    # Patch print to capture print statements for assertions if needed
    printed = []

    def fake_print(*args, **kwargs):
        printed.append((args, kwargs))

    monkeypatch.setattr(string_util, "print", fake_print)
    return printed


@pytest.mark.parametrize(
    "response,expected",
    [
        (
            # Single code block, double quotes
            '~~~"foo.py"\nprint("hi")\n~~~',
            OrderedDict([("foo.py", '\nprint("hi")\n')]),
        ),
        # (
        #     # Single code block, single quotes
        #     "~~~'bar.txt'\nhello\n~~~",
        #     OrderedDict([("bar.txt", "\nhello\n")]),
        # ),
        (
            # Single code block, backticks
            "~~~`baz.md`\n# Title\n~~~",
            OrderedDict([("baz.md", "\n# Title\n")]),
        ),
        (
            # Multiple code blocks
            '~~~"a.py"\nA\n~~~\n~~~"b.py"\nB\n~~~',
            OrderedDict([("a.py", "\nA\n"), ("b.py", "\nB\n")]),
        ),
        (
            # Duplicate file path (should overwrite)
            '~~~"dup.py"\nfirst\n~~~\n~~~"dup.py"\nsecond\n~~~',
            OrderedDict([("dup.py", "\nsecond\n")]),
        ),
        (
            # No code blocks
            "No code here",
            OrderedDict(),
        ),
        (
            # Code block with empty path (should skip)
            '~~~""\nnope\n~~~',
            OrderedDict(),
        ),
    ],
)
def test_parse_code_response_basic(response, expected, patch_print):
    files = string_util.parse_code_response(response)
    assert files == expected


@pytest.mark.parametrize(
    "response,root,paths,should_accept",
    [
        (
            # Path inside root
            '~~~"subdir/file.py"\ncode\n~~~',
            "sandbox",
            ["subdir/file.py"],
            [True],
        ),
        (
            # Path outside root (../)
            '~~~"../evil.py"\nmalicious\n~~~',
            "sandbox",
            ["../evil.py"],
            [False],
        ),
        (
            # Path inside root, absolute
            '~~~"/sandbox/ok.py"\ncode\n~~~',
            "/sandbox",
            ["/sandbox/ok.py"],
            [True],
        ),
        (
            # Path outside root, absolute
            '~~~"/etc/passwd"\nrooted\n~~~',
            "/sandbox",
            ["/etc/passwd"],
            [False],
        ),
    ],
)
def test_parse_code_response_with_root(
    tmp_path, response, root, paths, should_accept, patch_print, monkeypatch
):
    # Patch Path.resolve().is_relative_to to simulate sandboxing
    orig_resolve = string_util.Path.resolve
    orig_is_relative_to = getattr(string_util.Path, "is_relative_to", None)

    def fake_resolve(self):
        # Simulate resolve: just join with tmp_path/root
        if str(self).startswith("/"):
            return tmp_path.joinpath(str(self).lstrip("/"))
        return tmp_path.joinpath(root, str(self))

    def fake_is_relative_to(self, base):
        # Accept if path does not contain ".." or is under base
        return ".." not in str(self) and (str(base) in str(self))

    monkeypatch.setattr(string_util.Path, "resolve", fake_resolve)
    monkeypatch.setattr(string_util.Path, "is_relative_to", fake_is_relative_to)

    files = string_util.parse_code_response(response, root=tmp_path / root)
    for p, accept in zip(paths, should_accept):
        if accept:
            assert p in files or p.lstrip("/") in files or (root + "/" + p) in files
        else:
            assert not files

    # Restore Path methods (pytest will undo monkeypatch, but for clarity)
    if orig_is_relative_to:
        monkeypatch.setattr(string_util.Path, "is_relative_to", orig_is_relative_to)
    monkeypatch.setattr(string_util.Path, "resolve", orig_resolve)


def test_parse_code_response_prints_for_no_files(patch_print):
    files = string_util.parse_code_response("no blocks here")
    assert files == OrderedDict()
    assert any("No file/code blocks found" in str(args[0]) for args, _ in patch_print)


def test_parse_code_response_prints_for_duplicate(monkeypatch, patch_print):
    # Accept all paths as inside root
    monkeypatch.setattr(string_util.Path, "resolve", lambda self: self)
    monkeypatch.setattr(string_util.Path, "is_relative_to", lambda self, base: True)
    response = '~~~"dup.py"\nA\n~~~\n~~~"dup.py"\nB\n~~~'
    files = string_util.parse_code_response(response)
    assert files["dup.py"] == "\nB\n"
    assert any("Duplicate file path" in str(args[0]) for args, _ in patch_print)


def test_parse_code_response_prints_for_extracted(monkeypatch, patch_print):
    monkeypatch.setattr(string_util.Path, "resolve", lambda self: self)
    monkeypatch.setattr(string_util.Path, "is_relative_to", lambda self, base: True)
    response = '~~~"foo.py"\nprint()\n~~~'
    files = string_util.parse_code_response(response)
    assert files["foo.py"] == "\nprint()\n"


def test_parse_code_response_rejects_path_outside_root(monkeypatch, patch_print):
    # Simulate is_relative_to returning False
    monkeypatch.setattr(string_util.Path, "resolve", lambda self: self)
    monkeypatch.setattr(string_util.Path, "is_relative_to", lambda self, base: False)
    response = '~~~"../evil.py"\nmalicious\n~~~'
    files = string_util.parse_code_response(response, root="sandbox")
    assert files == OrderedDict()
    assert any(
        "Rejected path outside root sandbox" in str(args[0]) for args, _ in patch_print
    )


def test_get_instruction_strings_none():
    # Should return empty list if instructions is None
    assert string_util.get_instruction_strings(None) == []


def test_get_instruction_strings_empty():
    # Should return empty list if instructions is []
    assert string_util.get_instruction_strings([]) == []


def test_get_instruction_strings_flatten(monkeypatch):
    inst1 = Instruction(instructions=["a", "b"])
    inst2 = Instruction(instructions=["c"])
    result = string_util.get_instruction_strings([inst1, inst2])
    assert result == ["a", "b", "c"]
