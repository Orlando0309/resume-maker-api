from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, User
from schemas import GeneratePDFRequest
from utils import get_current_user
from jinja2 import Template, Environment, FileSystemLoader
import pdfkit
import os
import uuid
from datetime import date

router = APIRouter()

# Set up Jinja2 environment
env = Environment(loader=FileSystemLoader("templates"))

# Custom filter for date formatting
def format_date(value, format_string="%b %Y"):
    if isinstance(value, date) and value:
        return value.strftime(format_string)
    return "Present" if format_string == "%b %Y" else ""

env.filters["strftime"] = format_date

@router.post("/generate-resume")
def generate_resume(request: GeneratePDFRequest, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    # Validate resume_id
    try:
        resume_id = uuid.UUID(str(request.resume_id))
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid resume ID")

    # Fetch resume from database
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or not owned by user")

    # Prepare resume data with all sections
    resume_data = {
        "personal_info": resume.personal_info or {},  # Handle case where personal_info is None
        "experiences": [
            {
                "title": e.title,
                "company": e.company,
                "description": e.description,
                "start_date": e.start_date,
                "end_date": e.end_date
            }
            for e in resume.experiences
        ],
        "educations": [
            {
                "school": edu.school,
                "degree": edu.degree,
                "start_date": edu.start_date,
                "end_date": edu.end_date
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
                "date": cert.date
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

    # Load and render HTML template
    template_path = f"{request.template_id}.html"
    try:
        template = env.get_template(template_path)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Template not found: {template_path}")

    html = template.render(resume=resume_data)

    # Generate unique PDF filename to avoid overwrites
    pdf_filename = f"resume_{uuid.uuid4()}.pdf"
    try:
        pdfkit.from_string(html, pdf_filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail="Failed to generate PDF")

    # Return the PDF file as a response
    return FileResponse(pdf_filename, media_type="application/pdf", filename="resume.pdf")