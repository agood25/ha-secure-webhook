import logging
import hashlib
import secrets
from aiohttp import web
from homeassistant.core import HomeAssistant

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

async def handle_webhook(hass: HomeAssistant, webhook_id: str, request, stored_token_hash: str) -> web.Response:
    """Handle incoming webhook POST requests.

    Validates the authorization header and token, then fires an event with the webhook data.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        webhook_id (str): The ID of the webhook.
        request (aiohttp.web.Request): The incoming request object.
        stored_token_hash (str): The stored hash of the valid authentication token.

    Returns:
        web.Response: The HTTP response indicating success (200) or failure (401/500).
    """
    try:
        # 1. READ HEADERS
        # We strictly expect "Authorization: Bearer <token>"
        auth_header = request.headers.get("Authorization")
        
        if not auth_header:
             _LOGGER.warning("Webhook %s failed: Missing Authorization header", webhook_id)
             return web.Response(text="Unauthorized", status=401)

        if not auth_header.startswith("Bearer "):
             _LOGGER.warning("Webhook %s failed: Invalid Authorization header format (Missing 'Bearer')", webhook_id)
             return web.Response(text="Unauthorized", status=401)
        
        # Extract token (remove "Bearer " prefix)
        provided_token = auth_header[7:]
        
        # 2. HASH & VERIFY
        # Hash the incoming token to compare with the stored hash
        provided_token_hash = hashlib.sha256(provided_token.encode('utf-8')).hexdigest()

        if not secrets.compare_digest(provided_token_hash, stored_token_hash):
            _LOGGER.warning("Webhook %s failed: Invalid token", webhook_id)
            return web.Response(text="Unauthorized", status=401)

        # 3. READ DATA
        try:
            data = await request.json()
        except ValueError:
            data = {} 

        _LOGGER.debug("Secure Webhook triggered: %s", data)

        # 4. FIRE EVENT
        hass.bus.async_fire(
            f"{DOMAIN}_event",
            {
                "webhook_id": webhook_id,
                "data": data,
            }
        )

        return web.Response(text="OK", status=200)

    except Exception as err:
        _LOGGER.error("Error processing webhook %s: %s", webhook_id, err)
        return web.Response(status=500)
