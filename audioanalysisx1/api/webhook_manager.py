"""
Webhook Manager
===============

Manages webhook notifications for events.
"""

import asyncio
import hashlib
import hmac
import uuid
from typing import Dict, Optional, Any
from datetime import datetime
import logging

import httpx

from .models import WebhookConfig, WebhookEvent

logger = logging.getLogger(__name__)


class WebhookManager:
    """Manager for webhook notifications."""

    def __init__(self):
        """Initialize webhook manager."""
        self.webhooks: Dict[str, WebhookConfig] = {}
        self.client = httpx.AsyncClient(timeout=30.0)

    async def register_webhook(self, webhook: WebhookConfig) -> str:
        """
        Register a webhook.

        Args:
            webhook: WebhookConfig object

        Returns:
            Webhook ID
        """
        webhook_id = str(uuid.uuid4())
        self.webhooks[webhook_id] = webhook
        logger.info(f"Registered webhook {webhook_id} for events: {webhook.events}")
        return webhook_id

    async def send_webhook(
        self,
        url: str,
        event: str,
        job_id: str,
        data: Dict[str, Any],
        secret: Optional[str] = None
    ):
        """
        Send webhook notification.

        Args:
            url: Webhook URL
            event: Event name
            job_id: Associated job ID
            data: Event data
            secret: Optional secret for signature
        """
        try:
            # Create webhook event
            webhook_event = WebhookEvent(
                event=event,
                job_id=job_id,
                timestamp=datetime.utcnow(),
                data=data
            )

            # Prepare payload
            payload = webhook_event.model_dump()

            # Add signature if secret provided
            if secret:
                signature = self._generate_signature(payload, secret)
                payload['signature'] = signature

            # Send webhook
            logger.info(f"Sending webhook to {url} for event {event}")
            response = await self.client.post(
                url,
                json=payload,
                headers={'Content-Type': 'application/json'}
            )

            if response.status_code == 200:
                logger.info(f"Webhook delivered successfully to {url}")
            else:
                logger.warning(
                    f"Webhook delivery failed: {response.status_code} - {response.text}"
                )

        except Exception as e:
            logger.error(f"Failed to send webhook to {url}: {str(e)}")

    async def trigger_webhooks(
        self,
        event: str,
        job_id: str,
        data: Dict[str, Any]
    ):
        """
        Trigger all webhooks registered for an event.

        Args:
            event: Event name
            job_id: Associated job ID
            data: Event data
        """
        tasks = []

        for webhook_id, webhook in self.webhooks.items():
            if event in webhook.events:
                task = self.send_webhook(
                    url=str(webhook.url),
                    event=event,
                    job_id=job_id,
                    data=data,
                    secret=webhook.secret
                )
                tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def _generate_signature(self, payload: Dict, secret: str) -> str:
        """
        Generate HMAC signature for webhook payload.

        Args:
            payload: Webhook payload
            secret: Secret key

        Returns:
            Hex signature
        """
        import json
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            secret.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        return signature

    def verify_signature(self, payload: Dict, signature: str, secret: str) -> bool:
        """
        Verify webhook signature.

        Args:
            payload: Webhook payload
            signature: Provided signature
            secret: Secret key

        Returns:
            True if valid
        """
        expected_signature = self._generate_signature(payload, secret)
        return hmac.compare_digest(signature, expected_signature)

    async def close(self):
        """Close HTTP client."""
        await self.client.aclose()
