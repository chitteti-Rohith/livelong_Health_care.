# LiveLine AI – Healthcare Navigator & Cost Estimation System

> *India's smart, budget-aware healthcare navigator*

---

## 🚀 Quick Start (Run in 3 commands)

```bash
# 1. Install the only dependency
pip install flask

# 2. Run the app (DB is auto-created on first run)
python app.py

# 3. Open in browser
# http://127.0.0.1:5000
```

That's it. No Docker, no complex setup.

---

## 📁 Project Structure

```
lifeline_ai/
│
├── app.py                     ← Flask entry point (run this)
├── requirements.txt           ← pip install flask
│
├── routes/
│   └── main.py                ← All URL routes (/, /analyse, /chat, /about)
│
├── utils/
│   ├── decision_engine.py     ← Core logic: symptom matching, severity, cost
│   └── chatbot.py             ← Rule-based chatbot
│
├── database/
│   ├── schema.sql             ← Full SQL schema + sample data
│   ├── init_db.py             ← One-time DB initialisation script
│   ├── db.py                  ← DB connection helper
│   └── lifeline.db            ← SQLite database (auto-created)
│
├── templates/
│   ├── index.html             ← Main app page
│   └── about.html             ← About page
│
└── static/
    ├── css/
    │   └── style.css          ← Full custom CSS (no frameworks)
    └── js/
        └── app.js             ← Frontend logic (fetch API, rendering)
```

---

## 🗄️ Database Schema

| Table             | Purpose                                       |
|-------------------|-----------------------------------------------|
| `symptoms`        | Symptom keywords + severity levels            |
| `conditions`      | Medical conditions mapped to symptom clusters |
| `cost_ranges`     | Govt vs Private cost per condition            |
| `hospitals`       | Real hospitals in 10 Indian cities            |
| `recommendations` | Audit log of all user queries                 |

**Covered cities:** Delhi, Mumbai, Bangalore, Chennai, Hyderabad, Kolkata, Pune, Ahmedabad, Nellore

---

## ⚙️ How the Decision Engine Works

```
User Input (symptoms + city + budget)
         │
         ▼
  Keyword Matching  ←── symptoms table
         │
         ▼
  Severity Detection  (low / medium / critical)
         │
         ▼
  Condition Matching  ←── conditions table
         │
         ▼
  Cost Lookup  ←── cost_ranges table
         │
         ▼
  Care Type Selection (budget vs cost)
  → home | clinic | govt | private
         │
         ▼
  Hospital Lookup  ←── hospitals table
         │
         ▼
  JSON Result → Frontend Rendering
```

---

## 💬 Chatbot Capabilities

The chatbot is **rule-based** (no ML/LLM required):
- Answers questions about govt/private hospitals
- Explains Ayushman Bharat / PM-JAY
- Handles emergency queries (redirects to 108)
- Provides context-aware replies based on last analysis result
- Covers: fever, dengue, diabetes, chest pain, home remedies, and more

---

## 🔌 API Endpoints

| Method | Endpoint   | Description                        |
|--------|------------|------------------------------------|
| GET    | `/`        | Main app page                      |
| POST   | `/analyse` | Analyse symptoms → JSON result     |
| POST   | `/chat`    | Chatbot message → JSON reply       |
| GET    | `/about`   | About page                         |

**POST /analyse** – Request body:
```json
{ "symptoms": "fever and headache", "city": "delhi", "budget": 2000 }
```

**POST /chat** – Request body:
```json
{ "message": "what is ayushman bharat?" }
```

---

## 🗺️ Future Roadmap (for production)

- [ ] Migrate SQLite → MySQL for multi-user production
- [ ] Add user login + history
- [ ] Integrate Google Maps API for real-time hospital location
- [ ] Add more symptom-condition pairs with doctor review
- [ ] Hindi language support
- [ ] Mobile app (Flutter/React Native) using the same Flask API


**Tech Stack:** Python · Flask · SQLite · HTML · CSS · JavaScript 

