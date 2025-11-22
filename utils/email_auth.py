import sqlite3
import time
import os

DB_PATH = "users.db"


# -----------------------------
# Database Connection
# -----------------------------
def get_conn():
    return sqlite3.connect(DB_PATH)


# -----------------------------
# Create Table
# -----------------------------
def create_table():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS email_auth (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL,
            otp TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


# -----------------------------
# Store OTP
# -----------------------------
def store_otp(email: str, otp: str):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO email_auth (email, otp, timestamp) VALUES (?, ?, ?)",
        (email, otp, int(time.time())),
    )
    conn.commit()
    conn.close()


# -----------------------------
# Verify OTP
# -----------------------------
def verify_otp(email: str, otp: str) -> bool:
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT otp FROM email_auth
        WHERE email=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (email,),
    )
    row = cur.fetchone()
    conn.close()

    if not row:
        return False

    return row[0] == otp


# -----------------------------
# Check if email is verified
# -----------------------------
def is_verified(email: str) -> bool:
    """
    Checks whether an email has ANY OTP record.
    You can expand this later to require "successful OTP".
    """
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id FROM email_auth
        WHERE email=?
        ORDER BY id DESC
        LIMIT 1
        """,
        (email,),
    )
    row = cur.fetchone()
    conn.close()

    return row is not None


# Initialize DB on import
create_table()
