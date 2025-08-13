from crowler.instruction.instruction_model import Instruction

UNIT_TEST_INSTRUCTION = Instruction(
    instructions=[
        "✅ MANDATORY: Generate exactly one test file per non-test source file.",
        "Use the pytest framework; place all tests under a top-level"
        "`tests/` directory. Name each test file following the pattern:",
        "  `src/path/to/module.py` → `tests/path/to/test_module.py`.",
        "🔧 When replacing behavior or defaults in another module or class, "
        "ALWAYS patch the exact symbol reference used by the module under test.",
        "  • This means: patch the *import binding* inside the module under test, "
        "    NOT the original location where the symbol was defined, unless the "
        "    module calls it directly from that location.",
        "  • Example: if `my_module.py` has `from lib.api import fetch_data`, "
        "    patch `'my_module.fetch_data'`, not `'lib.api.fetch_data'`.",
        "  • If the module does `import lib.api as api` and calls `api.fetch_data()`, "
        "    patch `'my_module.api.fetch_data'`.",
        "  • If the code imports from another internal submodule, patch it where "
        "    it is imported into that submodule, e.g. `'package.submodule.symbol'`.",
        "Never patch the top-level library/module unless the code under test "
        "uses it via a top-level import.",
        "Never reassign `sys.modules[...]` or replace entire modules.",
        "Stub every external dependency (I/O, network, DB, filesystem, OS calls) "
        "by patching the name in the module under test.",
        "If a file imports anything from another file, patch that imported name "
        "as it appears in the importing file, even if the original function/class "
        "is defined elsewhere.",
        "Use pytest fixtures (`tmp_path`, `monkeypatch`) for setup/teardown "
        "and filesystem isolation.",
        "Leverage `pytest.mark.parametrize` to cover multiple input/output cases "
        "in one function.",
        "Keep tests independent—no shared state—by mocking I/O, network, and DB calls.",
        "Assert both return values and side effects (e.g., file writes, DB updates).",
        "Cover normal cases, boundary conditions, and expected exceptions "
        "(use `with pytest.raises(...)`).",
        "Give each test function a clear, descriptive `snake_case` name stating "
        "the behavior under test.",
        "Keep each test focused on a single behavior or scenario for maximum clarity "
        "and maintainability.",
        "No need to confirm print/log output in tests;"
        "evaluate behavior by calling the function and validating expected results.",
    ],
)
