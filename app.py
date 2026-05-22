"""app.py — LiveLong AI entry point. Run: python app.py"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from flask import Flask
from routes.main import main

app = Flask(__name__)
app.secret_key = "livelong-ai-v3-secret-2024"
app.register_blueprint(main)

def ensure_db():
    db_path = os.path.join("database", "livelong.db")
    if not os.path.exists(db_path):
        print("[APP] Initialising database…")
        from database.init_db import init_database
        init_database()
    else:
        print("[APP] ✅ Database found")

if __name__ == "__main__":
    ensure_db()
    print("[APP] LiveLong AI starting at http://127.0.0.1:5000")
    app.run(debug=True, port=5000)
