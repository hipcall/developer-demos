# Hipcall External Management Demo

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This project is a basic dummy program that demonstrates how [**Hipcall External Management**](https://use.hipcall.com.tr/portal/customer-service/contents/hipcall/gelis%CC%A7tirme-arac%CC%A7lar%C4%B1/hipcall-harici-yo%CC%88netim-external-management-nedir-ve-nas%C4%B1l-kullan%C4%B1l%C4%B1r/) features communicate with different systems and how they can be used. This program should be considered as the customer’s own software that integrates with Hipcall External Management and can be further developed according to their specific needs.

---

## 🚀 Features

The project demonstrates a core telephony interaction:

   **PIN Query (PIN Sorgulama):**
    *   Authenticates users by requesting a 1-4 digit PIN code via IVR.
    *   Matches the caller's phone number in the database.
    *   **Success:** If PIN is correct, redirects the call to the **Customer Representative** (`1091`).
    *   **Failure:** If PIN is incorrect, redirects the call to the **Sales Team** (`1092`).

---

## 🛠 Usage & Administration

The application provides a web-based dashboard for managing the system:

*   **User Management:** Add, edit, or delete user records and their respective PIN codes.
*   **Log Tracking:** Monitor real-time logs of the webhook POST requests coming from the Hipcall Ingress API. You can see the full request body (caller info, digits pressed, etc.) and the JSON sequence response returned by the system.

---

## 📂 Project Structure

```text
user_management_system/
├── app.py              # Main Flask application (API & Web Routes)
├── init_db.py          # Database initialization and seeding script
├── entrypoint.sh       # Docker entrypoint script (Restores DB from seed)
├── Dockerfile          # Docker image configuration
├── docker-compose.yml  # Docker Compose orchestration
├── requirements.txt    # Python dependencies
├── data/               # Persistent storage for SQLite database
│   ├── database.db     # Active SQLite database
│   └── database.db.seed # Seed file for database resets
├── static/             # Static assets (CSS, JS, and Audio files)
│   └── audio/          # MP3 files used for IVR responses
└── templates/          # HTML templates for the dashboard
```

---

## ⚙️ Getting Started

### Prerequisites
- Docker & Docker Compose (Recommended)
- [ngrok](https://ngrok.com/) (Required for receiving webhooks from Hipcall on your local machine)
- Python 3.8+ (For local development)

### Running with Docker

```bash
docker-compose up --build
```
The application will be accessible at `http://localhost:5000`.

### Using External Management in Hipcall
You can create a new external management by clicking **Settings > Developer > External Managements** in the top right corner.
The endpoint used for this dummy application is: `/api/external/hipcall-ingress`

### Exposing for Hipcall (ngrok)
Since Hipcall needs a public URL to communicate with your local dummy application, use ngrok to tunnel your local port:
1. Run: `ngrok http 5000`
2. Copy the generated Forwarding URL (e.g., `https://random-id.ngrok-free.app`).
3. Your Hipcall External Management target URL will be: `https://random-id.ngrok-free.app/api/external/hipcall-ingress`

**Default Login:**
- **Username:** `admin`
- **Password:** `admin123`

---

## 📄 License
This project is licensed under the MIT License.
