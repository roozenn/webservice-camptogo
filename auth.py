from fastapi import APIRouter, HTTPException, Depends, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, constr
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from jose import jwt, JWTError
from datetime import timedelta, datetime
from db import SessionLocal
from models import User, BlacklistedToken

SECRET_KEY = "supersecretkey"  # Ganti di produksi
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

security = HTTPBearer()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt, int((expire - datetime.utcnow()).total_seconds())

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    print("TOKEN:", token)
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        # Cek apakah token ada di blacklist
        blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
        if blacklisted:
            raise credentials_exception
            
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print("PAYLOAD:", payload)
        user_id = payload.get("sub")
        if user_id is None:
            print("User ID None")
            raise credentials_exception
        user_id = int(user_id)
    except (JWTError, ValueError, TypeError) as e:
        print("JWT ERROR:", e)
        raise credentials_exception
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        print("User not found in DB")
        raise credentials_exception
    return user

def cleanup_expired_tokens(db: Session):
    """Membersihkan token yang sudah expired dari blacklist"""
    now = datetime.utcnow()
    db.query(BlacklistedToken).filter(BlacklistedToken.expires_at < now).delete()
    db.commit()

# Pydantic schemas
class RegisterRequest(BaseModel):
    full_name: str
    email: EmailStr
    password: constr(min_length=6)
    confirm_password: constr(min_length=6)

class RegisterResponseData(BaseModel):
    user_id: int
    email: EmailStr
    full_name: str

class RegisterResponse(BaseModel):
    success: bool
    message: str
    data: Optional[RegisterResponseData]

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UserData(BaseModel):
    id: int
    email: EmailStr
    full_name: str
    profile_picture: Optional[str] = None

class LoginResponseData(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: UserData

class LoginResponse(BaseModel):
    success: bool
    message: str
    data: Optional[LoginResponseData]

class RefreshResponse(BaseModel):
    access_token: str
    expires_in: int

class LogoutResponse(BaseModel):
    success: bool
    message: str

@router.post("/register", response_model=RegisterResponse)
def register(req: RegisterRequest, db: Session = Depends(get_db)):
    if req.password != req.confirm_password:
        return RegisterResponse(success=False, message="Password tidak cocok", data=None)
    user = db.query(User).filter(User.email == req.email).first()
    if user:
        return RegisterResponse(success=False, message="Email sudah terdaftar", data=None)
    hashed_password = get_password_hash(req.password)
    new_user = User(full_name=req.full_name, email=req.email, hashed_password=hashed_password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return RegisterResponse(
        success=True,
        message="Registrasi berhasil",
        data=RegisterResponseData(user_id=new_user.id, email=new_user.email, full_name=new_user.full_name)
    )

@router.post("/login", response_model=LoginResponse)
def login(req: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.hashed_password):
        return LoginResponse(success=False, message="Email atau password salah", data=None)
    token, expires_in = create_access_token({"sub": str(user.id)})
    return LoginResponse(
        success=True,
        message="Login berhasil",
        data=LoginResponseData(
            access_token=token,
            token_type="bearer",
            expires_in=expires_in,
            user=UserData(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                profile_picture=user.profile_picture
            )
        )
    )

@router.post("/refresh", response_model=RefreshResponse, dependencies=[Depends(security)])
def refresh(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Token tidak valid")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token tidak valid")
    user = db.query(User).filter(User.id == int(user_id)).first()
    if not user:
        raise HTTPException(status_code=401, detail="User tidak ditemukan")
    new_token, expires_in = create_access_token({"sub": str(user.id)})
    return RefreshResponse(access_token=new_token, expires_in=expires_in)

@router.post("/logout", response_model=LogoutResponse, dependencies=[Depends(security)])
def logout(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    token = credentials.credentials
    try:
        # Decode token untuk mendapatkan waktu expired
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        expires_at = datetime.fromtimestamp(payload.get("exp"))
        
        # Tambahkan token ke blacklist
        blacklisted_token = BlacklistedToken(
            token=token,
            expires_at=expires_at
        )
        db.add(blacklisted_token)
        db.commit()
        
        # Bersihkan token yang sudah expired
        cleanup_expired_tokens(db)
        
        return LogoutResponse(success=True, message="Logout berhasil")
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token tidak valid"
        ) 