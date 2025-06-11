from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Form
from sqlalchemy.orm import Session
from typing import Optional
from datetime import date, datetime
from models import User
from auth import get_db, get_current_user, verify_password, get_password_hash
from pydantic import BaseModel, EmailStr
import shutil # For file upload
import os # For file path anjay

router = APIRouter(prefix="/profile", tags=["User Profile"])

# Response Models
class UserProfileData(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    username: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None
    profile_picture: Optional[str] = None
    class Config:
        from_attributes = True

class UserProfileResponse(BaseModel):
    success: bool
    data: UserProfileData

class SimpleResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None

class UpdateProfileRequest(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    phone_number: Optional[str] = None

class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    confirm_password: str

# Endpoint: GET /profile
@router.get("", response_model=UserProfileResponse)
def get_profile(user: User = Depends(get_current_user)):
    return {"success": True, "data": user}

# Endpoint: PUT /profile
@router.put("", response_model=SimpleResponse)
def update_profile(req: UpdateProfileRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Check if username exists if being updated and is not current user's username
    if req.username and req.username != user.username:
        existing_user = db.query(User).filter(User.username == req.username).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username sudah dipakai")

    update_data = req.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)

    db.commit()
    # db.refresh(user) # Not needed here

    return {"success": True, "message": "Profil berhasil diupdate"}

# Endpoint: POST /profile/upload-photo
# Set upload directory
UPLOAD_DIRECTORY = "./uploads"
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

@router.post("/upload-photo", response_model=SimpleResponse)
async def upload_profile_photo(file: UploadFile = File(...), user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Validate file type and size if needed
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in [".jpg", ".jpeg", ".png"]:
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Format file tidak diizinkan. Gunakan JPG, JPEG, atau PNG.")

    # Generate unique filename
    filename = f"{user.id}_{datetime.utcnow().strftime('%Y%m%d%H%M%S')}{file_extension}"
    file_path = os.path.join(UPLOAD_DIRECTORY, filename)

    # Save file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Update user profile picture URL (use relative path or a base URL)
    user.profile_picture = f"/uploads/{filename}" # Example URL, adjust as needed
    db.commit()
    db.refresh(user)

    return {"success": True, "message": "Foto profil berhasil diupload", "data": {"profile_picture": user.profile_picture}}

# Endpoint: PUT /profile/change-password
@router.put("/change-password", response_model=SimpleResponse)
def change_password(req: ChangePasswordRequest, user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Verify current password
    if not verify_password(req.current_password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Password saat ini salah")

    # Check if new password matches confirm password
    if req.new_password != req.confirm_password:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Konfirmasi password tidak cocok")

    # Hash and update password
    user.hashed_password = get_password_hash(req.new_password)
    db.commit()
    # db.refresh(user) # Not needed here

    return {"success": True, "message": "Password berhasil diubah"} 