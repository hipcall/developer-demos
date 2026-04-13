# Hipcall External Management Demo

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.0%2B-green.svg)](https://flask.palletsprojects.com/)

This project is a demonstration of [**Hipcall External Management**](https://use.hipcall.com.tr/portal/customer-service/contents/hipcall/gelis%CC%A7tirme-arac%CC%A7lar%C4%B1/hipcall-harici-yo%CC%88netim-external-management-nedir-ve-nas%C4%B1l-kullan%C4%B1l%C4%B1r/) capabilities. It shows how Hipcall's telephony features can communicate with external systems to perform real-time logic, such as PIN verification and dynamic call routing.

---

## 🚀 Features

The project demonstrates a core telephony interaction:

**PIN Query (PIN Sorgulama):**
* Authenticates users by requesting a 1-4 digit PIN code via IVR.
* Matches the caller's phone number in the local database.
* Success: If the PIN is correct, redirects the call to the **Customer Representative** (`1091`).
* Failure: If the PIN is incorrect, redirects the call to the **Sales Team** (`1092`).

---

## 🛠 Usage & Administration

The application provides a web-based dashboard:
* **User Management:** Add, edit, or delete user records and their respective PIN codes.
* **Log Tracking:** Monitor real-time logs of webhook POST requests from the Hipcall Ingress API, including the full request body and the JSON response returned.

---

## ⚙️ Installation & Setup

### Prerequisites
- [ngrok](https://ngrok.com/)
- Docker & Docker Compose (Recommended) **OR** Python 3.8+

---

### Option 1: Running with Docker (Recommended)
Docker manages the environment and dependencies for you.

1. **Start the application**:
   ```bash
   docker-compose up -d --build
   ```
2. The dashboard will be accessible at `http://localhost:5000`.

---

### Option 2: Running Locally (Without Docker)
If you prefer to run the application directly on your system:

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
4. The dashboard will be accessible at `http://localhost:5000`.

---

## 🔗 Hipcall Integration

### 1. Exposing to the Internet (ngrok)
Hipcall needs a public URL to communicate with your local application.
1. Run: `ngrok http 5000`
2. Copy the generated URL (e.g., `https://random-id.ngrok-free.app`).
3. Your Hipcall target URL will be: `https://<your-ngrok-url>/api/external/hipcall-ingress`

### 2. Configuration in Hipcall
1. Go to **Settings > Developer > External Managements**.
2. Create a new entry and set the **Target URL** to your ngrok address.
3. Use the integration in your IVR or call flow.

**Default Admin Login:**
- **Username:** `admin`
- **Password:** `admin123`
