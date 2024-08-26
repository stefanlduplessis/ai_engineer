"""
The AIEngineer class defines abstract methods for setting the prompt and response properties,
processing the AI model's response, and handling the conversation history.
"""
from datetime import datetime
import json
import re
import os
import fnmatch
from system_prompts import SystemPrompts
import logging.config

# Define the logging configuration dictionary
logging_config = {
    'version': 1,  # Required
    'disable_existing_loggers': False,  # Keeps existing loggers active

    # Formatters specify the layout of the log messages
    'formatters': {
        'standard': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        },
        'detailed': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
        },
    },

    # Handlers direct log messages to a particular destination
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'standard',
        },
        'file': {
            'class': 'logging.FileHandler',
            'level': 'DEBUG',
            'formatter': 'detailed',
            'filename': 'app.log',
            'mode': 'a',  # Append mode
        },
    },

    # Loggers capture log messages and route them to handlers
    'loggers': {
        '': {  # Root logger
            'level': 'INFO',
            'handlers': ['console', 'file'],
            'propagate': False,  # Prevent log messages from propagating to the root logger
        },
    }
}

# Apply the logging configuration
logging.config.dictConfig(logging_config)

class AIEngineer:
    """
    AIEngineer is an abstract base class that represents an AI engineer.

    Attributes:
        ai_engineer_conversation_history (list): Store the conversation history.
        ai_engineer_prompt (str): Prompt to send to the AI model.
        ai_engineer_response (str): Response from the AI model.
    """

    def __init__(self):
        self.init_time = datetime.now()  # Initialize the current time
        self.ai_engineer_conversation_history = []  # Store the conversation history
        self.ai_engineer_prompt = None  # Prompt to send to the AI model
        self.ai_engineer_response = None  # Response from the AI model
        self.ai_engineer_system_prompts = SystemPrompts
        self.project_root = None

    def ai_engineer_conversation_history_append(self, chat):
        """
        Append a new entry to the conversation history.
        """
        self.ai_engineer_conversation_history.append(chat)
        self.ai_engineer_export_conversation_history()

    @staticmethod
    def ai_engineer_chunk_data(data, chunk_size=2000):
        """
        Chunk data into manageable pieces.

        Args:
            data (str): Data to be chunked.
            chunk_size (int, optional): Size of each chunk. Defaults to 2000.

        Returns:
            list: A list of chunks.
        """
        return [data[i: i + chunk_size] for i in range(0, len(data), chunk_size)]

    @staticmethod
    def ai_engineer_convert_markdown_to_commented_python(content):
        """
        Convert markdown content to commented Python code.

        Args:
            content (str): Markdown content to be converted.

        Returns:
            tuple: A tuple containing the converted Python script and comments.
        """
        # Split the content into parts, separating code blocks from regular text
        parts = re.split(r"(```python.*?```)", content, flags=re.DOTALL)
        python_script = ""
        python_comments = ""
        for part in parts:
            if part.startswith("```python"):
                # Extract code block without the markdown delimiters
                code_block = re.sub(
                    r"^```python|```$", "", part, flags=re.DOTALL
                ).strip()
                python_script += code_block + "\n\n"
            else:
                # Convert non-code part to comments
                comments = part.strip().split("\n")
                comment = ""
                for line in comments:
                    content = line.strip()  # Avoid writing empty lines
                    if content:
                        comment += "# " + content + "\n"

                python_comments += f"{comment}\n"
                python_script += f"{comment}\n"

        return python_script, python_comments

    @staticmethod
    def ai_engineer_read_ignore_file(ignore_file_path):
        """
        Read patterns from an ignore file to determine which files should be ignored.

        Args:
            ignore_file_path (str): Path to the ignore file.

        Returns:
            list: A list of patterns to ignore.
        """
        with open(ignore_file_path, 'r', encoding="utf-8") as file:
            ignore_patterns = [line.strip() for line in file if line.strip() and not line.startswith('#')]
        return ignore_patterns

    @staticmethod
    def ai_engineer_should_ignore(path, ignore_patterns):
        """
        Check whether the given path matches any ignore patterns.

        Args:
            path (str): The file or directory path.
            ignore_patterns (list): List of patterns.

        Returns:
            bool: True if path should be ignored, False otherwise.
        """
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False

    def ai_engineer_build_dir_structure(self, root_dir, ignore_file_path=""):
        """
        Build a directory structure representation of the project.

        Args:
            root_dir (str): The root directory to analyze.
            ignore_file_path (str, optional): Path to a file with ignore patterns.

        Returns:
            dict: A dictionary representing the directory structure.
        """
        dir_structure = {}

        for dirpath, dirnames, filenames in os.walk(root_dir):
            # Current level reference in the dictionary
            rel_path = os.path.relpath(dirpath, root_dir)
            parts = rel_path.split(os.sep)
            current_level = dir_structure

            for part in parts:
                if part != ".":
                    current_level = current_level.setdefault(part, {})

            ignore_patterns = ["ai_engineer_output/*"]
            if ignore_file_path:
                if os.path.exists(ignore_file_path):
                    ignore_patterns.extend(self.ai_engineer_read_ignore_file(ignore_file_path))

            # Modify dirnames in-place to remove ignored directories
            dirnames[:] = [d for d in dirnames if not self.ai_engineer_should_ignore(d + "/", ignore_patterns)]

            # Add files to the current level
            for filename in filenames:
                if not self.ai_engineer_should_ignore(os.path.join(dirpath, filename), ignore_patterns):
                    current_level[filename] = None

        return dir_structure

    def ai_engineer_flatten_dir_structure(self, dir_structure, base_path=""):
        """
        Flatten a nested directory structure into a single-level dictionary.

        Args:
            dir_structure (dict): The directory structure to flatten.
            base_path (str, optional): Base path for keys.

        Returns:
            dict: A flattened dictionary with file paths.
        """
        flat_dict = {}

        for name, content in dir_structure.items():
            current_path = os.path.join(base_path, name)

            if isinstance(content, dict) and content:  # If it's a non-empty directory
                flat_dict.update(self.ai_engineer_flatten_dir_structure(content, current_path))
            else:
                flat_dict[current_path] = content  # File or empty directory

        return flat_dict

    def ai_engineer_export_conversation_history(self, file_prefix="ai_engineer_conversation_history"):
        """
        Export the conversation history to a JSON file.

        Args:
            file_prefix (str): Prefix for the output file name.
        """
        if not os.path.exists(f"{self.project_root}/ai_engineer_output"):
            os.makedirs(f"{self.project_root}/ai_engineer_output")
        with open(f"{self.project_root}/ai_engineer_output/" + file_prefix + "_" + self.init_time.strftime("%Y%m%d%H%M%S") + ".json", "w+", encoding="utf-8") as f:
            f.write(json.dumps(self.ai_engineer_conversation_history, indent=4))
