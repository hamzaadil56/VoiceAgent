"""Dependencies for v1 API."""

from __future__ import annotations

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.orm import Session

from .database import get_db
from .models import AdminUser, Membership
from .security import decode_token

bearer_scheme = HTTPBearer(auto_error=True)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> AdminUser:
    token = credentials.credentials
    claims = decode_token(token)
    if claims.get("type") != "access" or not claims.get("sub"):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid access token")

    user = db.get(AdminUser, claims["sub"])
    if not user or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found or inactive")
    return user


def require_org_membership(org_id: str, admin: AdminUser, db: Session) -> Membership:
    membership = db.execute(
        select(Membership).where(
            Membership.org_id == org_id,
            Membership.admin_user_id == admin.id,
        )
    ).scalar_one_or_none()
    if not membership:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No membership in this organization")
    return membership


def extract_public_session_token(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing session token")
    return authorization.split(" ", 1)[1].strip()
