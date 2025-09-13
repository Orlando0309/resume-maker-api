from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, User, UserProfile
from schemas import GenerateResumeRequest, OptimizeRequest, ResumeCreate
from utils import get_current_user
import json
import logging
from pydantic import BaseModel
import os
import time
from typing import Dict, Any, Union
from dotenv import load_dotenv
from functools import lru_cache
load_dotenv() 
from LLM.agents import resume_graph

import google.generativeai as genai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Configuration
class OptimizationConfig:
    MODEL_NAME = "gemini-2.0-flash-lite"
    MAX_RETRIES = 3
    TIMEOUT_SECONDS = 30
    RETRY_DELAY = 1

# Environment setup
GEMINI_API_TOKEN = os.getenv("GEMINI_API_TOKEN")
if not GEMINI_API_TOKEN:
    raise ValueError("GEMINI_API_TOKEN environment variable not set")
genai.configure(api_key=GEMINI_API_TOKEN)

# Custom Exceptions
class OptimizationError(Exception):
    """Base exception for optimization errors"""
    pass

class APIServiceUnavailable(OptimizationError):
    """Raised when external API is unavailable"""
    pass

class InvalidResumeData(OptimizationError):
    """Raised when resume data is invalid"""
    pass

# Response Models
class OptimizedResumeResponse(BaseModel):
    optimized_resume: ResumeCreate
    
class GeneratedResumeResponse(BaseModel):
    generated_resume: ResumeCreate

# Utility Functions
def serialize_resume_data(resume_or_profile: Union[Resume, UserProfile], include_used_skills: bool = True) -> Dict[str, Any]:
    """Serialize resume or profile data to dictionary format."""
    data = {
        "personal_info": resume_or_profile.personal_info or {},
        "experiences": [
            {
                "title": e.title,
                "company": e.company,
                "description": e.description,
                "start_date": e.start_date.isoformat(),
                "end_date": e.end_date.isoformat() if e.end_date else None
            }
            for e in resume_or_profile.experiences
        ],
        "educations": [
            {
                "school": edu.school,
                "degree": edu.degree,
                "start_date": edu.start_date.isoformat(),
                "end_date": edu.end_date.isoformat() if edu.end_date else None,
                **({"used_skills": edu.used_skills} if include_used_skills and hasattr(edu, 'used_skills') else {})
            }
            for edu in resume_or_profile.educations
        ],
        "skills": [
            {"skill_name": s.skill_name}
            for s in resume_or_profile.skills
        ],
        "certifications": [
            {
                "title": cert.title,
                "authority": cert.authority,
                "date": cert.date.isoformat()
            }
            for cert in resume_or_profile.certifications
        ],
        "projects": [
            {
                "title": proj.title,
                "description": proj.description,
                "link": proj.link,
                "used_skills": proj.used_skills,
            }
            for proj in resume_or_profile.projects
        ]
    }
    return data

@lru_cache(maxsize=100)
def get_cached_optimization(resume_hash: str, job_desc_hash: str) -> Dict[str, Any]:
    """Cache frequently optimized resume combinations."""
    # This would integrate with a proper caching system like Redis in production
    pass

def query_to_llm_with_retry(prompt: str, max_retries: int = OptimizationConfig.MAX_RETRIES) -> str:
    """Query the Gemini API with retry logic and proper error handling."""
    model = genai.GenerativeModel(OptimizationConfig.MODEL_NAME)
    
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            logger.info(f"Making API call to Gemini (attempt {attempt + 1}/{max_retries})")
            response = model.generate_content(prompt)
            
            if not response.text:
                raise APIServiceUnavailable("Empty response from Gemini API")
                
            generated_text = response.text.strip()
            logger.info("Successfully received response from Gemini API")
            return generated_text
            
        except Exception as e:
            last_exception = e
            logger.warning(f"API call attempt {attempt + 1} failed: {str(e)}")
            
            if attempt < max_retries - 1:
                delay = OptimizationConfig.RETRY_DELAY * (2 ** attempt)  # Exponential backoff
                logger.info(f"Retrying in {delay} seconds...")
                time.sleep(delay)
    
    # If all retries failed
    logger.error(f"All {max_retries} API call attempts failed")
    raise APIServiceUnavailable(f"Gemini API call failed after {max_retries} attempts: {str(last_exception)}")

