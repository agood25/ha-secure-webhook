<p align="center">
  <img src="custom_components/secure_webhook/logo.jpg" alt="Secure Webhook Logo" width="200">
</p>

# Secure Webhook for Home Assistant

[![Tests](https://github.com/agood25/ha-secure-webhook/actions/workflows/tests.yml/badge.svg)](https://github.com/agood25/ha-secure-webhook/actions/workflows/tests.yml)
[![codecov](https://codecov.io/gh/agood25/ha-secure-webhook/branch/main/graph/badge.svg)](https://codecov.io/gh/agood25/ha-secure-webhook)
[![Language](https://img.shields.io/github/languages/top/agood25/ha-secure-webhook)](https://github.com/agood25/ha-secure-webhook)
[![License](https://img.shields.io/github/license/agood25/ha-secure-webhook)](https://github.com/agood25/ha-secure-webhook/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/agood25/ha-secure-webhook)](https://github.com/agood25/ha-secure-webhook/releases)
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/integration)

A custom integration that replaces the standard, insecure Home Assistant webhooks with a secure, authenticated version. It validates requests using a cryptographically secure, hashed Bearer Token before firing an event in Home Assistant.

## Why use this?

Standard Home Assistant webhooks rely on the secrecy of the webhook ID itself. If that ID is leaked, anyone can trigger your automation. **Secure Webhook** adds a layer of authentication by requiring a Bearer Token in the HTTP header, which is hashed and verified securely.

## Features

- **Secure Storage**: Authentication tokens are SHA-256 hashed before saving.
- **Standard Auth**: Strictly enforces `Authorization: Bearer <token>` headers.
- **Multiple Endpoints**: Create as many unique webhook IDs as needed.
- **Safe IDs**: Automatically enforces URL-safe slugs for webhook IDs.
- **Event-Based**: Fires `secure_webhook_event` with payload data, allowing for complex automation logic.

## Installation

### Option 1: HACS (Recommended)

1.  Click the button below to open the repository in HACS:
    
    [![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=agood25&repository=ha-secure-webhook&category=integration)

2.  Click **Download**.
3.  Restart Home Assistant.

### Option 2: Manual Installation

1.  Download the `custom_components/secure_webhook` folder from this repository.
2.  Copy it to your Home Assistant `config/custom_components/` directory.
3.  Restart Home Assistant.

## Configuration

1.  Navigate to **Settings** > **Devices & Services**.
2.  Click **Add Integration** in the bottom right.
3.  Search for **Secure Webhook**.
4.  Enter a **Webhook ID** (e.g., `return_home`).
5.  Click **Submit**.

> **⚠️ IMPORTANT:** Copy the generated Authentication Token immediately. It is shown only once and cannot be retrieved later.

## Usage

### Sending a Request

To trigger the webhook, send a POST request to your Home Assistant instance with the generated Authorization header.

**Format:**
`POST /api/webhook/<YOUR_WEBHOOK_ID>`

**Headers:**
*   `Authorization: Bearer <YOUR_SECURE_TOKEN>`
*   `Content-Type: application/json`

**Example (cURL):**

```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_SECURE_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"status": "arrived", "person": "admin"}' \
  https://YOUR_HOME_ASSISTANT.com/api/webhook/YOUR_WEBHOOK_ID
```

### Consuming the Event in Automations

This integration does not use the standard "Webhook" trigger. Instead, it fires a standard Home Assistant Event named `secure_webhook_event`.

**Automation Example:**

```yaml
alias: "Handle Secure Webhook"
trigger:
  - platform: event
    event_type: secure_webhook_event
    event_data:
      webhook_id: return_home
action:
  - service: notify.mobile_app_phone
    data:
      message: "Webhook triggered by {{ trigger.event.data.person }}"
```

### Testing

1.  Go to **Developer Tools** > **Events**.
2.  In "Listen to events", type `secure_webhook_event` and click **Start listening**.
3.  Run the cURL command above.
4.  You should see the event appear with your data.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
