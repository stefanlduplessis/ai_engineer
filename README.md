# AIEngineer
1. **Project Structure Overview**
2. **Installation and Setup with Poetry**
3. **Using the CLI Tool**
4. **Importing and Using the Library in Python Code**
5. **Additional Tips**

---

## 1. Project Structure Overview

Assuming you followed the initial setup with Poetry and refactored your CLI using Typer, your project structure might look like this:

```
my_project/
├── pyproject.toml
├── poetry.lock
├── README.md
├── src/
│   ├── ai_engineer/
│   │   ├── __init__.py
│   │   └── services/
│   │       ├── __init__.py
│   │       └── openai_engineer.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
└── .env
```

- **`src/ai_engineer/services/openai_engineer.py`**: Contains the `OpenAIEngineer` class.
- **`src/main.py`**: Contains the Typer-based CLI application.
- **`pyproject.toml`**: Configuration file for Poetry.
- **`.env`**: Environment variables (e.g., `OPENAI_API_KEY`).

---

## 2. Installation and Setup with Poetry


### **a. Install the Package Locally**

```bash
poetry install
```

This command installs the dependencies and sets up the CLI script defined in `[tool.poetry.scripts]`.

### **b. Activate the Virtual Environment**

```bash
poetry shell
```

---

## 3. Using the CLI Tool

Once installed, you can use your CLI tool (`ai-engineer-cli`) directly from the terminal.

### **a. Basic Usage**

```bash
ai-engineer-cli main /path/to/project "Implement feature X" "development"
```

**Arguments:**

1. **`project_path`**: Path to the project directory.
2. **`prompt`**: Action prompt for the AI Engineer.
3. **`mode`**: System mode for the AI Engineer.

### **b. Using Optional Arguments**

You can also provide optional arguments as needed:

```bash
my-cli main /path/to/project "Implement feature X" "creator" \
    --api_key YOUR_API_KEY \
    --auto_file_discovery \
    --overwrite \
    --max_chat_iterations 50
```

**Options:**

- **`--api_key`**: Your OpenAI API key. If not provided, the CLI will attempt to read `OPENAI_API_KEY` from the `.env` file or environment variables.
- **`--auto_file_discovery`**: Enable auto-file-discovery context.
- **`--reuse_auto_file_discovery`**: Reuse the auto-file-discovery context from the previous run.
- **`--gitignore_file_path`**: Relative path of `.gitignore` (default: `.gitignore`).
- **`--overwrite`**: Overwrite existing files.
- **`--max_chat_iterations`**: Maximum chat iterations for the AI model (default: `25`).

### **c. Help Command**

Typer automatically generates help messages. Use the `--help` flag to see available commands and options:

```
ai-engineer-cli main --help
```

---

## 4. Importing and Using the Library in Python Code

In addition to the CLI, you might want to use the underlying functionality (`OpenAIEngineer`) directly within your Python code. Here's how you can do that.

### **a. Ensure Proper Package Structure**

Your `pyproject.toml` should be configured to recognize the `src` directory as the source of your package. Typically, it should look like this:

```toml
[tool.poetry]
name = "my-project"
version = "0.1.0"
description = "Description of your project."
authors = ["Your Name <you@example.com>"]
packages = [{ include = "ai_engineer", from = "src" }]
```

### **b. Importing the `OpenAIEngineer` Class**

Here's how you can import and use the `OpenAIEngineer` class in your Python scripts:

```python
from ai_engineer.services.openai_engineer import OpenAIEngineer

def run_engineer_tasks():
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    # Get the OpenAI API key from environment variables
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OpenAI API key not found in environment variables.")

    # Create an instance of OpenAIEngineer
    engineer = OpenAIEngineer(api_key=api_key)

    # Run the project tree prompt processing
    engineer.ai_engineer_project_tree_prompt(
        project_path="/path/to/project",
        prompt="Implement feature X",
        mode="creator",
        auto_file_discovery=True,
        reuse_auto_file_discovery=False,
        gitignore_file_path=".gitignore",
        overwrite=True,
        max_chat_iterations=25,
    )

if __name__ == "__main__":
    run_engineer_tasks()
```

---

## 5. Additional Tips

### **a. Environment Variables Management**

- **`.env` File:** Store sensitive information like API keys in a `.env` file. Ensure this file is listed in your `.gitignore` to prevent accidental commits.

    **Sample `.env`:**
    ```
    OPENAI_API_KEY=your_openai_api_key_here
    ```
