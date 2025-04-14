import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, Experience, Education, Skill, Certification, Project, User
from schemas import ResumeCreate, ResumeResponse
from utils import get_current_user

router = APIRouter()

@router.post("/resume", response_model=ResumeResponse)
def create_resume(resume: ResumeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_resume = Resume(user_id=user.id, personal_info=resume.personal_info.dict())
    db.add(db_resume)
    db.commit()
    db.refresh(db_resume)
    for exp in resume.experiences:
        db.add(Experience(resume_id=db_resume.id, **exp.dict()))
    for edu in resume.educations:
        db.add(Education(resume_id=db_resume.id, **edu.dict()))
    for skill in resume.skills:
        db.add(Skill(resume_id=db_resume.id, **skill.dict()))
    for cert in resume.certifications:
        db.add(Certification(resume_id=db_resume.id, **cert.dict()))
    for proj in resume.projects:
        db.add(Project(resume_id=db_resume.id, **proj.dict()))
    db.commit()
    return db_resume

@router.get("/resume/{resume_id}", response_model=ResumeResponse)
def get_resume(resume_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    print(resume)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    return resume

@router.put("/resume/{resume_id}", response_model=ResumeResponse)
def update_resume(resume_id: uuid.UUID, resume: ResumeCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not db_resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db_resume.personal_info = resume.personal_info.dict()
    for model in [Experience, Education, Skill, Certification, Project]:
        db.query(model).filter(model.resume_id == resume_id).delete()
    for exp in resume.experiences:
        db.add(Experience(resume_id=resume_id, **exp.dict()))
    for edu in resume.educations:
        db.add(Education(resume_id=resume_id, **edu.dict()))
    for skill in resume.skills:
        db.add(Skill(resume_id=resume_id, **skill.dict()))
    for cert in resume.certifications:
        db.add(Certification(resume_id=resume_id, **cert.dict()))
    for proj in resume.projects:
        db.add(Project(resume_id=resume_id, **proj.dict()))
    db.commit()
    db.refresh(db_resume)
    return db_resume

@router.delete("/resume/{resume_id}")
def delete_resume(resume_id: uuid.UUID, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resume = db.query(Resume).filter(Resume.id == resume_id, Resume.user_id == user.id).first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    db.delete(resume)
    db.commit()
    return {"message": "Resume deleted"}