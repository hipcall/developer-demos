# Call Via Order Number – Hipcall Speed Dial Demo

This demo application showcases how **Hipcall's Speed Dial** feature can be extended to route calls based on **external data that does not exist within Hipcall itself**.

> [!IMPORTANT]
> This is a **dummy program** designed for demonstration purposes. It uses a specific scenario to show how Hipcall can integrate with external systems to protect user privacy and automate call routing.

---

## 📖 The Scenario: Courier & Customer Privacy

In this scenario, we simulate a delivery service where:
*   A **courier** needs to call a **customer** regarding an order.
*   For **privacy and data protection**, the courier is not allowed to see the customer's actual phone number.
*   The courier only knows the **Order Number** (e.g., `12345`).

### How the Demo Works:
1.  The courier dials a designated **Speed Dial extension** (e.g., `72`) on their Hipcall phone.
2.  Hipcall prompts: *"Please enter the order number."*
3.  The courier enters the digits (e.g., `12345`).
4.  Hipcall sends this code to this **dummy application** via a webservice request.
5.  The application looks up the order number in its local database, finds the associated customer number, and returns it to Hipcall.
6.  Hipcall **automatically bridges the call**, connecting the courier to the customer without ever revealing the phone number.

---

## 🛠 Project Structure

```text
call_via_order_number/
├── app.py              # Main Flask application (Webhook & Dashboard)
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Docker orchestration
├── data/               # Persistent SQLite database storage
├── static/             # Modern UI styling (CSS/JS)
└── templates/          # HTML templates for the management dashboard
```

---

## ⚙️ Installation & Requirements

### What You Need:
- **Hipcall Account**: With "Speed Dial" (Hızlı Arama) feature enabled.
- **ngrok**: To expose your local environment to Hipcall.
- **Docker** (Recommended) **OR** **Python 3.8+**.

---

### Option 1: Running with Docker (Recommended)
```bash
docker-compose up -d --build
```
*The application starts automatically on port `5010`.*

### Option 2: Running Locally
1. **Install dependencies**: `pip install -r requirements.txt`
2. **Initialize DB**: `python3 init_db.py`
3. **Start app**: `python3 app.py`
*The dashboard will be available at `http://localhost:5010`.*

---

## 🔗 Hipcall Integration

1.  **Expose Port 5010**: `ngrok http 5010`
2.  **Webhook URL**: Copy the ngrok URL and add `/lookup` (e.g., `https://.../lookup`).
3.  **Hipcall Setup**: Navigate to **Account > Integrations > Speed Dial** and set:
    *   **Extension**: `72`
    *   **Announcement**: "Please enter the order number."
    *   **Webservice URL**: Your ngrok lookup URL.
