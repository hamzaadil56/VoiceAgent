"""SSO (SAML/OIDC) service for enterprise authentication.

Requires `authlib` for OIDC or `python3-saml` for SAML.
Configure per-org SSO settings in the Organization model.
"""

from __future__ import annotations

import logging
import os
from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import AdminUser, Membership, Organization
from ..security import create_access_token, hash_password

logger = logging.getLogger(__name__)


OIDC_PROVIDERS: dict[str, dict[str, str]] = {
    "google": {
        "issuer": "https://accounts.google.com",
        "authorization_endpoint": "https://accounts.google.com/o/oauth2/v2/auth",
        "token_endpoint": "https://oauth2.googleapis.com/token",
        "userinfo_endpoint": "https://openidconnect.googleapis.com/v1/userinfo",
    },
    "github": {
        "authorization_endpoint": "https://github.com/login/oauth/authorize",
        "token_endpoint": "https://github.com/login/oauth/access_token",
        "userinfo_endpoint": "https://api.github.com/user",
    },
}

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_OAUTH_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_OAUTH_CLIENT_SECRET", "")
GITHUB_CLIENT_ID = os.getenv("GITHUB_OAUTH_CLIENT_ID", "")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_OAUTH_CLIENT_SECRET", "")


async def get_oauth_redirect_url(provider: str, redirect_uri: str) -> str:
    """Generate OAuth authorization URL for a provider."""
    if provider == "google" and GOOGLE_CLIENT_ID:
        params = {
            "client_id": GOOGLE_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "response_type": "code",
            "scope": "openid email profile",
            "access_type": "offline",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{OIDC_PROVIDERS['google']['authorization_endpoint']}?{query}"

    if provider == "github" and GITHUB_CLIENT_ID:
        params = {
            "client_id": GITHUB_CLIENT_ID,
            "redirect_uri": redirect_uri,
            "scope": "user:email",
        }
        query = "&".join(f"{k}={v}" for k, v in params.items())
        return f"{OIDC_PROVIDERS['github']['authorization_endpoint']}?{query}"

    raise ValueError(f"OAuth provider {provider} is not configured")


async def handle_oauth_callback(
    provider: str,
    code: str,
    redirect_uri: str,
    db: Session,
) -> dict[str, Any]:
    """Exchange OAuth code for tokens, create/find user, return access token."""
    try:
        import httpx
    except ImportError:
        raise RuntimeError("httpx required for OAuth")

    user_info = {}

    if provider == "google":
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                OIDC_PROVIDERS["google"]["token_endpoint"],
                data={
                    "code": code,
                    "client_id": GOOGLE_CLIENT_ID,
                    "client_secret": GOOGLE_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            tokens = token_resp.json()
            access_token = tokens.get("access_token")
            if not access_token:
                raise ValueError("Failed to get access token from Google")

            info_resp = await client.get(
                OIDC_PROVIDERS["google"]["userinfo_endpoint"],
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_info = info_resp.json()
            user_info["provider_id"] = user_info.get("sub", "")

    elif provider == "github":
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                OIDC_PROVIDERS["github"]["token_endpoint"],
                data={
                    "code": code,
                    "client_id": GITHUB_CLIENT_ID,
                    "client_secret": GITHUB_CLIENT_SECRET,
                    "redirect_uri": redirect_uri,
                },
                headers={"Accept": "application/json"},
            )
            tokens = token_resp.json()
            access_token = tokens.get("access_token")
            if not access_token:
                raise ValueError("Failed to get access token from GitHub")

            info_resp = await client.get(
                OIDC_PROVIDERS["github"]["userinfo_endpoint"],
                headers={"Authorization": f"Bearer {access_token}"},
            )
            gh = info_resp.json()
            user_info = {
                "email": gh.get("email"),
                "name": gh.get("name") or gh.get("login"),
                "provider_id": str(gh.get("id", "")),
            }

            if not user_info["email"]:
                emails_resp = await client.get(
                    "https://api.github.com/user/emails",
                    headers={"Authorization": f"Bearer {access_token}"},
                )
                for e in emails_resp.json():
                    if e.get("primary"):
                        user_info["email"] = e["email"]
                        break
    else:
        raise ValueError(f"Unsupported OAuth provider: {provider}")

    email = user_info.get("email")
    if not email:
        raise ValueError("No email returned from OAuth provider")

    user = db.execute(
        select(AdminUser).where(AdminUser.email == email)
    ).scalar_one_or_none()

    if not user:
        import uuid
        user = AdminUser(
            email=email,
            password_hash=hash_password(uuid.uuid4().hex),
            full_name=user_info.get("name", email.split("@")[0]),
            is_active=True,
            email_verified=True,
            oauth_provider=provider,
            oauth_provider_id=str(user_info.get("provider_id", "")),
        )
        db.add(user)
        db.flush()

        org = Organization(
            name=f"{user.full_name}'s Workspace",
            slug=email.split("@")[0].lower().replace(".", "-")[:50],
        )
        db.add(org)
        db.flush()

        membership = Membership(
            org_id=org.id, admin_user_id=user.id, role="org_admin"
        )
        db.add(membership)
        db.commit()
    else:
        if not user.oauth_provider:
            user.oauth_provider = provider
            user.oauth_provider_id = str(user_info.get("provider_id", ""))
            user.email_verified = True
            db.commit()

    token = create_access_token(user.id)
    return {"access_token": token, "token_type": "bearer", "user_id": user.id}
