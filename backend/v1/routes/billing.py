"""Billing routes for Stripe integration."""

from __future__ import annotations

import logging
import os
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..database import get_db
from ..deps import get_current_admin, require_org_membership
from ..models import AdminUser, Organization, Subscription

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/billing", tags=["v1-billing"])

STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "")

PLAN_STRIPE_PRICES = {
    "pro": os.getenv("STRIPE_PRO_PRICE_ID", ""),
    "business": os.getenv("STRIPE_BUSINESS_PRICE_ID", ""),
}

PLAN_LIMITS = {
    "free": {"responses": 50, "forms": 3, "voice_minutes": 0, "seats": 1},
    "pro": {"responses": 1000, "forms": 999999, "voice_minutes": 100, "seats": 3},
    "business": {"responses": 5000, "forms": 999999, "voice_minutes": 500, "seats": 10},
    "enterprise": {"responses": 999999, "forms": 999999, "voice_minutes": 999999, "seats": 999999},
}


@router.post("/orgs/{org_id}/checkout")
async def create_checkout_session(
    org_id: str,
    plan: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    """Create a Stripe Checkout session for upgrading."""
    require_org_membership(org_id, current_user, db)

    if plan not in PLAN_STRIPE_PRICES:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {plan}")

    price_id = PLAN_STRIPE_PRICES[plan]
    if not price_id or not STRIPE_SECRET_KEY:
        raise HTTPException(
            status_code=503,
            detail="Stripe is not configured. Set STRIPE_SECRET_KEY and price IDs.",
        )

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        org = db.get(Organization, org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")

        if not org.stripe_customer_id:
            customer = stripe.Customer.create(
                email=current_user.email,
                name=org.name,
                metadata={"org_id": org_id},
            )
            org.stripe_customer_id = customer.id
            db.commit()

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        session = stripe.checkout.Session.create(
            customer=org.stripe_customer_id,
            mode="subscription",
            line_items=[{"price": price_id, "quantity": 1}],
            success_url=f"{frontend_url}/admin/settings/billing?success=true",
            cancel_url=f"{frontend_url}/admin/settings/billing?canceled=true",
            metadata={"org_id": org_id, "plan": plan},
        )

        return {"checkout_url": session.url}

    except ImportError:
        raise HTTPException(status_code=503, detail="stripe package not installed")
    except Exception as exc:
        logger.exception("Stripe checkout failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create checkout session")


@router.post("/stripe-webhook")
async def stripe_webhook(request: Request, db: Session = Depends(get_db)):
    """Handle Stripe webhook events."""
    if not STRIPE_SECRET_KEY or not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        payload = await request.body()
        sig_header = request.headers.get("stripe-signature", "")

        event = stripe.Webhook.construct_event(
            payload, sig_header, STRIPE_WEBHOOK_SECRET
        )
    except ImportError:
        raise HTTPException(status_code=503, detail="stripe package not installed")
    except Exception as exc:
        logger.warning("Stripe webhook verification failed: %s", exc)
        raise HTTPException(status_code=400, detail="Invalid webhook signature")

    event_type = event["type"]
    data = event["data"]["object"]

    if event_type == "checkout.session.completed":
        org_id = data.get("metadata", {}).get("org_id")
        plan = data.get("metadata", {}).get("plan", "pro")
        subscription_id = data.get("subscription")

        if org_id:
            org = db.get(Organization, org_id)
            if org:
                limits = PLAN_LIMITS.get(plan, PLAN_LIMITS["pro"])
                org.plan = plan
                org.plan_responses_limit = limits["responses"]
                org.plan_forms_limit = limits["forms"]
                org.plan_voice_minutes_limit = limits["voice_minutes"]
                org.plan_seats_limit = limits["seats"]

                sub = db.execute(
                    select(Subscription).where(Subscription.org_id == org_id)
                ).scalar_one_or_none()
                if not sub:
                    sub = Subscription(org_id=org_id)
                    db.add(sub)

                sub.stripe_subscription_id = subscription_id
                sub.plan = plan
                sub.status = "active"
                db.commit()
                logger.info("Org %s upgraded to %s", org_id, plan)

    elif event_type == "customer.subscription.deleted":
        subscription_id = data.get("id")
        sub = db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription_id
            )
        ).scalar_one_or_none()
        if sub:
            org = db.get(Organization, sub.org_id)
            if org:
                org.plan = "free"
                limits = PLAN_LIMITS["free"]
                org.plan_responses_limit = limits["responses"]
                org.plan_forms_limit = limits["forms"]
                org.plan_voice_minutes_limit = limits["voice_minutes"]
                org.plan_seats_limit = limits["seats"]
            sub.status = "canceled"
            db.commit()
            logger.info("Subscription %s canceled", subscription_id)

    elif event_type in (
        "customer.subscription.updated",
        "invoice.payment_succeeded",
        "invoice.payment_failed",
    ):
        logger.info("Received Stripe event: %s", event_type)

    return {"status": "ok"}


@router.post("/orgs/{org_id}/portal")
async def create_portal_session(
    org_id: str,
    db: Session = Depends(get_db),
    current_user: AdminUser = Depends(get_current_admin),
):
    """Create a Stripe Customer Portal session for managing subscriptions."""
    require_org_membership(org_id, current_user, db)

    org = db.get(Organization, org_id)
    if not org or not org.stripe_customer_id:
        raise HTTPException(status_code=400, detail="No Stripe customer found")

    if not STRIPE_SECRET_KEY:
        raise HTTPException(status_code=503, detail="Stripe not configured")

    try:
        import stripe
        stripe.api_key = STRIPE_SECRET_KEY

        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
        session = stripe.billing_portal.Session.create(
            customer=org.stripe_customer_id,
            return_url=f"{frontend_url}/admin/settings/billing",
        )
        return {"portal_url": session.url}
    except ImportError:
        raise HTTPException(status_code=503, detail="stripe package not installed")
    except Exception as exc:
        logger.exception("Stripe portal failed: %s", exc)
        raise HTTPException(status_code=500, detail="Failed to create portal session")
