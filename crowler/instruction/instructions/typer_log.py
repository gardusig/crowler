from crowler.instruction.instruction_model import Instruction

TYPER_LOG_INSTRUCTION = Instruction(
    instructions=[
        # ───────────── mandatory rules ─────────────
        "✅ MANDATORY: Replace all ad-hoc `print()` calls with"
        "`typer.echo()` or `typer.secho()` calls so that logging"
        "honors Typer/Click flags.",
        "🔹 Use `typer.secho(..., fg=...)` to add color:"
        "green for success/info (✅), yellow for warnings (⚠️),"
        "red for errors (❌)",
        "🔹 Prefix messages with a single emoji to indicate level,"
        "then a short descriptive text, e.g.:\n"
        "    • `typer.secho(f'✅ Loading config: {config_path}', fg='green')`\n"
        "    • `typer.secho('⚠️  Missing optional field, "
        "using default', fg='yellow')`\n"
        "    • `typer.secho('❌  Failed to connect to DB',"
        "fg='red', err=True)`",
        "",
        # ───────────── where to log ─────────────
        "📍 Focus only on exit of every public command function"
        "(after major steps, whether it's an error or an informational log).",
        "Avoid too noisy logs like informing about inner internal operations.",
        "Like after any file I/O, network call, or subprocess invocation.",
        "📍 Inside `except` blocks to surface stack-level context with"
        "`err=True` for stderr.",
        "📍 Around key state changes: configuration load, cache clear,"
        "DB write, test generation, etc.",
        "Remove or adapt excessive logs, like informative that may already be present.",
        "",
        # ───────────── formatting & style ─────────────
        "🎨 Keep messages concise (one sentence plus context), no stack"
        "traces or raw objects—format data neatly.",
        "🚫 DO NOT leave bare `print()` or commented‐out debug lines"
        "in the final patch.",
        "🚫 DO NOT over-log: one log per logical operation is enough.",
    ],
)
