import copy
from enum import Enum
import json
import os
from ai_engineer import AIEngineer
from openai import OpenAI


class OpenAIEngineer(AIEngineer, OpenAI):
    def __init__(self, api_key):
        super().__init__()  # Initialize the AIEngineer
        OpenAI.__init__(self, api_key=api_key)  # Initialize OpenAI with the provided API key
        self.ai_engineer_prompt = None
        self.project_files_history_init_cache = {}

    class Roles(Enum):
        """Define the roles for the AI model."""

        USER = "user"
        SYSTEM = "system"
        ASSISTANT = "assistant"

    @staticmethod
    def ai_engineer_create_prompt(role: Roles, content):
        """Create a prompt for the AI model with a specified role and content."""
        return {"role": role.value, "content": content}

    def ai_engineer_process_history(self):
        """Process the conversation history to get a response from the AI model."""
        return self.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.ai_engineer_conversation_history,
        )

    def ai_engineer_project_tree_prompt(self, project_path, prompt, context_prompt="", auto_context=False,
                                         gitignore_file_path=""):
        """Main function to process project files with the AI model."""
        self.project_root = project_path

        project_dir_structure = self.ai_engineer_build_dir_structure(project_path,
                                                                     project_path + "/" + gitignore_file_path)

        # Load existing conversation history
        with open(project_path + "/ai_engineer_output/ai_engineer_conversation_history.json", "r",
                  encoding="utf-8") as f:
            self.ai_engineer_conversation_history = json.loads(f.read())

        if auto_context:
            self.ai_engineer_conversation_history_append(self.ai_engineer_create_prompt(
                self.Roles.SYSTEM,
                self.ai_engineer_system_prompts.AI_ENGINEER_PROJECT_FILES_DISCOVERY.value,
            ))
            self.ai_engineer_conversation_history_append(
                self.ai_engineer_create_prompt(self.Roles.USER, json.dumps(project_dir_structure))
            )

            chat_iterations = 1
            response = self.ai_engineer_process_history()
            response_choice = response.choices[-1].message.content

            while not response_choice.startswith("READY") and chat_iterations < 10:
                self.ai_engineer_conversation_history_append(
                    self.ai_engineer_create_prompt(self.Roles.ASSISTANT, response_choice))

                # Handle file path requests
                if response.choices[-1].message.content.startswith("FILE_PATH"):
                    file_path = response.choices[-1].message.content.split(":")[1].strip()
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_content = f.read()
                        prompt = self.ai_engineer_create_prompt(self.Roles.USER, file_content)
                    else:
                        prompt = self.ai_engineer_create_prompt(self.Roles.USER,
                                                                f"Could not find specified file at file path: {file_path}")

                    self.ai_engineer_conversation_history_append(prompt)
                    chat_iterations += 1
                    response = self.ai_engineer_process_history()
                    response_choice = response.choices[-1].message.content
                else:
                    raise Exception(
                        "Unexpected response from AI model. Please check the conversation history at ai_engineer_output/auto_discovery_init.md")

        # Set context prompt if not provided
        if not context_prompt:
            context_prompt = self.ai_engineer_create_prompt(self.Roles.SYSTEM,
                                                            self.ai_engineer_system_prompts.AI_ENGINEER_PROJECT_FILES_GENERATOR.value)
        self.ai_engineer_conversation_history_append(context_prompt)

        # Cache the initial conversation history
        self.project_files_history_init_cache = copy.deepcopy(self.ai_engineer_conversation_history)

        # Flatten the project directory structure
        project_dir_structure_flat = self.ai_engineer_flatten_dir_structure(project_dir_structure)

        for file_path, empty_value in project_dir_structure_flat.items():
            if empty_value is None:
                # Reset the conversation history for each file
                self.ai_engineer_conversation_history = self.project_files_history_init_cache

                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                prompt_content = f"FILE_PATH:{file_path}\nFILE_CONTENT:\n{file_content}\nFILE_ACTION:{prompt}"

                self.ai_engineer_conversation_history_append(
                    self.ai_engineer_create_prompt(self.Roles.USER, prompt_content))
                response = self.ai_engineer_process_history()
                response_choice = response.choices[-1].message.content

                self.ai_engineer_conversation_history_append(
                    self.ai_engineer_create_prompt(self.Roles.ASSISTANT, response_choice))

                file_root, _ = os.path.splitext(file_path)
                with open(f"{file_root}_ai_engineer.md", "w+", encoding="utf-8") as f:
                    f.write(response_choice)
