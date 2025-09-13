from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import desc, func, and_
from database import get_db
from models import Application, ApplicationStatusHistory, User, Resume
from schemas import (
    ApplicationCreate, ApplicationUpdate, ApplicationResponse, 
    ApplicationWithResumeResponse, ApplicationStatusHistoryResponse,
    OptimizeResumeForApplicationRequest, ApplicationAnalyticsResponse,
    ResumeCreate
)
from utils import get_current_user
import logging
from typing import List, Optional
from datetime import datetime, date, timedelta
import uuid

# Import optimization functions
from optimization import (
    serialize_resume_data, query_to_llm_with_retry, 
    build_optimization_prompt, parse_llm_response, 
    validate_optimized_resume, APIServiceUnavailable, InvalidResumeData
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Application Status Constants
VALID_STATUSES = ["applied", "under_review", "interview", "rejected", "accepted", "withdrawn"]

def create_status_history(db: Session, application_id: uuid.UUID, status: str, notes: Optional[str] = None):
    """Create a status history entry for an application."""
    status_history = ApplicationStatusHistory(
        application_id=application_id,
        status=status,
        notes=notes
    )
    db.add(status_history)
    return status_history

def validate_status(status: str) -> bool:
    """Validate if the status is in the allowed list."""
    return status in VALID_STATUSES

@router.post("/applications", response_model=ApplicationResponse)
def create_application(
    application_data: ApplicationCreate, 
    db: Session = Depends(get_db), 
    user: User = Depends(get_current_user)
):
    """Create a new job application."""
    try:
        # Validate resume_id if provided
        if application_data.resume_id:
            resume = db.query(Resume).filter(
                Resume.id == application_data.resume_id,
                Resume.user_id == user.id
            ).first()
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")

        # Validate status
        if not validate_status(application_data.status):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            )

        # Set default application date if not provided
        app_date = application_data.application_date or date.today()

        # Create the application
        application = Application(
            user_id=user.id,
            resume_id=application_data.resume_id,
            job_title=application_data.job_title,
            company_name=application_data.company_name,
            job_description=application_data.job_description,
            application_date=app_date,
            status=application_data.status,
            source=application_data.source,
            salary_range=application_data.salary_range,
            location=application_data.location,
            notes=application_data.notes
        )

        db.add(application)
        db.commit()
        db.refresh(application)

        # Create initial status history
        create_status_history(db, application.id, application_data.status, "Application created")
        db.commit()

        logger.info(f"Created application {application.id} for user {user.id}")
        return application

    except Exception as e:
        db.rollback()
        logger.error(f"Error creating application: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create application")

@router.get("/applications", response_model=List[ApplicationResponse])
def get_applications(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    status: Optional[str] = Query(None),
    company: Optional[str] = Query(None),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get user's job applications with optional filtering."""
    try:
        query = db.query(Application).filter(Application.user_id == user.id)

        # Apply filters
        if status:
            if not validate_status(status):
                raise HTTPException(
                    status_code=400, 
                    detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
                )
            query = query.filter(Application.status == status)

        if company:
            query = query.filter(Application.company_name.ilike(f"%{company}%"))

        # Order by application date (newest first)
        query = query.order_by(desc(Application.application_date))

        applications = query.offset(skip).limit(limit).all()
        return applications

    except Exception as e:
        logger.error(f"Error fetching applications: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch applications")

@router.get("/applications/{application_id}", response_model=ApplicationWithResumeResponse)
def get_application(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get a specific application by ID with resume details."""
    try:
        application = db.query(Application).options(
            joinedload(Application.resume),
            joinedload(Application.status_history)
        ).filter(
            Application.id == application_id,
            Application.user_id == user.id
        ).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        return application

    except Exception as e:
        logger.error(f"Error fetching application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch application")

@router.put("/applications/{application_id}", response_model=ApplicationResponse)
def update_application(
    application_id: uuid.UUID,
    application_update: ApplicationUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Update an application."""
    try:
        application = db.query(Application).filter(
            Application.id == application_id,
            Application.user_id == user.id
        ).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # Validate resume_id if provided
        if application_update.resume_id:
            resume = db.query(Resume).filter(
                Resume.id == application_update.resume_id,
                Resume.user_id == user.id
            ).first()
            if not resume:
                raise HTTPException(status_code=404, detail="Resume not found")

        # Validate status if provided
        if application_update.status and not validate_status(application_update.status):
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}"
            )

        # Update fields
        update_data = application_update.dict(exclude_unset=True)
        
        # Track status changes
        if 'status' in update_data and update_data['status'] != application.status:
            create_status_history(
                db, 
                application.id, 
                update_data['status'], 
                application_update.notes or "Status updated"
            )

        for field, value in update_data.items():
            setattr(application, field, value)

        application.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(application)

        logger.info(f"Updated application {application.id}")
        return application

    except Exception as e:
        db.rollback()
        logger.error(f"Error updating application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update application")

