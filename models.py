from sqlalchemy import Column, String, DateTime, ForeignKey, JSON, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String)
    email = Column(String, unique=True)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    resumes = relationship("Resume", back_populates="user")
    applications = relationship("Application", back_populates="user")

class Resume(Base):
    __tablename__ = "resumes"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    personal_info = Column(JSON)  # Stores structured data like name, email, phone
    created_at = Column(DateTime, default=datetime.utcnow)
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