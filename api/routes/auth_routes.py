"""Authentication routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from api.auth import create_access_token, get_current_user, verify_password
from api.database import get_db
from api.db_models import User
from api.schemas import LoginRequest, MeResponse, TokenResponse

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    """Authenticate user and return JWT token."""
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    token = create_access_token({"sub": user.id, "role": user.role})
    return TokenResponse(access_token=token)


@router.get("/me", response_model=MeResponse)
def me(user: User = Depends(get_current_user)) -> MeResponse:
    """Return current authenticated user info."""
    return MeResponse.model_validate(user)
