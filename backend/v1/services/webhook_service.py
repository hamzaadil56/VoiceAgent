"""Webhook delivery service for form events."""

from __future__ import annotations

import asyncio
import hashlib
import hmac
import json
import logging
from datetime import datetime

import httpx
from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import FormWebhook, WebhookDelivery

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
TIMEOUT_SECONDS = 10


def _sign_payload(payload: str, secret: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


async def deliver_webhook(
    db: Session,
    form_id: str,
    event: str,
    payload: dict,
) -> None:
    """Fire webhooks for a form event asynchronously."""
    hooks = db.execute(
        select(FormWebhook).where(
            FormWebhook.form_id == form_id,
            FormWebhook.is_active == True,
        )
    ).scalars().all()

    for hook in hooks:
        if event not in hook.events:
            continue

        delivery = WebhookDelivery(
            webhook_id=hook.id,
            event=event,
            payload_json=payload,
            status="pending",
        )
        db.add(delivery)
        db.flush()

        asyncio.create_task(
            _send_webhook(hook.url, hook.secret, event, payload, delivery.id, db)
        )

    db.commit()


async def _send_webhook(
    url: str,
    secret: str,
    event: str,
    payload: dict,
    delivery_id: str,
    db: Session,
) -> None:
    payload_str = json.dumps(payload, default=str)
    signature = _sign_payload(payload_str, secret)

    headers = {
        "Content-Type": "application/json",
        "X-TalkForms-Event": event,
        "X-TalkForms-Signature": f"sha256={signature}",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
                response = await client.post(url, content=payload_str, headers=headers)

            delivery = db.get(WebhookDelivery, delivery_id)
            if delivery:
                delivery.status_code = response.status_code
                delivery.response_body = response.text[:1000]
                delivery.attempts = attempt
                delivery.status = "delivered" if response.is_success else "failed"
                db.commit()

            if response.is_success:
                logger.info("Webhook delivered: %s -> %s (%d)", event, url, response.status_code)
                return

        except Exception as exc:
            logger.warning(
                "Webhook delivery attempt %d/%d failed for %s: %s",
                attempt, MAX_RETRIES, url, exc,
            )
            if attempt < MAX_RETRIES:
                await asyncio.sleep(2 ** attempt)

    delivery = db.get(WebhookDelivery, delivery_id)
    if delivery:
        delivery.status = "failed"
        delivery.attempts = MAX_RETRIES
        db.commit()
    logger.error("Webhook delivery exhausted retries: %s -> %s", event, url)
