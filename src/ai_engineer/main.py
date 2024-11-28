"""Main entry point for the AIEngineer CLI application."""

import logging
import os
import traceback
from typing import Optional

import typer
from dotenv import load_dotenv

from .services.openai_engineer import OpenAIEngineer

app = typer.Typer()

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def cli():
    """Entry point for the CLI."""
    app()


def load_api_key(provided_key: str) -> str:
    """
    Load the OpenAI API key from environment or provided argument.

    Args:
        provided_key (str): API key provided via command line.

    Returns:
        str: OpenAI API key.

    Raises:
        ValueError: If API key is not found.
    """
    load_dotenv()
    api_key = provided_key or os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error(
            "OpenAI API key not provided as an argument or in the environment variable OPENAI_API_KEY."
        )
        raise ValueError(
            "OpenAI API key not provided as an argument or in the environment variable OPENAI_API_KEY."
        )
    return api_key


@app.command()
def main(
    project_path: str = typer.Argument(..., help="Path to the project directory."),
    prompt: str = typer.Argument(..., help="Action prompt for the AIEngineer."),
    mode: str = typer.Argument(
        ..., help="System mode for the AIEngineer. creator|editor"
    ),
    api_key: Optional[str] = typer.Option(
        None, "--api_key", help="Your OpenAI API key."
    ),
    auto_file_discovery: bool = typer.Option(
        False,
        "--auto_file_discovery",
        help="Enable auto-file-discovery context for model to prompt and feed itself the necessary files.",
    ),
    reuse_auto_file_discovery: bool = typer.Option(
        False,
        "--reuse_auto_file_discovery",
        help="Reuse the auto-file-discovery context from the previous run.",
    ),
    gitignore_file_path: str = typer.Option(
        ".gitignore",
        "--gitignore_file_path",
        help="Relative path of .gitignore.",
    ),
    overwrite: bool = typer.Option(
        False, "--overwrite", help="Overwrite existing files."
    ),
    max_chat_iterations: int = typer.Option(
        25,
        "--max_chat_iterations",
        help="Max chat iterations for the AI model.",
    ),
):
    """
    Run AI co-creator tasks with OpenAI.
    """
    try:
        # Load API key
        openai_api_key = load_api_key(api_key)

        # Create an instance of OpenAIEngineer
        engineer = OpenAIEngineer(api_key=openai_api_key)

        # Log the start of processing
        logger.info("Starting processing with project_path: %s", project_path)

        # Run the project tree prompt processing
        engineer.ai_engineer_project_tree_prompt(
            project_path=project_path,
            prompt=prompt,
            mode=mode,
            auto_file_discovery=auto_file_discovery,
            reuse_auto_file_discovery=reuse_auto_file_discovery,
            gitignore_file_path=gitignore_file_path,
            overwrite=overwrite,
            max_chat_iterations=max_chat_iterations,
        )

        # Log successful completion
        logger.info("Processing completed successfully.")

    except Exception as e:
        logger.error("An error occurred during processing: %s", e)
        traceback.print_exc()
        raise typer.Exit(code=1)


if __name__ == "__main__":
    cli()
