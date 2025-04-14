from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import date, datetime
import uuid

# Authentication
class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

# Resume Sections
class PersonalInfo(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    linkedin: Optional[str] = None  # New field for LinkedIn
    facebook: Optional[str] = None  # New field for Facebook
    x: Optional[str] = None  # New field for X
class ExperienceBase(BaseModel):
    title: str
    company: str
    description: str
    start_date: date
    end_date: Optional[date] = None

class EducationBase(BaseModel):
    school: str
    degree: str
    start_date: date
    end_date: Optional[date] = None

class SkillBase(BaseModel):
    skill_name: str

class CertificationBase(BaseModel):
    title: str
    authority: str
    date: date

class ProjectBase(BaseModel):
    title: str
    description: str
    link: Optional[str] = None
    used_skills: List[str] = []

class ResumeCreate(BaseModel):
    personal_info: PersonalInfo
    experiences: List[ExperienceBase] = []
    educations: List[EducationBase] = []
    skills: List[SkillBase] = []
    certifications: List[CertificationBase] = []
    projects: List[ProjectBase] = []

class ResumeResponse(ResumeCreate):
    id: uuid.UUID
    created_at: datetime
    class Config:
        orm_mode = True

# Optimization
class OptimizeRequest(BaseModel):
    resume_id: uuid.UUID
    job_description: str

class OptimizeResponse(BaseModel):
    suggestions: str
    ats_optimizations: str

# PDF Generation
class GeneratePDFRequest(BaseModel):
    resume_id: uuid.UUID
    template_id: str

# Application
class ApplicationCreate(BaseModel):
    resume_id: Optional[uuid.UUID] = None
    job_title: str
    company_name: str
    application_date: date
    status: str

class ApplicationResponse(BaseModel):
    id: uuid.UUID
    resume_id: Optional[uuid.UUID]
    job_title: str
    company_name: str
    application_date: date
    status: str
    class Config:
        orm_mode = True