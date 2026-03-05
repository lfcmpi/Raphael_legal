"""User management routes."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from api.auth import get_current_user, hash_password
from api.database import get_db
from api.db_models import User
from api.schemas import (
    UserCreateRequest,
    UserListResponse,
    UserSummary,
    UserUpdateRequest,
)

router = APIRouter(prefix="/api/users", tags=["users"])

VALID_ROLES = {"admin", "manager", "consulta"}
MANAGE_ROLES = {"admin"}


def _require_admin(user: User) -> None:
    if user.role not in MANAGE_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Apenas administradores podem gerenciar usuarios",
        )


@router.get("", response_model=UserListResponse)
def list_users(
    search: str | None = Query(None),
    role: str | None = Query(None),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserListResponse:
    """List users. Admin and manager can list; consulta is forbidden."""
    if user.role not in {"admin", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissao")

    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if search:
        like = f"%{search}%"
        query = query.filter((User.nome.ilike(like)) | (User.email.ilike(like)))

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * per_page).limit(per_page).all()
    return UserListResponse(users=[UserSummary.model_validate(u) for u in users], total=total)


@router.post("", response_model=UserSummary, status_code=status.HTTP_201_CREATED)
def create_user(
    body: UserCreateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserSummary:
    """Create a new user. Admin only."""
    _require_admin(user)

    if body.role not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role invalido. Use: {', '.join(VALID_ROLES)}")

    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ja cadastrado")

    new_user = User(
        email=body.email,
        nome=body.nome,
        hashed_password=hash_password(body.password),
        role=body.role,
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return UserSummary.model_validate(new_user)


@router.get("/{user_id}", response_model=UserSummary)
def get_user(
    user_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserSummary:
    """Get user details. Admin and manager can view."""
    if user.role not in {"admin", "manager"}:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissao")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")
    return UserSummary.model_validate(target)


@router.patch("/{user_id}", response_model=UserSummary)
def update_user(
    user_id: str,
    body: UserUpdateRequest,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> UserSummary:
    """Update user. Admin only."""
    _require_admin(user)

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

    update_data = body.model_dump(exclude_unset=True)

    if "role" in update_data and update_data["role"] not in VALID_ROLES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role invalido. Use: {', '.join(VALID_ROLES)}")

    if "email" in update_data and update_data["email"] != target.email:
        existing = db.query(User).filter(User.email == update_data["email"]).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email ja cadastrado")

    if "password" in update_data:
        pwd = update_data.pop("password")
        if pwd:
            target.hashed_password = hash_password(pwd)

    for field, value in update_data.items():
        setattr(target, field, value)

    db.commit()
    db.refresh(target)
    return UserSummary.model_validate(target)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """Delete a user. Admin only. Cannot delete yourself."""
    _require_admin(user)

    if user_id == user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Nao e possivel excluir a si mesmo")

    target = db.query(User).filter(User.id == user_id).first()
    if not target:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario nao encontrado")

    db.delete(target)
    db.commit()
