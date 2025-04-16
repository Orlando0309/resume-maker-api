from pathlib import Path
def get_prompt(prompt)->str:
    prompt_file = Path(__file__).parent / "prompt" / prompt
    return str(prompt_file)