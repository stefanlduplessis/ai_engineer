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


class AIEngineer:
    """
    AIEngineer is an abstract base class that represents an AI engineer.

    Attributes:
        ai_engineer_conversation_history (list): Store the conversation history.
        ai_engineer_prompt (str): Prompt to send to the AI model.
        ai_engineer_response (str): Response from the AI model.
    """

    def __init__(self):
        self.init_time = datetime.now() # Initialize the current time
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

    def ai_engineer_read_project_files(self, project_path):
        """
        Read all files in a directory.

        Args:
            project_path (str): Path to the project directory.

        Returns:
            dict: A dictionary containing file paths as keys and file contents as values.
        """
        project_files = {}
        for root, _, files in os.walk(project_path):
            for file in files:
                if file.endswith(".py") or file.endswith(".html"):  # Adjust as needed
                    file_path = os.path.join(root, file)
                    with open(file_path, "r", encoding="utf-8") as f:
                        project_files[file_path] = f.read()
        return project_files

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
        return [data[i : i + chunk_size] for i in range(0, len(data), chunk_size)]

    def ai_engineer_convert_markdown_to_commented_python(self, content):
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

    def ai_engineer_read_ignore_file(self, ignore_file_path):
        """
        ignore_patterns = read_ignore_file('.ignore')
        print(ignore_patterns)
        # Output: ['*.log', 'temp/', 'build/', '*.tmp']
        """
        with open(ignore_file_path, 'r', encoding="utf-8") as file:
            ignore_patterns = [line.strip() for line in file if line.strip() and not line.startswith('#')]
        return ignore_patterns

    def ai_engineer_should_ignore(self, path, ignore_patterns):
        for pattern in ignore_patterns:
            if fnmatch.fnmatch(path, pattern):
                return True
        return False

    def ai_engineer_build_dir_structure(self, root_dir, ignore_file_path=""):
        """
        /path/to/your/root
        ├── dir1
        │   ├── file1.txt
        │   └── file2.txt
        ├── dir2
        │   ├── subdir1
        │   │   └── file3.txt
        │   └── subdir2
        └── file4.txt

        The resulting JSON file would look like:
        {
            "root": {
                "dir1": {
                    "file1.txt": null,
                    "file2.txt": null
                },
                "dir2": {
                    "subdir1": {
                        "file3.txt": null
                    },
                    "subdir2": {}
                },
                "file4.txt": null
            }
        }
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

            ignore_patterns = []
            if ignore_file_path:
                if os.path.exists(ignore_file_path):
                    ignore_patterns = self.ai_engineer_read_ignore_file(ignore_file_path)

            # Modify dirnames in-place to remove ignored directories
            dirnames[:] = [d for d in dirnames if not self.ai_engineer_should_ignore(d + "/", ignore_patterns)]

            # Add files to the current level
            for filename in filenames:
                if not self.ai_engineer_should_ignore(os.path.join(dirpath, filename), ignore_patterns):
                    current_level[filename] = None

        return dir_structure
    
    def ai_engineer_flatten_dir_structure(self, dir_structure, base_path=""):
        flat_dict = {}
        
        for name, content in dir_structure.items():
            current_path = os.path.join(base_path, name)
            
            if isinstance(content, dict) and content:  # If it's a non-empty directory
                flat_dict.update(self.ai_engineer_flatten_dir_structure(content, current_path))
            else:
                flat_dict[current_path] = content  # File or empty directory
        
        return flat_dict
    
    def ai_engineer_export_conversation_history(self, file_prefix="ai_engineer_conversation_history"):
        if not os.path.exists(f"{self.project_root}/ai_engineer_output"):
            os.makedirs(f"{self.project_root}/ai_engineer_output")
        with open(f"{self.project_root}/ai_engineer_output/" + file_prefix + "_" + self.init_time.strftime("%Y%m%d%H%M%S"), "w+", encoding="utf-8") as f:
            f.write(json.dumps(self.ai_engineer_conversation_history, indent=4))
