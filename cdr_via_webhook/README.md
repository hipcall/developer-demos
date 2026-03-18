# Hipcall CDR Webhook Integration Example (Dummy App)

This is a **dummy application** designed to demonstrate how to receive and process Call Detail Records (CDR) from Hipcall using webhooks. It serves as a reference implementation for developers looking to integrate Hipcall events into their own systems.

## 📋 Overview

The goal of this project is to show the end-to-end flow of a CDR webhook integration:
1.  **Hipcall** triggers a `call.ended` or `call_hangup` event.
2.  The **Webhook Endpoint** (`/webhook/hipcall-cdr`) receives the JSON payload.
3.  The **Backend** (Flask) parses the data and stores it in a local SQLite database.
4.  A **Simple Dashboard** displays the recorded data for verification.

## 🛠️ Setup Instructions

### 1. Prerequisites
- Python 3.8+
- [ngrok](https://ngrok.com/) (required for receiving webhooks on a local machine)

### 2. Installation
```bash
# Install required Python packages
pip install -r requirements.txt

# Initialize the SQLite database schema
python init_db.py

# Run the Flask development server
python app.py
```
The application will run locally at `http://localhost:5007`.

### 3. Docker Setup (Recommended)
You can run the entire stack using Docker and Docker Compose without manual dependency installation:
```bash
# Build and start the container in detached mode
docker-compose up -d
```
The app will be available at `http://localhost:5007`. The database file will be persisted in the `./data` directory on your host machine.

### 4. Exposing for Hipcall (ngrok)
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
| **Events** | `Call Ended` (`call.ended`) |
| **Method** | `POST` |

## 📂 Project Structure

- `app.py`: Contains the webhook endpoint logic and basic API.
- `init_db.py`: Sets up the database tables (ran automatically in Docker).
- `Dockerfile` & `docker-compose.yml`: Containerization configuration.
- `templates/index.html`: A basic dashboard to view received CDRs.
- `data/`: Directory where the SQLite database file is stored.

---
*Note: This is a demonstration project and is not intended for production use without further security and scalability considerations.*
