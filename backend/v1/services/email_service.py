"""Email notification service.

Uses Resend for transactional emails when RESEND_API_KEY is configured,
otherwise logs the email content for development.
"""

from __future__ import annotations

import logging
import os

logger = logging.getLogger(__name__)

RESEND_API_KEY = os.getenv("RESEND_API_KEY", "")
FROM_EMAIL = os.getenv("EMAIL_FROM", "TalkForms <noreply@talkforms.io>")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")


async def send_email(to: str, subject: str, html: str) -> bool:
    if RESEND_API_KEY:
        try:
            import resend
            resend.api_key = RESEND_API_KEY
            resend.Emails.send({
                "from": FROM_EMAIL,
                "to": [to],
                "subject": subject,
                "html": html,
            })
            logger.info("Email sent to %s: %s", to, subject)
            return True
        except ImportError:
            logger.warning("resend package not installed, logging email instead")
        except Exception as exc:
            logger.exception("Failed to send email to %s: %s", to, exc)
            return False

    logger.info("EMAIL [to=%s subject=%s]\n%s", to, subject, html)
    return True


async def send_welcome_email(email: str, full_name: str) -> bool:
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 560px; margin: 0 auto; padding: 32px;">
        <h1 style="color: #2d6a5a; font-size: 24px;">Welcome to TalkForms!</h1>
        <p style="color: #444; font-size: 15px; line-height: 1.6;">
            Hi {full_name},<br><br>
            Your account is ready. Start creating conversational forms that your
            respondents will actually enjoy filling out.
        </p>
        <a href="{FRONTEND_URL}/admin"
           style="display: inline-block; background: #2d6a5a; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 16px;">
            Go to Dashboard
        </a>
        <p style="color: #999; font-size: 12px; margin-top: 32px;">
            TalkForms — Conversational forms powered by AI
        </p>
    </div>
    """
    return await send_email(email, "Welcome to TalkForms!", html)


async def send_password_reset_email(email: str, reset_token: str) -> bool:
    reset_url = f"{FRONTEND_URL}/admin/reset-password?token={reset_token}"
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 560px; margin: 0 auto; padding: 32px;">
        <h1 style="color: #2d6a5a; font-size: 24px;">Reset Your Password</h1>
        <p style="color: #444; font-size: 15px; line-height: 1.6;">
            You requested a password reset. Click the button below to set a new password.
            This link expires in 1 hour.
        </p>
        <a href="{reset_url}"
           style="display: inline-block; background: #2d6a5a; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 16px;">
            Reset Password
        </a>
        <p style="color: #999; font-size: 12px; margin-top: 32px;">
            If you didn't request this, you can safely ignore this email.
        </p>
    </div>
    """
    return await send_email(email, "Reset Your TalkForms Password", html)


async def send_team_invite_email(
    email: str, org_name: str, inviter_name: str, invite_token: str
) -> bool:
    invite_url = f"{FRONTEND_URL}/admin/accept-invite?token={invite_token}"
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 560px; margin: 0 auto; padding: 32px;">
        <h1 style="color: #2d6a5a; font-size: 24px;">You're Invited!</h1>
        <p style="color: #444; font-size: 15px; line-height: 1.6;">
            {inviter_name} has invited you to join <strong>{org_name}</strong> on TalkForms.
        </p>
        <a href="{invite_url}"
           style="display: inline-block; background: #2d6a5a; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 16px;">
            Accept Invitation
        </a>
    </div>
    """
    return await send_email(email, f"Join {org_name} on TalkForms", html)


async def send_submission_notification(
    email: str, form_title: str, submission_count: int
) -> bool:
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 560px; margin: 0 auto; padding: 32px;">
        <h1 style="color: #2d6a5a; font-size: 24px;">New Response</h1>
        <p style="color: #444; font-size: 15px; line-height: 1.6;">
            Your form <strong>{form_title}</strong> received a new response!
            Total responses: {submission_count}
        </p>
        <a href="{FRONTEND_URL}/admin"
           style="display: inline-block; background: #2d6a5a; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none; font-weight: 600; margin-top: 16px;">
            View Submissions
        </a>
    </div>
    """
    return await send_email(email, f"New response on {form_title}", html)


async def send_respondent_confirmation(
    email: str, form_title: str, answers_summary: str
) -> bool:
    html = f"""
    <div style="font-family: Inter, sans-serif; max-width: 560px; margin: 0 auto; padding: 32px;">
        <h1 style="color: #2d6a5a; font-size: 24px;">Response Confirmed</h1>
        <p style="color: #444; font-size: 15px; line-height: 1.6;">
            Thank you for completing <strong>{form_title}</strong>. Here's a summary of your response:
        </p>
        <div style="background: #f7f5f0; border-radius: 8px; padding: 16px; margin-top: 16px; font-size: 14px; color: #444;">
            {answers_summary}
        </div>
        <p style="color: #999; font-size: 12px; margin-top: 32px;">
            Powered by TalkForms
        </p>
    </div>
    """
    return await send_email(email, f"Your response to {form_title}", html)
