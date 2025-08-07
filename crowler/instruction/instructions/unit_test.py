from crowler.instruction.instruction_model import Instruction

UNIT_TEST_INSTRUCTION = Instruction(
    instructions=[
        "✅ MANDATORY: Generate exactly one test file per non-test source file.",
        "Use the pytest framework; place all tests under a top-level `tests/`"
        "directory.",
        "Name each test file following the pattern:\n"
        "  `src/path/to/module.py` → `tests/path/to/test_module.py`.",
        "🔧 When you need to replace behavior or defaults in another module or"
        "class,",
        "  use `monkeypatch.setattr()` or `unittest.mock.patch()` on the specific",
        "  class, function, or attribute.",
        "**never** reassign `sys.modules[...]` or replace entire modules.",
        "  • Example: `monkeypatch.setattr('crowler.ai.aws.bedrock_config."
        "BedrockClientConfig', 'max_tokens', 4096)`",
        "Stub every external dependency (I/O, network, DB) by patching the"
        "symbol in the module under test:",
        "  • Don’t patch the import path of the library; patch the name as it appears'"
        "in your module.",
        "    E.g. `patch('myapp.module.external_api', fake_api)` not "
        "`patch('external_lib.api', fake_api)`.",
        "Use pytest fixtures (`tmp_path`, `monkeypatch`) for setup/teardown"
        "and filesystem isolation.",
        "Leverage `pytest.mark.parametrize` to cover multiple input/output"
        "cases in one function.",
        "Keep tests independent—no shared state—by mocking I/O, network, and DB calls.",
        "Assert both return values and side effects (e.g., file writes, DB updates).",
        "Cover normal cases, boundary conditions, and expected exceptions (use"
        "`with pytest.raises(...)`).",
        "Give each test function a clear, descriptive `snake_case` name stating"
        "the behavior under test.",
        "Keep each test focused on a single behavior or scenario for maximum"
        "clarity and maintainability.",
        "No need to confirm print and logs in tests, just evaluate if the function"
        "works as expected by calling it and validating the expected behavior",
    ],
)
