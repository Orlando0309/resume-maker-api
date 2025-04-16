from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, User, UserProfile
from schemas import GenerateResumeRequest, OptimizeRequest, ResumeCreate
from utils import get_current_user
import json
import re
from pydantic import BaseModel
import requests
import os
from dotenv import load_dotenv
load_dotenv() 
from LLM.agents import resume_graph

import google.generativeai as genai
router = APIRouter()

# Hugging Face model configuration

GEMINI_API_TOKEN = os.getenv("GEMINI_API_TOKEN")
if not GEMINI_API_TOKEN:
    raise ValueError("GEMINI_API_TOKEN environment variable not set")
genai.configure(api_key=GEMINI_API_TOKEN)

class OptimizedResumeResponse(BaseModel):
    optimized_resume: ResumeCreate
class GeneratedResumeResponse(BaseModel):
    generated_resume: ResumeCreate
def query_to_llm(prompt: str) -> str:
    """Helper function to query the Gemini API for chat completions."""
    model = genai.GenerativeModel('gemini-2.0-flash-exp')  # Or 'gemini-pro-vision' for multimodal

    try:
        response = model.generate_content(prompt)
        

        # The text output is directly accessible
        generated_text = response.text.strip()
        print(generated_text)
        return generated_text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Gemini API call failed: {str(e)}")
      
@router.post("/optimize-resume", response_model=OptimizedResumeResponse)
def optimize_resume(request: OptimizeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")

    # Serialize resume data
    resume_data = {
        "personal_info": resume.personal_info or {},
        "experiences": [
            {
                "title": e.title,
                "company": e.company,
                "description": e.description,
                "start_date": e.start_date.isoformat(),
                "end_date": e.end_date.isoformat() if e.end_date else None
            }
            for e in resume.experiences
        ],
        "educations": [
            {
                "school": edu.school,
                "degree": edu.degree,
                "start_date": edu.start_date.isoformat(),
                "end_date": edu.end_date.isoformat() if edu.end_date else None
            }
            for edu in resume.educations
        ],
        "skills": [
            {"skill_name": s.skill_name}
            for s in resume.skills
        ],
        "certifications": [
            {
                "title": cert.title,
                "authority": cert.authority,
                "date": cert.date.isoformat()
            }
            for cert in resume.certifications
        ],
        "projects": [
            {
                "title": proj.title,
                "description": proj.description,
                "link": proj.link,
                "used_skills": proj.used_skills,
            }
            for proj in resume.projects
        ]
    }
    job_description = request.job_description
    print(json.dumps(resume_data, indent=2))
    # Construct the prompt for the Hugging Face model.
    optimization_prompt = (
    "You are an HR professional reviewing a candidate's resume against a specific job description. "
    "Your goal is to enhance the candidate's skills, education, experiences, certifications, and projects so that they better meet "
    "the job requirements, while strictly preserving the candidate’s original personal information "
    "(full_name, email, phone, address, linkedin, facebook, and x) and all the original resume content. Do not create new personal data, "
    "modify existing personal details, or add any extra fields not present in the candidate’s original resume.\n\n"
    
    f"Original Resume Data:\n{json.dumps(resume_data, indent=2)}\n\n"
    f"Job Description:\n{job_description}\n\n"
    
    "Using only the information available in the original resume data, optimize the wording, ordering, and emphasis "
    "of the skills, education, experiences, certifications, and projects to better align with the job description. "
    "Ensure that you do not introduce any new skills, used_skills, or any other data that were not originally present. "
    "Only rephrase, reorder, or clarify the existing information.\n\n"
    
    "In addition, please follow standard resume norms:\n"
    "- List work experiences and education in reverse chronological order (newest first).\n"
    "- Use concise, action-oriented language and ensure consistency throughout the resume.\n"
    "- Ensure date values are in the 'YYYY-MM-DD' format and accurately reflect the timeline (most recent experiences and educations come first).\n"
    "- Maintain clarity and proper formatting of sections to make the resume easy to read.\n\n"
    "- If the skills, certification, description of the job experiences are irrelevant to the job application, rewrite if possible Or if it does not concern the job, don't include it in the result.\n\n"
    
    "For every optional field (such as address, linkedin, facebook, x, end_date, link), if it is missing in the original resume data, "
    "set its value explicitly to null in the optimized JSON.\n\n"
    
    "Return the optimized resume strictly in JSON format matching the following ResumeCreate schema. Do not include any additional text, explanations, or formatting.\n\n"
    
    f"The required ouput JSON schema is: {ResumeCreate.model_json_schema()}\n"
    
    "Ensure that:\n"
    "- All dates are formatted as 'YYYY-MM-DD'.\n"
    "- Work experiences and education entries are sorted in reverse chronological order (newest first).\n"
    "- No new personal or resume content is generated or altered; only the wording, order, and emphasis are improved.\n"
    "- All fields correspond directly to entries from the original resume data.\n"
    "- Optional fields missing from the original data are explicitly set to null.\n"
    "- The final result is valid JSON matching the provided schema.\n\n"
    
    "Output only the JSON and nothing else."
)





    # Query the Hugging Face model for the optimized resume.
    optimized_resume_str = query_to_llm(optimization_prompt)

    # Parse the generated response as JSON.
    try:
        # Remove any markdown formatting if present.
        optimized_resume_str = optimized_resume_str.replace("```json", "").replace("```", "")
        print(f"------------------{optimized_resume_str}-------------")
        optimized_resume_json = json.loads(optimized_resume_str)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="Failed to parse optimized resume JSON")

    # Validate the JSON data against the ResumeCreate schema.
    try:
        optimized_resume = ResumeCreate(**optimized_resume_json)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid optimized resume data: {str(e)}")

    return OptimizedResumeResponse(optimized_resume=optimized_resume)

@router.post("/generate-resume", response_model=GeneratedResumeResponse)
def generate_resume(request: GenerateResumeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Retrieve the user's profile from the database
    profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="User profile not found")

    # Serialize the user's profile data
    profile_data = {
        "personal_info": profile.personal_info or {},
        "experiences": [
            {
                "title": e.title,
                "company": e.company,
                "description": e.description,
                "start_date": e.start_date.isoformat(),
                "end_date": e.end_date.isoformat() if e.end_date else None
            }
            for e in profile.experiences
        ],
        "educations": [
            {
                "school": edu.school,
                "degree": edu.degree,
                "start_date": edu.start_date.isoformat(),
                "end_date": edu.end_date.isoformat() if edu.end_date else None,
                "used_skills": edu.used_skills,
            }
            for edu in profile.educations
        ],
        "skills": [
            {"skill_name": s.skill_name}
            for s in profile.skills
        ],
        "certifications": [
            {
                "title": cert.title,
                "authority": cert.authority,
                "date": cert.date.isoformat()
            }
            for cert in profile.certifications
        ],
        "projects": [
            {
                "title": proj.title,
                "description": proj.description,
                "link": proj.link,
                "used_skills": proj.used_skills,
            }
            for proj in profile.projects
        ]
    }
    job_description = request.job_description

    # Construct the prompt for the LLM

    initial_state = {
    "profile_data": profile_data,
    "job_description": job_description,
    "generated_resume": {},
    "score": 0,
    "attempts": 0
    }
    # Query the LLM for the generated resume
    
    result_state = resume_graph.invoke(initial_state)
    final_resume = result_state["generated_resume"]

    # Validate the JSON data against the ResumeCreate schema
    try:
        generated_resume = ResumeCreate(**final_resume)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Invalid generated resume data: {str(e)}")

    # Return the generated resume
    return GeneratedResumeResponse(generated_resume=generated_resume)