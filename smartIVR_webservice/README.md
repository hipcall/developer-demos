# Hipcall Smart IVR Webhook Integration Example (Dummy App)

This is a **dummy application** designed to demonstrate how to integrate Hipcall's Smart IVR feature with an external web service. It serves as a reference implementation for developers looking to route incoming calls based on CRM data dynamically.

## 📋 Overview

The goal of this project is to show the end-to-end flow of a Smart IVR webhook integration:
1.  A call comes into **Hipcall**, and the Smart IVR app reaches out to your **Endpoint** (`/api/smart-ivr`).
2.  The **Backend** (Flask) receives the JSON payload containing the caller's phone number.
3.  The application queries a local SQLite database (acting as a basic CRM) to check if the caller is a registered customer.
4.  If the customer exists, the app responds with a routing instruction (e.g., {"extension": "1093"}).
5.  If not found, it responds with a different routing instruction (e.g., {"extension": "1094"}).
6.  A **Simple Dashboard** allows managing customers and viewing webhook request logs.

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
The application will run locally at `http://localhost:5008`.

### 3. Docker Setup (Recommended)
You can run the entire stack using Docker and Docker Compose without manual dependency installation:
```bash
# Build and start the container in detached mode
docker-compose up -d
```
The app will be available at `http://localhost:5008`. The database file will be persisted in the `./data` directory on your host machine.

### 4. Exposing for Hipcall (ngrok)
Since Hipcall needs a public URL to communicate with your Smart IVR service, use ngrok to tunnel your local port:
1. Run: `ngrok http 5008`
2. Copy the generated URL (e.g., `https://random-id.ngrok-free.app`).
3. Your webhook target URL will be: `https://random-id.ngrok-free.app/api/smart-ivr`

## 🔗 Hipcall Configuration

At Hipcall, navigate to **Settings > Phone System > Smart Routing** (Ayarlar > Telefon Sistemi > Akıllı Yönlendirmeler). Click on the **"New"** (Yeni) button and select **"Webservice"** (Webservis) as the route type.

In your Hipcall Smart IVR settings, use the following configuration:

| Field | Value |
| :--- | :--- |
| **URL** | Your ngrok or Server URL + `/api/smart-ivr` |
| **Authentication** | Enter the authentication details if required. |

*Ensure the returned JSON structure matches expectations defined in Hipcall documentation (e.g., `{"extension": "1093"}`).*

## 📂 Project Structure

- `app.py`: Contains the Smart IVR endpoint logic, CRM APIs, and frontend routes.
- `init_db.py`: Sets up the database tables and inserts dummy data (ran automatically in Docker).
- `Dockerfile` & `docker-compose.yml`: Containerization configuration.
- `templates/`: HTML templates for the CRM dashboard (`index.html`) and logs view (`logs.html`).
- `data/`: Directory where the SQLite database file (`crm.db`) is stored.

---
*Note: This is a demonstration project and is not intended for production use without further security and scalability considerations.*
