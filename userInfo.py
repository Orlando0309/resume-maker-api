import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from database import get_db
from models import UserProfile, UserExperience, UserEducation, UserSkill, UserCertification, UserProject, User
from schemas import UserProfileCreate, UserProfileResponse, UserProfileUpdate
from utils import get_current_user

router = APIRouter(prefix="/user-profile", tags=["User Profile"])

@router.post("/", response_model=UserProfileResponse, status_code=status.HTTP_201_CREATED)
def create_user_profile(
    profile: UserProfileCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Create a new user profile for the authenticated user.
    Raises an error if a profile already exists.
    """
    # Check if a profile already exists for the user
    existing_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if existing_profile:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User profile already exists")

    # Create the new user profile
    db_profile = UserProfile(
        user_id=current_user.id,
        personal_info=profile.personal_info.dict() if profile.personal_info else None
    )
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)

    # Add related data if provided
    for exp in profile.experiences or []:
        db.add(UserExperience(profile_id=db_profile.id, **exp.dict()))
    for edu in profile.educations or []:
        db.add(UserEducation(profile_id=db_profile.id, **edu.dict()))
    for skill in profile.skills or []:
        db.add(UserSkill(profile_id=db_profile.id, **skill.dict()))
    for cert in profile.certifications or []:
        db.add(UserCertification(profile_id=db_profile.id, **cert.dict()))
    for proj in profile.projects or []:
        db.add(UserProject(profile_id=db_profile.id, **proj.dict()))

    db.commit()
    return db_profile

@router.get("/", response_model=UserProfileResponse)
def get_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Retrieve the authenticated user's profile, including all related data.
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")
    return profile

@router.put("/", response_model=UserProfileResponse)
def updatefacieuser_profile(
    profile_update: UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update the authenticated user's profile. Replaces all related data with the provided data.
    """
    db_profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not db_profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    # Update personal_info only if provided in the request
    if profile_update.personal_info is not None:
        db_profile.personal_info = profile_update.personal_info.dict()

    # Delete all existing related data
    for model in [UserExperience, UserEducation, UserSkill, UserCertification, UserProject]:
        db.query(model).filter(model.profile_id == db_profile.id).delete()

    # Add new related data if provided
    for exp in profile_update.experiences or []:
        db.add(UserExperience(profile_id=db_profile.id, **exp.dict()))
    for edu in profile_update.educations or []:
        db.add(UserEducation(profile_id=db_profile.id, **edu.dict()))
    for skill in profile_update.skills or []:
        db.add(UserSkill(profile_id=db_profile.id, **skill.dict()))
    for cert in profile_update.certifications or []:
        db.add(UserCertification(profile_id=db_profile.id, **cert.dict()))
    for proj in profile_update.projects or []:
        db.add(UserProject(profile_id=db_profile.id, **proj.dict()))

    db.commit()
    db.refresh(db_profile)
    return db_profile

@router.delete("/")
def delete_user_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Delete the authenticated user's profile and all related data.
    """
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")
    db.delete(profile)
    db.commit()
    return {"message": "User profile deleted"}