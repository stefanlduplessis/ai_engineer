import copy
import logging
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
        self.project_root = ""

    class Modes(Enum):
        """Define the modes for the AI model."""

        CREATOR = "creator"
        EDITOR = "editor"

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

    def ai_engineer_project_tree_prompt(self, project_path, prompt, mode: Modes, auto_file_discovery=False, reuse_auto_file_discovery=False,
                                         gitignore_file_path="", overwrite=False, max_chat_iterations=25):
        """Main function to process project files with the AI model."""
        chat_iterations = 0
        self.project_root = project_path
        project_dir_structure = self.ai_engineer_build_dir_structure(self.project_root,
                                                                     self.project_root + "/" + gitignore_file_path)

        # Reset the conversation history
        self.ai_engineer_conversation_history = []

        if reuse_auto_file_discovery:
            latest_auto_context = self.ai_engineer_import_auto_context_latest()
            if latest_auto_context:
                self.ai_engineer_conversation_history = latest_auto_context
                logging.info("Reusing the latest auto-context from the previous run.")
            else:
                logging.info("No auto-context found from the previous run. Running the model without auto-context.")
        elif auto_file_discovery:
            self.ai_engineer_conversation_history_append(self.ai_engineer_create_prompt(
                self.Roles.SYSTEM,
                self.ai_engineer_system_prompts.AI_ENGINEER_PROJECT_TREE_DISCOVERY.value.replace("{% prompt %}", prompt),
            ))
            self.ai_engineer_conversation_history_append(
                self.ai_engineer_create_prompt(self.Roles.USER, json.dumps(project_dir_structure))
            )
            response = self.ai_engineer_process_history()
            response_choice = response.choices[-1].message.content
            while not "AI-ENGINEER:READY" in response_choice and chat_iterations < max_chat_iterations:
                self.ai_engineer_conversation_history_append(
                    self.ai_engineer_create_prompt(self.Roles.ASSISTANT, response_choice))
                requested_file_path, _ = self.ai_engineer_parse_response(response_choice)
                requested_project_file_path = os.path.join(self.project_root, requested_file_path.replace("project_root/", ""))
                if os.path.exists(requested_project_file_path):
                    with open(requested_project_file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                    prompt = self.ai_engineer_create_prompt(self.Roles.USER, file_content)
                else:
                    logging.error("Could not find specified file at file path: %s", requested_project_file_path)
                    prompt = self.ai_engineer_create_prompt(self.Roles.USER,
                                                            f"Could not find specified file at file path: {requested_file_path}")

                self.ai_engineer_conversation_history_append(prompt)
                chat_iterations += 1
                response = self.ai_engineer_process_history()
                response_choice = response.choices[-1].message.content
            if chat_iterations == max_chat_iterations and not "AI-ENGINEER:READY" in response_choice:
                logging.info("The model did not respond with AI-ENGINEER:READY after %s iterations.", max_chat_iterations)
            self.ai_engineer_export_conversation_history("ai_engineer_auto_context")

        # Process the project files based on the mode
        if mode == self.Modes.CREATOR.value:
            context_prompt = self.ai_engineer_create_prompt(self.Roles.SYSTEM, self.ai_engineer_system_prompts.AI_ENGINEER_PROJECT_TREE_CREATOR.value)
            self.ai_engineer_conversation_history_append(context_prompt)
            user_prompt = self.ai_engineer_create_prompt(self.Roles.USER, prompt)
            self.ai_engineer_conversation_history_append(user_prompt)
            response = self.ai_engineer_process_history()
            response_choice = response.choices[-1].message.content
            self.ai_engineer_conversation_history_append(
            self.ai_engineer_create_prompt(self.Roles.ASSISTANT, response_choice))
            while not "AI-ENGINEER:DONE" in response_choice and chat_iterations < max_chat_iterations:
                ai_project_file_path, parsed_file_content = self.ai_engineer_parse_response(response_choice)
                ai_project_file_path = ai_project_file_path.replace("project_root", self.project_root, 1)
                if not overwrite:
                    ai_project_file_path = f"{ai_project_file_path}.ai_engineer"

                # create path if not exists
                os.makedirs(os.path.dirname(ai_project_file_path), exist_ok=True)
                with open(ai_project_file_path, "w+", encoding="utf-8") as f:
                    f.write(parsed_file_content)
                self.ai_engineer_conversation_history_append(
                    self.ai_engineer_create_prompt(self.Roles.USER, "Thank you. Next file please."))
                response = self.ai_engineer_process_history()
                response_choice = response.choices[-1].message.content
                self.ai_engineer_conversation_history_append(
                    self.ai_engineer_create_prompt(self.Roles.ASSISTANT, response_choice))
                chat_iterations += 1
                
            if chat_iterations == max_chat_iterations and not "AI-ENGINEER:DONE" in response_choice:
                logging.info("The model did not respond with AI-ENGINEER:DONE after %s iterations.", max_chat_iterations)
        elif mode == self.Modes.EDITOR.value:
            context_prompt = self.ai_engineer_create_prompt(self.Roles.SYSTEM, self.ai_engineer_system_prompts.AI_ENGINEER_PROJECT_TREE_EDITOR.value.format(prompt=prompt))
            self.ai_engineer_conversation_history_append(context_prompt)

            # Cache the initial conversation history
            self.project_files_history_init_cache = copy.deepcopy(self.ai_engineer_conversation_history)

            # Flatten the project directory structure
            project_dir_structure_flat = self.ai_engineer_flatten_dir_structure(project_dir_structure)
            for system_project_file_path_mask, nested in project_dir_structure_flat.items():
                if nested is None:
                    system_project_file_path = system_project_file_path_mask.replace("project_root", self.project_root, 1)
                    # Reset the conversation history for each file
                    self.ai_engineer_conversation_history = self.project_files_history_init_cache
                    logging.info("Processing file: %s", system_project_file_path)
                    with open(system_project_file_path, "r", encoding="utf-8") as f:
                        file_content = f.read()
                    prompt_content = f"FILE_PATH:{system_project_file_path_mask}\nFILE_CONTENT:\n{file_content}\nFILE_ACTION:{prompt}"
                    self.ai_engineer_conversation_history_append(
                        self.ai_engineer_create_prompt(self.Roles.USER, prompt_content))
                    
                    response = self.ai_engineer_process_history()
                    response_choice = response.choices[-1].message.content
                    self.ai_engineer_conversation_history_append(
                        self.ai_engineer_create_prompt(self.Roles.ASSISTANT, response_choice))
                    
                    ai_project_file_path_mask, parsed_file_content = self.ai_engineer_parse_response(response_choice)
                    ai_project_file_path = ai_project_file_path_mask.replace("project_root", self.project_root, 1)

                    if os.path.realpath(system_project_file_path) == os.path.realpath(ai_project_file_path):
                        if not overwrite:
                            ai_project_file_path = f"{ai_project_file_path}.ai_engineer"
                        with open(ai_project_file_path, "w+", encoding="utf-8") as f:
                            f.write(parsed_file_content)
                    else:
                        logging.error("File path mismatch: file_path_input:%s != file_path_output:%s", system_project_file_path, ai_project_file_path)
