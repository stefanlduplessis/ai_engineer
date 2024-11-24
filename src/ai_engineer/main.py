import argparse
import logging
import os
import traceback

from dotenv import load_dotenv

from src.ai_engineer.services.openai_engineer import OpenAIEngineer

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def Main():
    """
    Main function to run AI co-creator tasks with OpenAI.
    """
    # Set up argument parser
    parser = argparse.ArgumentParser(description="Run AI co-creator tasks with OpenAI.")

    # Add arguments
    parser.add_argument("project_path", type=str, help="Path to the project directory.")
    parser.add_argument("prompt", type=str, help="Action prompt for the AI Engineer.")
    parser.add_argument("mode", type=str, help="System mode for the AI Engineer.")
    parser.add_argument("--api_key", type=str, default="", help="Your OpenAI API key.")
    parser.add_argument(
        "--auto_file_discovery",
        action="store_true",
        help="Enable auto-file-discovery context for model to prompt and feed itself the necessary files.",
    )
    parser.add_argument(
        "--reuse_auto_file_discovery",
        action="store_true",
        help="Reuse the auto-file-discovery context from the previous run.",
    )
    parser.add_argument(
        "--gitignore_file_path",
        type=str,
        default=".gitignore",
        help="Relative path of .gitignore.",
    )
    parser.add_argument(
        "--overwrite", action="store_true", help="Overwrite existing files."
    )
    parser.add_argument(
        "--max_chat_iterations",
        type=int,
        default=25,
        help="Max chat iterations for the AI model.",
    )

    # Parse arguments
    args = parser.parse_args()

    # Load the environment variables
    load_dotenv()

    # Get the OpenAI API key
    openai_api_key = os.environ.get("OPENAI_API_KEY", args.api_key)
    if not openai_api_key:
        logger.error(
            "OpenAI API key not provided as an argument or in the environment variable OPENAI_API_KEY."
        )
        raise ValueError(
            "OpenAI API key not provided as an argument or in the environment variable OPENAI_API_KEY."
        )

    # Create an instance of OpenAIEngineer
    engineer = OpenAIEngineer(api_key=openai_api_key)

    # Run the project tree prompt processing
    try:
        logger.info("Starting processing with project_path: %s", args.project_path)
        engineer.ai_engineer_project_tree_prompt(
            project_path=args.project_path,
            prompt=args.prompt,
            mode=args.mode,
            auto_file_discovery=args.auto_file_discovery,
            reuse_auto_file_discovery=args.reuse_auto_file_discovery,
            gitignore_file_path=args.gitignore_file_path,
            overwrite=args.overwrite,
            max_chat_iterations=args.max_chat_iterations,
        )
        logger.info("Processing completed successfully.")
    except Exception as e:
        logger.error("An error occurred during processing: %s", e)
        traceback.print_exc()


if __name__ == "__main__":
    main()
