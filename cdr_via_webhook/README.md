# Hipcall CDR Webhook Integration Example (Dummy App)

This is a **dummy application** designed to demonstrate how to receive and process Call Detail Records (CDR) from Hipcall using webhooks. It serves as a reference implementation for developers looking to integrate Hipcall events into their own systems.

## 📋 Overview

The goal of this project is to show the end-to-end flow of a CDR webhook integration:
1.  **Hipcall** triggers a `call_hangup` event when a call ends.
2.  The **Webhook Endpoint** (`/webhook/hipcall-cdr`) receives the JSON payload.
3.  The **Backend** (Flask) parses the data and stores it in a local SQLite database.
4.  If a `record_url` is present, the call recording is automatically downloaded to the `data/records/` directory after a short delay.
5.  A **Simple Dashboard** displays the recorded data and allows playback of downloaded recordings.

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.8+
- [ngrok](https://ngrok.com/) (required for receiving webhooks on a local machine)

### 2. Environment Variables
Create a `.env` file in the project root:
```bash
HIPCALL_API_TOKEN=your_api_token_here
```

### 3. Installation
```bash
# Install required Python packages
pip install -r requirements.txt

# Initialize the SQLite database schema
python init_db.py

# Run the Flask development server
python app.py
```
The application will run locally at `http://localhost:5007`.

### 4. Docker Setup (Recommended)
You can run the entire stack using Docker and Docker Compose without manual dependency installation:
```bash
# Build and start the container in detached mode
docker-compose up -d
```
The app will be available at `http://localhost:5007`. The database and downloaded recordings will be persisted in the `./data` directory on your host machine.

### 5. Exposing for Hipcall (ngrok)
Since Hipcall needs a public URL to send webhooks, use ngrok to tunnel your local port:
1. Run: `ngrok http 5007`
2. Copy the generated URL (e.g., `https://random-id.ngrok-free.app`).
3. Your webhook target URL will be: `https://random-id.ngrok-free.app/webhook/hipcall-cdr`

## 🔗 Hipcall Configuration

At Hipcall you need to create a Webhook integration. At Account > Integrations > Create New Integration > Webhook.

In your Hipcall Webhook settings, use the following configuration:

| Field | Value |
| :--- | :--- |
| **Target URL** | Your ngrok or Server URL + `/webhook/hipcall-cdr` |
| **Events** | `Call Hangup` (`call_hangup`) |
| **Method** | `POST` |

## 🔊 Call Recording Download

When a `call_hangup` webhook includes a `record_url`, the application automatically downloads the recording in the background:

- The download starts after a **10-second delay** to ensure the recording file is available on storage.
- Recordings are saved to `data/records/<uuid>.mp3`.
- Once downloaded, the recording can be played back directly from the dashboard.

> **Note:** The `record_url` in the webhook payload is a pre-signed URL with a limited lifespan. The application downloads and stores the file locally so it remains accessible after the URL expires.

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/webhook/hipcall-cdr` | Receives CDR webhook payloads from Hipcall |
| `GET` | `/api/cdrs` | Returns the last 100 CDR records |
| `GET` | `/api/cdrs/<uuid>` | Returns full details of a specific CDR |
| `GET` | `/api/records/<filename>` | Serves a downloaded call recording file |

## 📂 Project Structure

```
cdr_via_webhook/
├── app.py                  # Webhook endpoint, API routes, and recording download logic
├── init_db.py              # Database schema initialization
├── requirements.txt        # Python dependencies
├── Dockerfile              # Container image definition
├── docker-compose.yml      # Container orchestration config
├── .env                    # Environment variables (not committed)
├── templates/
│   └── index.html          # Dashboard UI
├── static/
│   ├── css/style.css       # Dashboard styles
│   └── js/main.js          # Dashboard frontend logic
└── data/
    ├── cdr_database.db     # SQLite database
    └── records/            # Downloaded call recordings
```

---
*Note: This is a demonstration project and is not intended for production use without further security and scalability considerations.*
