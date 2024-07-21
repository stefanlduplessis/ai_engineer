from abc import ABC, abstractmethod
import re
import os

class AIEngineer(ABC):
    def __init__(self):
        self.ai_engineer_conversation_history = [] # Store the conversation history
        self.ai_engineer_prompt = None # Prompt to send to the AI model
        self.ai_engineer_response = None # Response from the AI model
    
    @property
    def ai_engineer_prompt(self):
        return self.ai_engineer_prompt
    
    @ai_engineer_prompt.setter
    @abstractmethod
    def ai_engineer_prompt(self):
        raise NotImplementedError("Setter for ai_engineer_conversation_history is not implemented")
    
    @property
    def ai_engineer_response(self):
        return self.ai_engineer_response
    
    @ai_engineer_response.setter
    @abstractmethod
    def ai_engineer_response(self):
        raise NotImplementedError("Setter for ai_engineer_conversation_history is not implemented")
      
    @abstractmethod
    def ai_engineer_process(self):
        raise NotImplementedError("Method for ai_engineer_process is not implemented")
    
    # Function to read all files in a directory
    def ai_engineer_read_project_files(self, project_path):
        project_files = {}
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith(".py") or file.endswith(".html"):  # Adjust as needed
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        project_files[file_path] = f.read()
        return project_files

    # Function to chunk data into manageable pieces
    def ai_engineer_chunk_data(data, chunk_size=2000):
        return [data[i:i + chunk_size] for i in range(0, len(data), chunk_size)]

    # Function to send chunks to AI model and process the responses
    def ai_engineer_process_chuncks(self, chunks, history_context=True):
        for chunk in chunks:
            self.ai_engineer_conversation_history.append(self.ai_engineer_prompt(chunk))
            response = self.ai_engineer_process(self.conversation_history)
            extracted_response = self.ai_engineer_response(response)
            self.ai_engineer_conversation_history.append(extracted_response)
            print("AI Chunk Response:", extracted_response)  # Print or handle the response as needed

    def ai_engineer_convert_markdown_to_commented_python(self, content):
        # Split the content into parts, separating code blocks from regular text
        parts = re.split(r'(```python.*?```)', content, flags=re.DOTALL)
        python_script = ""
        python_comments = ""
        for part in parts:
            if part.startswith('```python'):
                # Extract code block without the markdown delimiters
                code_block = re.sub(r'^```python|```$', '', part, flags=re.DOTALL).strip()
                python_script += (code_block + '\n\n')
            else:
                # Convert non-code part to comments
                comments = part.strip().split('\n')
                comment = ""
                for line in comments:
                    content = line.strip()  # Avoid writing empty lines
                    if content:
                        comment += ('# ' + content + '\n')

                python_comments += f"{comment}\n"
                python_script += f"{comment}\n"

        return python_script, python_comments
    
