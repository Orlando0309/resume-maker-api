import yaml
import json
from pathlib import Path

def load_prompt(prompt_file: str, prompt_key: str, **variables) -> str:
    """
    Load a prompt template from a YAML file and format it with the provided variables.

    Args:
        prompt_file (str): Path to the YAML file containing prompt templates.
        prompt_key (str): The key of the prompt template to load from the YAML file.
        **variables: Keyword arguments for the variables to replace in the template.

    Returns:
        str: The formatted prompt string.

    Raises:
        ValueError: If the prompt key is not found or a required variable is missing.
    """
    # Load the YAML file
    try:
        with open(prompt_file, 'r', encoding='utf-8') as file:
            prompts = yaml.safe_load(file)
    except FileNotFoundError:
        raise ValueError(f"YAML file not found: {prompt_file}")

    # Get the prompt template using the provided key
    template = prompts.get(prompt_key)
    if not template:
        raise ValueError(f"Prompt key '{prompt_key}' not found in {prompt_file}")

    # Format the template with the provided variables
    try:
        # Convert dictionaries to JSON strings for better formatting in the prompt
        formatted_variables = {
            key: json.dumps(value, indent=2, ensure_ascii=False) if isinstance(value, dict) else value
            for key, value in variables.items()
        }
        return template.format(**formatted_variables)
    except KeyError as e:
        raise ValueError(f"Missing variable for placeholder: {e}")