import argparse
import os
from gpt.openai_engineer import OpenAIEngineer


def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run AI co-creator tasks with OpenAI.")

    # Add arguments
    parser.add_argument('--project_path', type=str, required=True, help="Path to the project directory.")
    parser.add_argument('--prompt', type=str, required=True, help="Action prompt for the AI.")
    parser.add_argument('--api_key', type=str, default="", help="Your OpenAI API key.")
    parser.add_argument('--context_prompt', type=str, default="", help="Context prompt for the AI.")
    parser.add_argument('--auto_context', action='store_true', help="Enable auto-context discovery for model to prompt and feed itself the nessary files.")
    parser.add_argument('--gitignore_file_path', type=str, default=".gitignore", help="Relative path of .gitignore.")

    # Parse arguments
    args = parser.parse_args()

    # Get the OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY", args.api_key)
    if not openai_api_key:
        raise ValueError("OpenAI API key not provided as an argument or in the environment variable OPENAI_API_KEY.")

    # Create an instance of OpenAIEngineer
    engineer = OpenAIEngineer(api_key=openai_api_key)

    # Run the project tree prompt processing
    try:
        engineer.ai_engineer_project_tree_prompt(
            project_path=args.project_path,
            prompt=args.prompt,
            context_prompt=args.context_prompt,
            auto_context=args.auto_context,
            gitignore_file_path=args.gitignore_file_path
        )
        print("Processing completed successfully.")
    except Exception as e:
        print(f"Error during processing: {e}")


if __name__ == "__main__":
    main()
