from crowler.instruction.instruction_model import Instruction


RESPONSE_FORMAT_INSTRUCTION = Instruction(
    instructions=[
        # ───────────── mandatory rules ─────────────
        "✅ MANDATORY: Emit one fenced code block *per file* using"
        "exactly this pattern:\n"
        '   ~~~"relative/path.ext"  (opening fence + quoted path)\n'
        "   …file contents…\n"
        "   ~~~                     (closing fence)\n"
        "   Absolutely nothing may appear outside those fences.",
        "🔹 The opening fence is three tildes (~~~) at column 0,"
        "followed immediately by "
        "a quote (\", ', or `), the relative path, and the matching"
        "quote—no spaces or language tags.",
        "🔹 Everything until the closing fence is treated verbatim as UTF-8 text.",
        "",
        # ───────────── things NOT to do ────────────
        "🧼 DO NOT base64-encode, escape, or otherwise transform the file contents.",
        "🚫 DO NOT wrap multiple files in JSON; the parser expects *separate* blocks.",
        "🚫 No comments, markdown headings, or prose before, between,"
        "or after the blocks.",
        '🚫 Paths must be relative and must not escape the sandbox (e.g., avoid "../").',
        "",
        # ───────────── examples ───────────────
        "📄 Example – single file:\n" '~~~"main.py"\n' "print('hello world')\n" "~~~",
        "📄 Example – three files:\n"
        '~~~"a.py"\nA = 1\n~~~\n'
        "~~~'b.txt'\nHello\n~~~\n"
        "~~~`dir with space/data.txt`\nX\n~~~",
        "",
    ]
)
