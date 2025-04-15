from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base

# New UserProfile model to store reusable data
class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), unique=True)
    personal_info = Column(JSON)  # Name, email, phone, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="profile")
    experiences = relationship("UserExperience", back_populates="profile", cascade="all, delete-orphan")
    educations = relationship("UserEducation", back_populates="profile", cascade="all, delete-orphan")
    skills = relationship("UserSkill", back_populates="profile", cascade="all, delete-orphan")
    certifications = relationship("UserCertification", back_populates="profile", cascade="all, delete-orphan")
    projects = relationship("UserProject", back_populates="profile", cascade="all, delete-orphan")

# Update User model
class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    resumes = relationship("Resume", back_populates="user")
    applications = relationship("Application", back_populates="user")

# New models for user-level data (similar to resume-specific models)
class UserExperience(Base):
    __tablename__ = "user_experiences"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"))
    title = Column(String)
    company = Column(String)
    description = Column(String)
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    profile = relationship("UserProfile", back_populates="experiences")

class UserEducation(Base):
    __tablename__ = "user_educations"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"))
    school = Column(String)
    degree = Column(String)
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    profile = relationship("UserProfile", back_populates="educations")

class UserSkill(Base):
    __tablename__ = "user_skills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"))
    skill_name = Column(String)
    profile = relationship("UserProfile", back_populates="skills")

class UserCertification(Base):
    __tablename__ = "user_certifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"))
    title = Column(String)
    authority = Column(String)
    date = Column(Date)
    profile = relationship("UserProfile", back_populates="certifications")

class UserProject(Base):
    __tablename__ = "user_projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_id = Column(UUID(as_uuid=True), ForeignKey("user_profiles.id"))
    title = Column(String)
    description = Column(String)
    link = Column(String, nullable=True)
    used_skills = Column(JSON, default=list)
    profile = relationship("UserProfile", back_populates="projects")

# Updated Resume model
class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    title = Column(String, nullable=False)  # Added for clarity
    personal_info = Column(JSON)  # Still stored here, but can be pre-filled
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user = relationship("User", back_populates="resumes")
    experiences = relationship("Experience", back_populates="resume", cascade="all, delete-orphan")
    educations = relationship("Education", back_populates="resume", cascade="all, delete-orphan")
    skills = relationship("Skill", back_populates="resume", cascade="all, delete-orphan")
    certifications = relationship("Certification", back_populates="resume", cascade="all, delete-orphan")
    projects = relationship("Project", back_populates="resume", cascade="all, delete-orphan")
class Experience(Base):
    __tablename__ = "experience"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"))
    title = Column(String)
    company = Column(String)
    description = Column(String)
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    resume = relationship("Resume", back_populates="experiences")

class Education(Base):
    __tablename__ = "education"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"))
    school = Column(String)
    degree = Column(String)
    start_date = Column(Date)
    end_date = Column(Date, nullable=True)
    resume = relationship("Resume", back_populates="educations")

class Skill(Base):
    __tablename__ = "skills"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"))
    skill_name = Column(String)
    resume = relationship("Resume", back_populates="skills")

class Certification(Base):
    __tablename__ = "certifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"))
    title = Column(String)
    authority = Column(String)
    date = Column(Date)
    resume = relationship("Resume", back_populates="certifications")

class Project(Base):
    __tablename__ = "projects"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"))
    title = Column(String)
    description = Column(String)
    link = Column(String, nullable=True)
    used_skills = Column(JSON, default=list) 
    resume = relationship("Resume", back_populates="projects")

class Application(Base):
    __tablename__ = "applications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    resume_id = Column(UUID(as_uuid=True), ForeignKey("resumes.id"), nullable=True)
    job_title = Column(String)
    company_name = Column(String)
    application_date = Column(Date)
    status = Column(String)
    user = relationship("User", back_populates="applications")
    resume = relationship("Resume")