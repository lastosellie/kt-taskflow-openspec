from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models import User
from app.auth import hash_password, verify_password, validate_password, create_token
from app.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: int
    email: str

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    token: str
    user: UserOut


@router.post("/signup", status_code=201, response_model=TokenResponse)
def signup(body: SignupRequest, db: Session = Depends(get_db)):
    if not validate_password(body.password):
        raise HTTPException(
            status_code=422,
            detail={"code": "INVALID_PASSWORD", "message": "비밀번호는 8자 이상, 대문자·소문자·특수문자를 포함해야 합니다"},
        )
    user = User(email=body.email, password_hash=hash_password(body.password))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail={"code": "EMAIL_EXISTS", "message": "이미 사용 중인 이메일입니다"},
        )
    db.refresh(user)
    return {"token": create_token(user.id), "user": user}


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail={"code": "INVALID_CREDENTIALS", "message": "이메일 또는 비밀번호가 올바르지 않습니다"},
        )
    return {"token": create_token(user.id), "user": user}


@router.get("/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "team_id": current_user.team_id,
        "created_at": current_user.created_at,
    }


@router.post("/logout")
def logout():
    return {"message": "로그아웃되었습니다"}
