"""database/init_db.py — Run once to create LiveLong AI database."""
import sqlite3, os
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
DB_PATH    = os.path.join(BASE_DIR, "livelong.db")
SCHEMA_SQL = os.path.join(BASE_DIR, "schema.sql")

def init_database():
    print(f"[DB] Initialising: {DB_PATH}")
    with open(SCHEMA_SQL) as f:
        sql = f.read()
    conn = sqlite3.connect(DB_PATH)
    conn.executescript(sql)
    conn.commit()
    conn.close()
    print("[DB] ✅ LiveLong AI database ready!")

if __name__ == "__main__":
    init_database()
