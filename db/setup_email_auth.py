import sqlite3
import os

os.makedirs("db", exist_ok=True)

conn = sqlite3.connect("db/users.db")
c = conn.cursor()

c.execute("""
CREATE TABLE IF NOT EXISTS email_auth (
    email TEXT PRIMARY KEY,
    otp TEXT,
    verified INTEGER DEFAULT 0,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("Email auth table ready.")