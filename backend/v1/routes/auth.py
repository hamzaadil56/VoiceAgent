"""Auth routes for admin users."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin
from ..models import AdminUser, Membership
from ..schemas import LoginRequest, MeResponse, TokenRefreshResponse, TokenResponse
from ..security import create_access_token, verify_password

router = APIRouter(prefix="/auth", tags=["v1-auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.execute(select(AdminUser).where(AdminUser.email == payload.email)).scalar_one_or_none()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive")

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(
    current_user: AdminUser = Depends(get_current_admin),
):
    """Refresh the access token for an authenticated admin user."""
    new_token = create_access_token(current_user.id)
    return TokenRefreshResponse(access_token=new_token)


@router.get("/me", response_model=MeResponse)
def me(current_user: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    memberships = db.execute(
        select(Membership).where(Membership.admin_user_id == current_user.id)
    ).scalars().all()
    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        memberships=[{"org_id": m.org_id, "role": m.role} for m in memberships],
    )