# Prompt Templates (should be moved to external config files in production)
def build_optimization_prompt(resume_data: Dict[str, Any], job_description: str) -> str:
    """Build the optimization prompt from template."""
    return (
        "You are an HR professional reviewing a candidate's resume against a specific job description. "
        "Your goal is to enhance the candidate's skills, education, experiences, certifications, and projects so that they better meet "
        "the job requirements, while strictly preserving the candidate's original personal information "
        "(full_name, email, phone, address, linkedin, facebook, and x) and all the original resume content. Do not create new personal data, "
        "modify existing personal details, or add any extra fields not present in the candidate's original resume.\n\n"
        
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

def parse_llm_response(response_text: str) -> Dict[str, Any]:
    """Parse and validate LLM response JSON."""
    try:
        # Remove any markdown formatting if present
        cleaned_response = response_text.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned_response)
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse LLM response as JSON: {str(e)}")
        logger.error(f"Response was: {response_text[:500]}...")  # Log first 500 chars
        raise InvalidResumeData(f"Failed to parse optimized resume JSON: {str(e)}")

def validate_optimized_resume(resume_json: Dict[str, Any]) -> ResumeCreate:
    """Validate optimized resume data against schema."""
    try:
        return ResumeCreate(**resume_json)
    except Exception as e:
        logger.error(f"Invalid optimized resume data: {str(e)}")
        raise InvalidResumeData(f"Invalid optimized resume data: {str(e)}")

@router.post("/optimize-resume", response_model=OptimizedResumeResponse)
def optimize_resume(request: OptimizeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Optimize an existing resume against a job description."""
    try:
        # Fetch resume with proper error handling
        resume = db.query(Resume).filter(Resume.id == request.resume_id, Resume.user_id == user.id).first()
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found")

        logger.info(f"Optimizing resume {resume.id} for user {user.id}")

        # Serialize resume data using common function
        resume_data = serialize_resume_data(resume, include_used_skills=False)
        job_description = request.job_description
        
        # Build optimization prompt
        optimization_prompt = build_optimization_prompt(resume_data, job_description)

        # Query LLM with retry logic
        optimized_resume_str = query_to_llm_with_retry(optimization_prompt)

        # Parse and validate response
        optimized_resume_json = parse_llm_response(optimized_resume_str)
        optimized_resume = validate_optimized_resume(optimized_resume_json)

        logger.info(f"Successfully optimized resume {resume.id}")
        return OptimizedResumeResponse(optimized_resume=optimized_resume)
        
    except (APIServiceUnavailable, InvalidResumeData) as e:
        logger.error(f"Optimization failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during optimization: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during optimization")

@router.post("/generate-resume", response_model=GeneratedResumeResponse)
def generate_resume(request: GenerateResumeRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    """Generate a new resume from user profile data and job description."""
    try:
        # Retrieve the user's profile from the database
        profile = db.query(UserProfile).filter(UserProfile.user_id == user.id).first()
        if not profile:
            raise HTTPException(status_code=404, detail="User profile not found")

        logger.info(f"Generating resume for user {user.id}")

        # Serialize profile data using common function
        profile_data = serialize_resume_data(profile, include_used_skills=True)
        job_description = request.job_description

        # Prepare initial state for resume generation graph
        initial_state = {
            "profile_data": profile_data,
            "job_description": job_description,
            "generated_resume": {},
            "score": 0,
            "attempts": 0
        }
        
        # Invoke the resume generation graph
        logger.info("Invoking resume generation graph")
        result_state = resume_graph.invoke(initial_state)
        final_resume = result_state["generated_resume"]

        # Validate the generated resume data
        generated_resume = validate_optimized_resume(final_resume)

        logger.info(f"Successfully generated resume for user {user.id}")
        return GeneratedResumeResponse(generated_resume=generated_resume)
        
    except InvalidResumeData as e:
        logger.error(f"Resume generation validation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during resume generation: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error during resume generation")