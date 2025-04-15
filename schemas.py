from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import date, datetime
import uuid

# Authentication Schemas
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

# Personal Info Schema (used for input)
class PersonalInfo(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    linkedin: Optional[str] = None
    facebook: Optional[str] = None
    x: Optional[str] = None

# Resume Section Base Schemas (for Resume input)
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

# UserProfile Section Base Schemas (for UserProfile input)
class UserExperienceBase(BaseModel):
    title: str
    company: str
    description: str
    start_date: date
    end_date: Optional[date] = None

class UserEducationBase(BaseModel):
    school: str
    degree: str
    start_date: date
    end_date: Optional[date] = None

class UserSkillBase(BaseModel):
    skill_name: str

class UserCertificationBase(BaseModel):
    title: str
    authority: str
    date: date

class UserProjectBase(BaseModel):
    title: str
    description: str
    link: Optional[str] = None
    used_skills: List[str] = []

# UserProfile Schemas
class UserProfileCreate(BaseModel):
    personal_info: Optional[PersonalInfo] = None
    experiences: Optional[List[UserExperienceBase]] = []
    educations: Optional[List[UserEducationBase]] = []
    skills: Optional[List[UserSkillBase]] = []
    certifications: Optional[List[UserCertificationBase]] = []
    projects: Optional[List[UserProjectBase]] = []

class UserProfileUpdate(UserProfileCreate):
    pass

# Response Schemas for UserProfile Related Models
class UserExperienceResponse(UserExperienceBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class UserEducationResponse(UserEducationBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class UserSkillResponse(UserSkillBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class UserCertificationResponse(UserCertificationBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class UserProjectResponse(UserProjectBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class UserProfileResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    personal_info: Optional[Dict[str, Any]] = None  # JSON column
    created_at: datetime
    updated_at: datetime
    experiences: List[UserExperienceResponse] = []
    educations: List[UserEducationResponse] = []
    skills: List[UserSkillResponse] = []
    certifications: List[UserCertificationResponse] = []
    projects: List[UserProjectResponse] = []

    class Config:
        orm_mode = True

# Resume Schemas
class ResumeCreate(BaseModel):
    title: str  # Added to match model
    personal_info: PersonalInfo
    experiences: List[ExperienceBase] = []
    educations: List[EducationBase] = []
    skills: List[SkillBase] = []
    certifications: List[CertificationBase] = []
    projects: List[ProjectBase] = []

# Response Schemas for Resume Related Models
class ExperienceResponse(ExperienceBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class EducationResponse(EducationBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class SkillResponse(SkillBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class CertificationResponse(CertificationBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class ProjectResponse(ProjectBase):
    id: uuid.UUID

    class Config:
        orm_mode = True

class ResumeResponse(BaseModel):
    id: uuid.UUID
    title: str  # Added to match model
    personal_info: Dict[str, Any]  # JSON column
    created_at: datetime
    updated_at: datetime  # Added to match model
    experiences: List[ExperienceResponse] = []
    educations: List[EducationResponse] = []
    skills: List[SkillResponse] = []
    certifications: List[CertificationResponse] = []
    projects: List[ProjectResponse] = []

    class Config:
        orm_mode = True

# Optimization Schemas
class OptimizeRequest(BaseModel):
    resume_id: uuid.UUID
    job_description: str

class GenerateResumeRequest(BaseModel):
    job_description: str
    
class OptimizeResponse(BaseModel):
    suggestions: str
    ats_optimizations: str

# PDF Generation Schema
class GeneratePDFRequest(BaseModel):
    resume_id: uuid.UUID
    template_id: str

# Application Schemas
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