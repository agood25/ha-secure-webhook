import pytest
from unittest.mock import MagicMock, patch
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from custom_components.secure_webhook import async_setup_entry, async_unload_entry
from custom_components.secure_webhook.const import DOMAIN, CONF_WEBHOOK_ID, CONF_AUTH_TOKEN

@pytest.fixture
def mock_hass() -> MagicMock:
    """Fixture to mock HomeAssistant instance.
    
    Returns:
        MagicMock: A mock HomeAssistant object.
    """
    return MagicMock(spec=HomeAssistant)

@pytest.fixture
def mock_entry() -> MagicMock:
    """Fixture to mock ConfigEntry.

    Returns:
        MagicMock: A mock ConfigEntry object with predefined data.
    """
    entry = MagicMock(spec=ConfigEntry)
    entry.data = {
        CONF_WEBHOOK_ID: "test_webhook_id",
        CONF_AUTH_TOKEN: "test_token_hash"
    }
    entry.async_on_unload = MagicMock()
    return entry

@pytest.mark.asyncio
@patch("custom_components.secure_webhook.webhook.async_register")
@patch("custom_components.secure_webhook.webhook.async_unregister")
async def test_async_setup_entry(mock_unregister: MagicMock, mock_register: MagicMock, mock_hass: MagicMock, mock_entry: MagicMock) -> None:
    """Test the setup of a config entry.

    Verifies that the webhook is registered with correct parameters
    and unload listener is attached.
    
    Args:
        mock_unregister (MagicMock): Mock for webhook.async_unregister.
        mock_register (MagicMock): Mock for webhook.async_register.
        mock_hass (MagicMock): Mock HomeAssistant instance fixture.
        mock_entry (MagicMock): Mock ConfigEntry fixture.
    """
    result = await async_setup_entry(mock_hass, mock_entry)
    
    assert result is True
    mock_register.assert_called_once()
    args, kwargs = mock_register.call_args
    assert args[0] == mock_hass
    assert args[1] == DOMAIN
    assert args[2] == "Secure Webhook"
    assert args[3] == "test_webhook_id"
    assert kwargs["allowed_methods"] == ["POST", "PUT"]
    
    mock_entry.async_on_unload.assert_called_once()

@pytest.mark.asyncio
@patch("custom_components.secure_webhook.webhook.async_unregister")
async def test_async_unload_entry(mock_unregister: MagicMock, mock_hass: MagicMock, mock_entry: MagicMock) -> None:
    """Test the unloading of a config entry.

    Verifies that the webhook is unregistered using the webhook ID.

    Args:
        mock_unregister (MagicMock): Mock for webhook.async_unregister.
        mock_hass (MagicMock): Mock HomeAssistant instance fixture.
        mock_entry (MagicMock): Mock ConfigEntry fixture.
    """
    result = await async_unload_entry(mock_hass, mock_entry)
    
    assert result is True
    mock_unregister.assert_called_once_with(mock_hass, "test_webhook_id")
