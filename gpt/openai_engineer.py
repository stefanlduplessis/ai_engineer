import copy
from enum import Enum
import json
import os
from ai_engineer import AIEngineer
from openai import OpenAI


class OpenAIEngineer(AIEngineer, OpenAI):
    def __init__(self, api_key):
        AIEngineer.__init__(self)
        OpenAI.__init__(self, api_key=api_key)
        self.ai_engineer_prompt = None
        self.project_files_history_init_cache = {}

    class Roles(Enum):
        """
        Define the roles for the AI mode
        """

        USER = "user"
        SYSTEM = "system"
        ASSISTANT = "assistant"

    def ai_engineer_create_prompt(self, role: Roles, content):
        return {"role": role.value, "content": content}
    
    def ai_engineer_process_history(self):
        return self.chat.completions.create(
            model="gpt-4o-mini",
            messages=self.ai_engineer_conversation_history,
        )

    # Main function to process the entire project
    def ai_engineer_project_files_prompt(self, project_path, prompt, context_prompt="", auto_discovery=False, ignore_file_rel_path=""):
        self.ai_engineer_conversation_history = []
        project_files = self.ai_engineer_build_dir_structure(project_path, project_path + "/" + ignore_file_rel_path)

        if auto_discovery:
            self.ai_engineer_conversation_history.append(self.ai_engineer_create_prompt(
                self.Roles.SYSTEM,
                self.ai_engineer_system_prompts.AI_ENGINEER_PROJECT_FILES_DISCOVERY.value,
            )
            )
            self.ai_engineer_conversation_history.append(
                self.ai_engineer_create_prompt(self.Roles.USER, json.dumps(project_files))
            )


            chat_iterations = 1
            response = self.ai_engineer_process_history()
            while not response.choices[-1].message.content.startswith("READY") and chat_iterations < 10:
                with open(f"{project_path}/ai_engineer_output/auto_discovery_init.md", "a+", encoding="utf-8") as f:
                    f.write(response.choices[-1].message.content)
                # append or create and append to a new file


                if response.choices[-1].message.content.startswith("FILE_PATH"):
                    file_path = response.choices[-1].message.content.split(":")[1]
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            file_content = f.read()
                        prompt = self.ai_engineer_create_prompt(self.Roles.USER, file_content)
                    else:
                        prompt = self.ai_engineer_create_prompt(self.Roles.USER, f"Could not find specified file at file path: {file_path}")

                    self.ai_engineer_conversation_history.append(prompt)
                    chat_iterations += 1
                    response = self.ai_engineer_process_history()
                else:
                    raise Exception("Unexpected response from AI model. Please check the conversation history at ai_engineer_output/auto_discovery_init.md")
                
        if not context_prompt:
            context_prompt = (
                self.ai_engineer_create_prompt(self.Roles.SYSTEM,self.ai_engineer_system_prompts.AI_ENGINEER_PROJECT_FILES_GENERATOR.value)
            )
        self.ai_engineer_conversation_history.append(context_prompt)

        # Cache the initial conversation history
        self.project_files_history_init_cache = copy.deepcopy(self.ai_engineer_conversation_history)

        project_files_flat = self.ai_engineer_flatten_dir_structure(project_files)
        for file_path, empty_value in project_files_flat.items():
            if empty_value is None: # flattend end of the file path
                # reset the conversation history
                self.ai_engineer_conversation_history = [self.project_files_history_init_cache]
                with open(file_path, "r", encoding="utf-8") as f:
                    file_content = f.read()
                prompt_content = f"FILE_PATH:{file_path}\nFILE_CONTENT:\n{file_content}\nFILE_ACTION:{prompt}"
                file_prompt = self.ai_engineer_create_prompt(self.Roles.USER, prompt_content)
                self.ai_engineer_conversation_history.append(file_prompt)
                response = self.ai_engineer_process_history()
                for index, choice in enumerate(response.choices):
                    reponse_markdown = choice.message.content
                    file_root, _ = os.path.splitext(file_path)
                    with open(f"{file_root}_ai_engineer_{index}.md", "w+", encoding="utf-8") as f:
                        f.write(reponse_markdown)
