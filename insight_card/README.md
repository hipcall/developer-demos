# Hipcall Insight Card Demo

This scenario focuses on the usage of the Hipcall Insight Card feature. It simulates receiving information via webhooks and creating a card through an API request to be displayed on the Hipcall Webphone.

## Table of Contents
- [Overview](#overview)
- [Ngrok: Exposing Your Local Server](#ngrok-exposing-your-local-server)
- [Prerequisites](#prerequisites)
- [Method 1: Running with Docker (Recommended)](#method-1-running-with-docker-recommended)
- [Method 2: Running Locally (Without Docker)](#method-2-running-locally-without-docker)
- [Hipcall Webhook Configuration](#hipcall-webhook-configuration)

## Overview
1. **Webhook Reception**: The application listens for `call_init` events from Hipcall.
2. **Contact Matching**: It searches a local SQLite database for the caller/callee number.
3. **Insight Card Delivery**: If a match is found, it sends a personalized information card (Name, Company, Balance) to the Hipcall Card API to be displayed on the agent's screen.

## Ngrok: Exposing Your Local Server
Hipcall needs a public URL to send webhook events to your application. Since your application runs on `localhost`, you need a tool like **ngrok** to create a secure tunnel.

1. Install ngrok if you haven't: [ngrok.com](https://ngrok.com/)
2. Run ngrok on port `5009`:
   ```bash
   ngrok http 5009
   ```
3. Copy the `Forwarding` URL (e.g., `https://random-id.ngrok-free.app`). Your webhook URL will be: `https://<your-ngrok-url>/webhook/insight-card`.

## Prerequisites
- Hipcall API Token (Get it from Account > API Tokens)
- Python 3.9+ (if running locally)

Create a `.env` file in the project root:
```bash
HIPCALL_API_TOKEN=your_hipcall_api_token_here
```

---

## Method 1: Running with Docker (Recommended)
Docker simplifies the setup by managing dependencies and the environment for you.

1. **Build and start the container**:
   ```bash
   docker-compose up -d --build
   ```
   *Note: This command automatically initializes the database and starts the web server on port 5009.*

2. **Stop the container**:
   ```bash
   docker-compose down
   ```

---

## Method 2: Running Locally (Without Docker)
If you prefer to run it directly on your system:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Initialize the database**:
   ```bash
   python3 init_db.py
   ```

3. **Start the application**:
   ```bash
   python3 app.py
   ```
   The application will be available at `http://localhost:5009`.

---

## Hipcall Webhook Configuration
To see the insight card in action:

1. Log in to your Hipcall account.
2. Navigate to **Account > Integrations > Create New Integration > Webhook**.
3. Set the **Target URL** to your ngrok URL: `https://<your-ngrok-url>/webhook/insight-card`.
4. Select the **Call Init** (`call_init`) event.
5. Save the integration.

Now, whenever you receive or make a call, the application will look up the number in your database and display the contact's information on your Webphone!
