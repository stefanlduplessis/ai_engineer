from abc import abstractmethod
import re
import os
from ai_engineer.ai_engineer import AIEngineer
from openai import OpenAI

class OpenAIEngineer(AIEngineer, OpenAI):
    def __init__(self, api_key):
        AIEngineer.__init__(self)
        OpenAI.__init__(self, api_key=api_key)
    
    @AIEngineer.ai_engineer_prompt.setter
    def ai_engineer_prompt(self, value):
        return {"role": "user", "content": value}
    
    @AIEngineer.ai_engineer_response.setter
    def ai_engineer_response(self, value):
        return {"role": "assistant", "content": value['choices'][0]['message']['content']}
      
    def ai_engineer_process(self):
        return self.chat.completions.create(
            model="gpt-3.5-turbo-0125",
            messages=self.ai_engineer_conversation_history,
            max_tokens=1000
        )

    # Main function to process the entire project
    def ai_engineer_load_project(self, project_path):
        project_files = self.ai_engineer_read_project_files(project_path)
        all_content = ""
        for file_path, content in project_files.items():
            all_content += f"FILE:{file_path}\n{content}\n\n"

        return all_content
    
        chunks = self.ai_engineer_chunk_data(all_content)
        self.send_to_chatgpt(chunks)