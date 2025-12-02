import pytest
from unittest.mock import MagicMock, AsyncMock
import hashlib
from custom_components.secure_webhook.webhook_handler import handle_webhook
from custom_components.secure_webhook.const import DOMAIN

@pytest.fixture
def mock_hass() -> MagicMock:
    """Fixture for a mock HomeAssistant instance.

    Returns:
        MagicMock: A mock HomeAssistant object.
    """
    hass = MagicMock()
    hass.bus.async_fire = MagicMock()
    return hass

@pytest.fixture
def webhook_id() -> str:
    """Fixture for the webhook ID.

    Returns:
        str: The webhook ID.
    """
    return "test_webhook_id"

@pytest.fixture
def token() -> str:
    """Fixture for the authentication token.

    Returns:
        str: The authentication token.
    """
    return "test_token"

@pytest.fixture
def stored_token_hash(token: str) -> str:
    """Fixture for the stored token hash.

    Args:
        token (str): The authentication token fixture.

    Returns:
        str: The SHA256 hash of the token.
    """
    return hashlib.sha256(token.encode('utf-8')).hexdigest()

@pytest.fixture
def mock_request() -> MagicMock:
    """Fixture for a mock aiohttp request.

    Returns:
        MagicMock: A mock request object.
    """
    return MagicMock()

@pytest.mark.asyncio
async def test_missing_auth_header(mock_hass: MagicMock, webhook_id: str, mock_request: MagicMock, stored_token_hash: str) -> None:
    """Test webhook request with missing Authorization header.

    Verifies that a 401 Unauthorized response is returned.

    Args:
        mock_hass (MagicMock): Mock HomeAssistant instance fixture.
        webhook_id (str): Webhook ID fixture.
        mock_request (MagicMock): Mock request fixture.
        stored_token_hash (str): Stored token hash fixture.
    """
    mock_request.headers = {}
    response = await handle_webhook(mock_hass, webhook_id, mock_request, stored_token_hash)
    assert response.status == 401
    assert response.text == "Unauthorized"

@pytest.mark.asyncio
async def test_invalid_auth_header_format(mock_hass: MagicMock, webhook_id: str, mock_request: MagicMock, stored_token_hash: str) -> None:
    """Test webhook request with invalid Authorization header format.

    Verifies that a 401 Unauthorized response is returned when 'Bearer' is missing.

    Args:
        mock_hass (MagicMock): Mock HomeAssistant instance fixture.
        webhook_id (str): Webhook ID fixture.
        mock_request (MagicMock): Mock request fixture.
        stored_token_hash (str): Stored token hash fixture.
    """
    mock_request.headers = {"Authorization": "InvalidFormat"}
    response = await handle_webhook(mock_hass, webhook_id, mock_request, stored_token_hash)
    assert response.status == 401
    assert response.text == "Unauthorized"

@pytest.mark.asyncio
async def test_invalid_token(mock_hass: MagicMock, webhook_id: str, mock_request: MagicMock, stored_token_hash: str) -> None:
    """Test webhook request with invalid token.

    Verifies that a 401 Unauthorized response is returned when the token hash doesn't match.

    Args:
        mock_hass (MagicMock): Mock HomeAssistant instance fixture.
        webhook_id (str): Webhook ID fixture.
        mock_request (MagicMock): Mock request fixture.
        stored_token_hash (str): Stored token hash fixture.
    """
    mock_request.headers = {"Authorization": "Bearer wrong_token"}
    response = await handle_webhook(mock_hass, webhook_id, mock_request, stored_token_hash)
    assert response.status == 401
    assert response.text == "Unauthorized"

@pytest.mark.asyncio
async def test_valid_request(mock_hass: MagicMock, webhook_id: str, mock_request: MagicMock, stored_token_hash: str, token: str) -> None:
    """Test a valid webhook request with JSON data.

    Verifies that a 200 OK response is returned and the event is fired with the correct data.

    Args:
        mock_hass (MagicMock): Mock HomeAssistant instance fixture.
        webhook_id (str): Webhook ID fixture.
        mock_request (MagicMock): Mock request fixture.
        stored_token_hash (str): Stored token hash fixture.
        token (str): Authentication token fixture.
    """
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    mock_request.json = AsyncMock(return_value={"key": "value"})
    
    response = await handle_webhook(mock_hass, webhook_id, mock_request, stored_token_hash)
    
    assert response.status == 200
    assert response.text == "OK"
    mock_hass.bus.async_fire.assert_called_once_with(
        f"{DOMAIN}_event",
        {
            "webhook_id": webhook_id,
            "data": {"key": "value"},
        }
    )

@pytest.mark.asyncio
async def test_valid_request_invalid_json(mock_hass: MagicMock, webhook_id: str, mock_request: MagicMock, stored_token_hash: str, token: str) -> None:
    """Test a valid webhook request with invalid JSON data.

    Verifies that a 200 OK response is returned and the event is fired with empty data.

    Args:
        mock_hass (MagicMock): Mock HomeAssistant instance fixture.
        webhook_id (str): Webhook ID fixture.
        mock_request (MagicMock): Mock request fixture.
        stored_token_hash (str): Stored token hash fixture.
        token (str): Authentication token fixture.
    """
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    mock_request.json = AsyncMock(side_effect=ValueError)
    
    response = await handle_webhook(mock_hass, webhook_id, mock_request, stored_token_hash)
    
    assert response.status == 200
    assert response.text == "OK"
    mock_hass.bus.async_fire.assert_called_once_with(
        f"{DOMAIN}_event",
        {
            "webhook_id": webhook_id,
            "data": {},
        }
    )

@pytest.mark.asyncio
async def test_exception_handling(mock_hass: MagicMock, webhook_id: str, mock_request: MagicMock, stored_token_hash: str, token: str) -> None:
    """Test exception handling during request processing.

    Verifies that a 500 Internal Server Error response is returned on unexpected exceptions.

    Args:
        mock_hass (MagicMock): Mock HomeAssistant instance fixture.
        webhook_id (str): Webhook ID fixture.
        mock_request (MagicMock): Mock request fixture.
        stored_token_hash (str): Stored token hash fixture.
        token (str): Authentication token fixture.
    """
    mock_request.headers = {"Authorization": f"Bearer {token}"}
    mock_request.json = AsyncMock(side_effect=Exception("Unexpected error"))
    
    response = await handle_webhook(mock_hass, webhook_id, mock_request, stored_token_hash)
    
    assert response.status == 500