@router.delete("/applications/{application_id}")
def delete_application(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Delete an application."""
    try:
        application = db.query(Application).filter(
            Application.id == application_id,
            Application.user_id == user.id
        ).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        db.delete(application)
        db.commit()

        logger.info(f"Deleted application {application_id}")
        return {"message": "Application deleted successfully"}

    except Exception as e:
        db.rollback()
        logger.error(f"Error deleting application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete application")

@router.post("/applications/{application_id}/optimize-resume", response_model=dict)
def optimize_resume_for_application(
    application_id: uuid.UUID,
    request: OptimizeResumeForApplicationRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Optimize or generate a resume specifically for a job application."""
    try:
        # Get the application
        application = db.query(Application).filter(
            Application.id == application_id,
            Application.user_id == user.id
        ).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        if not application.job_description:
            raise HTTPException(status_code=400, detail="Job description is required for resume optimization")

        optimized_resume = None
        resume_title = f"{application.job_title} - {application.company_name}"

        if request.generate_new_resume:
            # Generate new resume from user profile
            from optimization import generate_resume
            from schemas import GenerateResumeRequest
            
            generate_request = GenerateResumeRequest(job_description=application.job_description)
            result = generate_resume(generate_request, db, user)
            optimized_resume = result.generated_resume
        else:
            # Optimize existing resume
            if not application.resume_id:
                raise HTTPException(status_code=400, detail="No resume attached to application for optimization")

            from optimization import OptimizeRequest
            from optimization import optimize_resume
            
            optimize_request = OptimizeRequest(
                resume_id=application.resume_id,
                job_description=application.job_description
            )
            result = optimize_resume(optimize_request, db, user)
            optimized_resume = result.optimized_resume

        # Create new resume from optimized data
        new_resume = Resume(
            user_id=user.id,
            title=resume_title,
            personal_info=optimized_resume.personal_info.dict()
        )
        db.add(new_resume)
        db.flush()  # Get the ID

        # Create resume sections
        from models import Experience, Education, Skill, Certification, Project
        
        # Add experiences
        for exp in optimized_resume.experiences:
            experience = Experience(
                resume_id=new_resume.id,
                title=exp.title,
                company=exp.company,
                description=exp.description,
                start_date=exp.start_date,
                end_date=exp.end_date
            )
            db.add(experience)

        # Add educations
        for edu in optimized_resume.educations:
            education = Education(
                resume_id=new_resume.id,
                school=edu.school,
                degree=edu.degree,
                start_date=edu.start_date,
                end_date=edu.end_date,
                used_skills=edu.used_skills
            )
            db.add(education)

        # Add skills
        for skill in optimized_resume.skills:
            skill_obj = Skill(
                resume_id=new_resume.id,
                skill_name=skill.skill_name
            )
            db.add(skill_obj)

        # Add certifications
        for cert in optimized_resume.certifications:
            certification = Certification(
                resume_id=new_resume.id,
                title=cert.title,
                authority=cert.authority,
                date=cert.date
            )
            db.add(certification)

        # Add projects
        for proj in optimized_resume.projects:
            project = Project(
                resume_id=new_resume.id,
                title=proj.title,
                description=proj.description,
                link=proj.link,
                used_skills=proj.used_skills
            )
            db.add(project)

        # Update application with new resume
        application.resume_id = new_resume.id
        application.updated_at = datetime.utcnow()

        db.commit()

        logger.info(f"Optimized resume for application {application_id}, created resume {new_resume.id}")
        
        return {
            "message": "Resume optimized successfully",
            "application_id": str(application_id),
            "resume_id": str(new_resume.id),
            "resume_title": resume_title
        }

    except (APIServiceUnavailable, InvalidResumeData) as e:
        db.rollback()
        logger.error(f"Resume optimization failed for application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        db.rollback()
        logger.error(f"Error optimizing resume for application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to optimize resume for application")

@router.get("/applications/analytics", response_model=ApplicationAnalyticsResponse)
def get_application_analytics(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get analytics and insights for user's applications."""
    try:
        # Total applications
        total_applications = db.query(Application).filter(Application.user_id == user.id).count()

        # Applications by status
        status_counts = db.query(
            Application.status,
            func.count(Application.id).label('count')
        ).filter(Application.user_id == user.id).group_by(Application.status).all()
        
        applications_by_status = {status: count for status, count in status_counts}

        # Applications by month (last 12 months)
        twelve_months_ago = date.today() - timedelta(days=365)
        monthly_counts = db.query(
            func.date_trunc('month', Application.application_date).label('month'),
            func.count(Application.id).label('count')
        ).filter(
            and_(
                Application.user_id == user.id,
                Application.application_date >= twelve_months_ago
            )
        ).group_by(func.date_trunc('month', Application.application_date)).all()
        
        applications_by_month = {
            month.strftime('%Y-%m'): count 
            for month, count in monthly_counts
        }

        # Top companies
        top_companies = db.query(
            Application.company_name,
            func.count(Application.id).label('count')
        ).filter(Application.user_id == user.id).group_by(
            Application.company_name
        ).order_by(desc('count')).limit(10).all()
        
        top_companies_list = [
            {"company": company, "applications": count} 
            for company, count in top_companies
        ]

        # Response rate (applications that got past "applied" status)
        total_with_responses = db.query(Application).filter(
            and_(
                Application.user_id == user.id,
                Application.status.in_(['under_review', 'interview', 'rejected', 'accepted'])
            )
        ).count()
        
        response_rate = (total_with_responses / total_applications * 100) if total_applications > 0 else 0

        # Average days to response (simplified calculation)
        # This would need more complex logic in a real implementation
        average_days_to_response = None

        return ApplicationAnalyticsResponse(
            total_applications=total_applications,
            applications_by_status=applications_by_status,
            applications_by_month=applications_by_month,
            top_companies=top_companies_list,
            response_rate=round(response_rate, 2),
            average_days_to_response=average_days_to_response
        )

    except Exception as e:
        logger.error(f"Error fetching application analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch application analytics")

@router.get("/applications/{application_id}/status-history", response_model=List[ApplicationStatusHistoryResponse])
def get_application_status_history(
    application_id: uuid.UUID,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Get status history for a specific application."""
    try:
        # Verify application belongs to user
        application = db.query(Application).filter(
            Application.id == application_id,
            Application.user_id == user.id
        ).first()

        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # Get status history
        status_history = db.query(ApplicationStatusHistory).filter(
            ApplicationStatusHistory.application_id == application_id
        ).order_by(ApplicationStatusHistory.changed_at).all()

        return status_history

    except Exception as e:
        logger.error(f"Error fetching status history for application {application_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch status history")
