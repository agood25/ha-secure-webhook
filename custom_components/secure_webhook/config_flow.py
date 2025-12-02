"""Config flow for Secure Webhook integration."""
import logging
import hashlib
import secrets
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.util import slugify
from .const import DOMAIN, CONF_WEBHOOK_ID, CONF_AUTH_TOKEN

_LOGGER = logging.getLogger(__name__)

class SecureWebhookConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Secure Webhook."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> config_entries.ConfigFlowResult:
        """Handle the initial step.

        Processes the user input, sanitizes the webhook ID, checks for duplicates,
        hashes the token, and creates the config entry if validation passes.

        Args:
            user_input (dict, optional): The input data from the user. Defaults to None.

        Returns:
            config_entries.ConfigFlowResult: The result of the config flow step.
        """
        errors = {}
        
        # Generate a standard secure token (43 chars approx)
        generated_token = secrets.token_urlsafe(32)

        if user_input is not None:
            # 1. SANITIZE WEBHOOK ID
            webhook_id = slugify(user_input[CONF_WEBHOOK_ID])

            if not webhook_id:
                errors["base"] = "invalid_slug"
            else:
                # 2. CHECK FOR DUPLICATES
                current_entries = self._async_current_entries()
                for entry in current_entries:
                    if entry.data[CONF_WEBHOOK_ID] == webhook_id:
                        return self.async_abort(reason="webhook_id_exists")
                
                # 3. HASH TOKEN
                raw_token = user_input[CONF_AUTH_TOKEN]
                hashed_token = hashlib.sha256(raw_token.encode('utf-8')).hexdigest()
                
                user_input[CONF_WEBHOOK_ID] = webhook_id
                user_input[CONF_AUTH_TOKEN] = hashed_token

                return self.async_create_entry(
                    title=f"Webhook: {webhook_id}",
                    data=user_input
                )

        data_schema = vol.Schema({
            vol.Required(CONF_WEBHOOK_ID, default="my_secure_endpoint"): str,
            vol.Required(CONF_AUTH_TOKEN, default=generated_token): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors
        )
