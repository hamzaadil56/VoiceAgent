"""Auth routes for admin users."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin
from ..models import AdminUser, Invitation, Membership, Organization, PasswordResetToken
from ..schemas import (
    AcceptInviteRequest,
    ForgotPasswordRequest,
    LoginRequest,
    MeResponse,
    RegisterRequest,
    ResetPasswordRequest,
    TokenRefreshResponse,
    TokenResponse,
)
from ..security import (
    RESET_TOKEN_TTL_HOURS,
    create_access_token,
    generate_reset_token,
    hash_password,
    verify_password,
)

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


@router.post("/register", response_model=TokenResponse)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    existing = db.execute(select(AdminUser).where(AdminUser.email == payload.email)).scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    user = AdminUser(
        email=payload.email,
        password_hash=hash_password(payload.password),
        full_name=payload.full_name,
        is_active=True,
        email_verified=False,
    )
    db.add(user)
    db.flush()

    org_slug = payload.org_name.lower().replace(" ", "-").strip("-")[:50]
    existing_org = db.execute(select(Organization).where(Organization.slug == org_slug)).scalar_one_or_none()
    if existing_org:
        import uuid
        org_slug = f"{org_slug}-{str(uuid.uuid4())[:6]}"

    org = Organization(name=payload.org_name, slug=org_slug)
    db.add(org)
    db.flush()

    membership = Membership(org_id=org.id, admin_user_id=user.id, role="org_admin")
    db.add(membership)
    db.commit()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Generate a password reset token. In production, sends an email."""
    user = db.execute(select(AdminUser).where(AdminUser.email == payload.email)).scalar_one_or_none()
    if not user:
        return {"message": "If the email exists, a reset link has been sent."}

    raw_token = generate_reset_token()
    reset = PasswordResetToken(
        admin_user_id=user.id,
        token=raw_token,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=RESET_TOKEN_TTL_HOURS),
    )
    db.add(reset)
    db.commit()

    # TODO: Send email with reset link containing raw_token
    return {"message": "If the email exists, a reset link has been sent.", "reset_token": raw_token}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    reset = db.execute(
        select(PasswordResetToken).where(
            PasswordResetToken.token == payload.token,
            PasswordResetToken.used == False,
        )
    ).scalar_one_or_none()

    if not reset:
        raise HTTPException(status_code=400, detail="Invalid or expired reset token")

    if reset.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="Reset token has expired")

    user = db.get(AdminUser, reset.admin_user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.password_hash = hash_password(payload.new_password)
    reset.used = True
    db.commit()

    return {"message": "Password reset successfully"}


@router.post("/accept-invite", response_model=TokenResponse)
def accept_invite(payload: AcceptInviteRequest, db: Session = Depends(get_db)):
    invitation = db.execute(
        select(Invitation).where(
            Invitation.token == payload.token,
            Invitation.status == "pending",
        )
    ).scalar_one_or_none()

    if not invitation:
        raise HTTPException(status_code=400, detail="Invalid or expired invitation")

    user = db.execute(select(AdminUser).where(AdminUser.email == invitation.email)).scalar_one_or_none()
    if not user:
        if not payload.password:
            raise HTTPException(status_code=400, detail="Password required for new users")
        user = AdminUser(
            email=invitation.email,
            password_hash=hash_password(payload.password),
            full_name=payload.full_name,
            is_active=True,
            email_verified=True,
        )
        db.add(user)
        db.flush()

    existing_membership = db.execute(
        select(Membership).where(
            Membership.org_id == invitation.org_id,
            Membership.admin_user_id == user.id,
        )
    ).scalar_one_or_none()

    if not existing_membership:
        membership = Membership(
            org_id=invitation.org_id,
            admin_user_id=user.id,
            role=invitation.role,
        )
        db.add(membership)

    invitation.status = "accepted"
    db.commit()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.get("/oauth/{provider}")
async def oauth_redirect(provider: str):
    """Redirect to OAuth provider for login."""
    import os
    from ..services.sso_service import get_oauth_redirect_url

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    redirect_uri = f"{frontend_url}/admin/oauth/callback/{provider}"

    try:
        url = await get_oauth_redirect_url(provider, redirect_uri)
        return {"redirect_url": url}
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/oauth/{provider}/callback", response_model=TokenResponse)
async def oauth_callback(
    provider: str,
    code: str,
    db: Session = Depends(get_db),
):
    """Handle OAuth callback and create/login user."""
    import os
    from ..services.sso_service import handle_oauth_callback

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    redirect_uri = f"{frontend_url}/admin/oauth/callback/{provider}"

    try:
        result = await handle_oauth_callback(provider, code, redirect_uri, db)
        return TokenResponse(access_token=result["access_token"])
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc))


@router.post("/refresh", response_model=TokenRefreshResponse)
def refresh_token(
    current_user: AdminUser = Depends(get_current_admin),
):
    new_token = create_access_token(current_user.id)
    return TokenRefreshResponse(access_token=new_token)


@router.get("/me", response_model=MeResponse)
def me(current_user: AdminUser = Depends(get_current_admin), db: Session = Depends(get_db)):
    memberships = db.execute(
        select(Membership).where(Membership.admin_user_id == current_user.id)
    ).scalars().all()

    plan = "free"
    if memberships:
        org = db.get(Organization, memberships[0].org_id)
        if org:
            plan = org.plan

    return MeResponse(
        id=current_user.id,
        email=current_user.email,
        full_name=current_user.full_name,
        memberships=[{"org_id": m.org_id, "role": m.role} for m in memberships],
        plan=plan,
    )
