from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import Resume, Application, User
from schemas import ApplicationCreate, ApplicationResponse, ResumeResponse
from utils import get_current_user

router = APIRouter()

@router.get("/dashboard")
def get_dashboard(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    resumes = db.query(Resume).filter(Resume.user_id == user.id).all()
    applications = db.query(Application).filter(Application.user_id == user.id).all()
    return {"resumes": resumes, "applications": applications}

@router.post("/application", response_model=ApplicationResponse)
def create_application(app: ApplicationCreate, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    db_app = Application(user_id=user.id, **app.dict())
    db.add(db_app)
    db.commit()
    db.refresh(db_app)
    return db_app