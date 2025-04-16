import json
from pathlib import Path
from LLM.load_prompt import load_prompt
from LLM.utils import get_prompt
from schemas import ResumeCreate

def build_resume_prompt(profile_data: dict, hr_key_points: dict) -> str:
    schema = ResumeCreate.model_json_schema()
    return load_prompt(
        prompt_file=get_prompt("build_resume.yaml"),
        prompt_key='prompt',
        profile_data=profile_data,
        hr_key_points=hr_key_points,
        schema=schema
    )

