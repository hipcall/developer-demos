# Button to Bridge – Hipcall Click-to-Call Demo

This is a **dummy application** designed to demonstrate how Hipcall's **Button to Bridge** feature works. A call button on a customer record triggers the Hipcall API, which first rings the agent's extension and then bridges the agent to the customer once answered.

> [!IMPORTANT]
> This is a **dummy program** designed for demonstration purposes. It uses a specific scenario to show how a CRM can initiate outbound calls through Hipcall with a single button click.

---

## 📖 The Scenario: Click-to-Call CRM

In this scenario, a user views a customer list and initiates a call directly from the browser:

1. The user clicks the **Call** button next to a customer.
2. The frontend sends the customer's phone number to the Flask backend.
3. The backend calls the **Hipcall API** using the configured user ID.
4. Hipcall **rings the user's phone/app first**.
5. Once the user answers, Hipcall **bridges the call** to the customer.

---

## 🛠 Project Structure

```text
button_to_bridge/
├── app.py              # Main Flask application (API & Dashboard)
├── init_db.py          # Database initialization script
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container configuration
├── docker-compose.yml  # Docker orchestration
├── .env                # Environment variables
├── data/               # Persistent SQLite database storage
├── static/             # UI styling and JavaScript
└── templates/          # HTML dashboard template
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
PORT=5011
HIPCALL_API_KEY="your_api_key_here"
```

### User ID (`HIPCALL_USER_ID`)

The `HIPCALL_USER_ID` constant in `app.py` identifies which agent's phone will ring when a call is initiated. This is the internal Hipcall ID of the user, **not** the extension number.

**How to find it:**
Navigate to **Hipcall → Settings → Users**, click on the relevant extension, and look at the ID in the browser's address bar.

```
Example: https://app.hipcall.com/settings/users/3508/edit
                                                    ^^^^
                                               This is the User ID
```

Set this value directly in `app.py`:

```python
HIPCALL_USER_ID = "3508"
```

---

## 🚀 Installation & Running

### Option 1: Docker (Recommended)

```bash
docker-compose up -d --build
```

*The application starts on port `5011`.*

### Option 2: Local

```bash
pip install -r requirements.txt
python init_db.py
python app.py
```

*The dashboard will be available at `http://localhost:5011`.*

---

## 📡 API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `/` | Customer management dashboard |
| `GET` | `/api/customers` | List all customers |
| `POST` | `/api/customers` | Add a new customer |
| `PUT` | `/api/customers/<id>` | Update a customer |
| `DELETE` | `/api/customers/<id>` | Delete a customer |
| `POST` | `/api/call` | Initiate a call via Hipcall API |

---

*Note: This is a demonstration project and is not intended for production use without further security and scalability considerations.*
