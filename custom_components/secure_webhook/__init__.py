"""The Secure Webhook integration."""
from aiohttp import web
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.components import webhook

from .const import DOMAIN, CONF_WEBHOOK_ID, CONF_AUTH_TOKEN
from .webhook_handler import handle_webhook

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Secure Webhook from a config entry.

    Registers the webhook with the specified ID and handler.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The config entry containing webhook ID and auth token.

    Returns:
        bool: True if setup was successful.
    """
    
    webhook_id = entry.data[CONF_WEBHOOK_ID]
    stored_token_hash = entry.data[CONF_AUTH_TOKEN]

    async def _handle_webhook(hass, webhook_id, request) -> web.Response:
        """Handle the webhook request by delegating to the handler with stored token.

        Args:
            hass (HomeAssistant): The Home Assistant instance.
            webhook_id (str): The ID of the webhook.
            request (aiohttp.web.Request): The incoming request object.

        Returns:
            web.Response: The response from the handler.
        """
        return await handle_webhook(hass, webhook_id, request, stored_token_hash)

    # Register the webhook
    webhook.async_register(
        hass,
        DOMAIN,
        "Secure Webhook",
        webhook_id,
        _handle_webhook,
        allowed_methods=["POST", "PUT"]
    )

    entry.async_on_unload(
        lambda: webhook.async_unregister(hass, webhook_id)
    )

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry.

    Unregisters the webhook.

    Args:
        hass (HomeAssistant): The Home Assistant instance.
        entry (ConfigEntry): The config entry to unload.

    Returns:
        bool: True if unload was successful.
    """
    webhook_id = entry.data[CONF_WEBHOOK_ID]
    webhook.async_unregister(hass, webhook_id)
    return True
