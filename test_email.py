import os
import smtplib
from email.mime.text import MIMEText

# Read env vars from Replit "Secrets"
host = os.getenv("EMAIL_HOST")
port = os.getenv("EMAIL_PORT")
user = os.getenv("EMAIL_USER")
password = os.getenv("EMAIL_PASS")

if not all([host, port, user, password]):
    print("❌ Missing email environment variables.")
    print("Make sure you added EMAIL_HOST, EMAIL_PORT, EMAIL_USER, EMAIL_PASS in Replit → Tools → Secrets")
    exit()

# Prepare email
msg = MIMEText("Test email from Replit OTP system.")
msg["Subject"] = "OTP Test"
msg["From"] = user
msg["To"] = user

try:
    with smtplib.SMTP(host, int(port)) as server:
        server.starttls()
        server.login(user, password)
        server.send_message(msg)

    print("✅ Email sent successfully! Check your inbox.")
except Exception as e:
    print("❌ Error sending email:", e)