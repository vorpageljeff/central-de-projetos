import json
import logging
from urllib import request

logger = logging.getLogger(__name__)


def notify_lead(webhook_url: str | None, payload: dict[str, str]) -> None:
    if not webhook_url:
        logger.info("Lead notification skipped: NOTIFICATION_WEBHOOK_URL is not configured.")
        return

    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    webhook_request = request.Request(
        webhook_url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with request.urlopen(webhook_request, timeout=8) as response:
            logger.info("Lead notification sent with status %s.", response.status)
    except Exception:
        logger.exception("Lead notification failed.")
