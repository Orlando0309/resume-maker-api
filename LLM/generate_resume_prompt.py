import json

from schemas import ResumeCreate

def build_resume_prompt(profile_data: dict, job_description: str) -> str:
    return (
        "You are an HR professional tasked with creating a tailored resume for a candidate based on their profile information and a specific job description. "
        "Your goal is to generate a resume that highlights the candidate's skills, education, experiences, certifications, and projects in a way that aligns with the job requirements. "
        "You must use only the information provided in the candidate's profile and not introduce any new data or modify the personal information.\n\n"
        
        f"Candidate Profile Data:\n{json.dumps(profile_data, indent=2)}\n\n"
        f"Job Description:\n{job_description}\n\n"
        
        "Using the candidate's profile data, create a resume that:\n"
        "- Tailors the wording, ordering, and emphasis of the skills, education, experiences, certifications, and projects to match the job description.\n"
        "- Does not add any new skills, experiences, or other data not present in the profile.\n"
        "- Preserves the candidate’s original personal information (full_name, email, phone, address, linkedin, facebook, x) exactly as provided.\n"
        "- Follows standard resume norms:\n"
        "  - Lists work experiences and education in reverse chronological order (newest first).\n"
        "  - Uses concise, action-oriented language and maintains consistency.\n"
        "  - Ensures date values are in 'YYYY-MM-DD' format.\n"
        "  - Maintains clarity and proper formatting for easy readability.\n"
        "- For optional fields (address, linkedin, facebook, x, end_date, link), if missing in the profile, set them explicitly to null.\n\n"
        
        "Generate the resume strictly in JSON format matching the following ResumeCreate schema. Do not include any additional text or explanations.\n\n"
        
        f"The required output JSON schema is: {ResumeCreate.model_json_schema()}\n\n"
        
        "Ensure that:\n"
        "- All dates are formatted as 'YYYY-MM-DD'.\n"
        "- Work experiences and education entries are sorted in reverse chronological order.\n"
        "- No new data is introduced; only the existing profile data is used.\n"
        "- Optional fields missing from the profile are set to null.\n"
        "- The output is valid JSON matching the provided schema.\n\n"
        
        "Output only the JSON and nothing else."
    )