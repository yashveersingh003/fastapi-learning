from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.dependencies import (
    get_db,
    get_current_user,
    get_current_admin
)
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    verify_token
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


class RegisterRequest(BaseModel):
    username: str
    password: str


@router.post("/register")
def register(
    data: RegisterRequest,
    db: Session = Depends(get_db)
):
    existing_user = db.query(User).filter(
        User.username == data.username
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Username already exists"
        )

    user = User(
        username=data.username,
        password_hash=hash_password(data.password)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "message": "User registered successfully"
    }


@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = db.query(User).filter(
        User.username == form_data.username
    ).first()

    if not user or not verify_password(
        form_data.password,
        user.password_hash
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid username or password"
        )

    access_token = create_access_token({
        "sub": str(user.id),
        "username": user.username
    })

    refresh_token = create_refresh_token({
        "sub": str(user.id),
        "username": user.username
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)
):
    return {
        "user_id": current_user.id,
        "username": current_user.username
    }

@router.get("/profile")
def profile(
    current_user: User = Depends(get_current_user)
):
    return {
        "message": "This is a protected route",
        "username": current_user.username
    }

@router.get("/admin")
def admin_test(
    current_admin: User = Depends(get_current_admin)
):
    return {
        "message": "Welcome Admin!",
        "username": current_admin.username,
        "role": current_admin.role
    }

class RefreshRequest(BaseModel):
    refresh_token: str



@router.post("/refresh")
def refresh_token(data: RefreshRequest):
    payload = verify_token(
        data.refresh_token,
        expected_type="refresh"
    )

    if payload is None:
        raise HTTPException(
            status_code=401,
            detail="Refresh token required"
    )

    new_access_token = create_access_token({
        "sub": payload["sub"],
        "username": payload["username"]
    })

    return {
        "access_token": new_access_token,
        "token_type": "bearer"
    }
