# from __future__ import annotations

# import os
# import subprocess
# from dataclasses import dataclass
# from pathlib import Path
# from typing import Mapping

# import typer


# @dataclass(slots=True)
# class CommandResult:
#     code: int
#     out: str
#     err: str


# class CommandRunner:
#     """Run commands inside *base_path* (optionally inside its venv)."""

#     def __init__(self, base_path: Path | str) -> None:
#         self.base_path = Path(base_path).resolve(strict=True)

#     # ──────────────────────────────────────────────────────────
#     def get_startup_commands(self) -> list[str]:
#         venv_bin = self.base_path / "venv" / "bin" / "activate"
#         return [f"source {venv_bin}"]

#     def _run(
#         self,
#         cmd_list: list[str],
#         env: Mapping[str, str] | None = None,
#         check: bool = False,
#     ) -> CommandResult:
#         commands = self.get_startup_commands()
#         commands.extend(cmd_list)

#         cmd = " && ".join(commands)

#         try:
#             proc = subprocess.run(
#                 cmd,
#                 cwd=self.base_path,
#                 env={**os.environ, **(env or {})},
#                 text=True,
#                 capture_output=True,
#                 check=check,
#                 shell=True,
#             )
#             result = CommandResult(
#                 proc.returncode, proc.stdout.strip(), proc.stderr.strip()
#             )
#             # Logging only on exit of public command functions, not here.
#             return result
#         except Exception as exc:
#             typer.secho(
#                 f"❌  Exception running command: {cmd} ({exc})", fg="red", err=True
#             )
#             return CommandResult(-1, "", str(exc))

#     # ───────────── public helpers ─────────────
#     def pytest(self, paths: list[str]) -> CommandResult:
#         paths = [str(p) for p in paths] or ["tests"]
#         result = self._run(["pytest", *paths])
#         if result.code == 0:
#             typer.secho("✅ Pytest completed successfully.", fg="green")
#         else:
#             typer.secho("❌  Pytest failed.", fg="red", err=True)
#         return result

#     def black(self, *targets: str, use_venv: bool = True) -> CommandResult:
#         result = self._run(["black", *targets])
#         if result.code == 0:
#             typer.secho("✅ Black formatting completed.", fg="green")
#         else:
#             typer.secho("❌  Black formatting failed.", fg="red", err=True)
#         return result

#     def custom(
#         self,
#         *cmd: str,
#         env: Mapping[str, str] | None = None,
#         use_venv: bool = True,
#     ) -> CommandResult:
#         result = self._run([str(c) for c in cmd], env=env)
#         if result.code == 0:
#             typer.secho(f"✅ Custom command completed: {' '.join(cmd)}", fg="green")
#         else:
#             typer.secho(
#                 f"❌  Custom command failed: {' '.join(cmd)}", fg="red", err=True
#             )
#         return result
