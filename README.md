# crowler

Command-line toolkit for managing prompts, files, and AI-powered workflows!

<div align="center">
  <img src="https://raw.githubusercontent.com/gardusig/crowler-cli/main/media/itachi.png" alt="eat" height="200" />
</div>

## 📚 Table of Contents

- [crowler](#crowler)
  - [📚 Table of Contents](#-table-of-contents)
  - [🔄 Example Workflow](#-example-workflow)
  - [🚀 Installation \& Setup](#-installation--setup)
    - [macOS: Python \& Homebrew](#macos-python--homebrew)
    - [Project Setup](#project-setup)
    - [Self improvement loop](#self-improvement-loop)
  - [🔐 Environment Configuration](#-environment-configuration)
  - [🛠️ CLI Usage](#️-cli-usage)
    - [💡 Prompt Management](#-prompt-management)
    - [📁 File Management](#-file-management)
    - [⚙️ Processing Queue](#️-processing-queue)
    - [🤖 Code Generation](#-code-generation)
    - [🌎 Global Commands](#-global-commands)

## 🔄 Example Workflow

Let's say you want to generate tests for your codebase:

```
crowler process add src/my_module.py
crowler prompt add "Write comprehensive unit tests."
crowler code unit-test
```

Or, to quickly create a README:

```
crowler code readme
```

## 🚀 Installation & Setup

### macOS: Python & Homebrew

```bash
brew install python
python3 -m pip install --upgrade pip
python3 -m pip install virtualenv
```

### Project Setup

Clone and set up your environment:

```bash
python3 -m venv venv
source venv/bin/activate
python3 -m pip install -e .
python3 -m pip install -e ".[dev]"
```

### Self improvement loop

Check if there's any failing test:

```
pytest -v .
```

In case there is, try using crowler to fix itself:

```
pytest -v . | pbcopy && \
python -m crowler.main prompt clear && \
python -m crowler.main paste && \
python -m crowler.main show && \
python -m crowler.main code unit-test --force
```

## 🔐 Environment Configuration

crowler uses OpenAI (or other LLM) APIs. Set your API key in a `.env` file at the project root:

```env
OPENAI_API_KEY=sk-...
```

Or export it in your shell:

```bash
export OPENAI_API_KEY=sk-...
```

## 🛠️ CLI Usage

Invoke crowler CLI with:

```bash
python -m crowler [COMMANDS...]
```

Or, if installed as a script:

```bash
crowler [COMMANDS...]
```

### 💡 Prompt Management

Manage your prompt history for AI interactions:

- **Add a prompt:**
  ```
  crowler prompt add "Summarize the following text"
  ```

- **Remove a prompt:**
  ```
  crowler prompt remove "Summarize the following text"
  ```

- **List all prompts:**
  ```
  crowler prompt list
  ```

- **Undo last prompt change:**
  ```
  crowler prompt undo
  ```

- **Clear all prompts:**
  ```
  crowler prompt clear
  ```

- **Add prompt from clipboard:**
  ```
  crowler clipboard
  ```

### 📁 File Management

Track files you want to share with your LLM:

- **Add a file or directory:**
  ```
  crowler file add path/to/file_or_folder
  ```

- **Remove a file:**
  ```
  crowler file remove path/to/file
  ```

- **List shared files:**
  ```
  crowler file list
  ```

- **Undo last file change:**
  ```
  crowler file undo
  ```

- **Clear all shared files:**
  ```
  crowler file clear
  ```

### ⚙️ Processing Queue

Queue files for processing (e.g., for test generation):

- **Add file(s) to process:**
  ```
  crowler process add path/to/file_or_folder
  ```

- **Remove file from process queue:**
  ```
  crowler process remove path/to/file
  ```

- **List processing files:**
  ```
  crowler process list
  ```

- **Undo last processing change:**
  ```
  crowler process undo
  ```

- **Clear processing queue:**
  ```
  crowler process clear
  ```

### 🤖 Code Generation

Let crowler and your LLM do the heavy lifting:

- **Generate unit tests for queued files:**
  ```
  crowler code unit-test
  ```

- **Generate a README.md for your project:**
  ```
  crowler code readme
  ```

  Add `--force` to overwrite existing files without confirmation.

### 🌎 Global Commands

- **Show all prompts, shared files, and processing files:**
  ```
  crowler show
  ```

- **Clear everything (prompts, shared files, processing files):**
  ```
  crowler clear
  ```
