import os
import base64
import json
import requests
import random
import string
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

def get_gmail_access_token():
    """Get Gmail access token from Replit connection"""
    try:
        hostname = os.environ.get('REPLIT_CONNECTORS_HOSTNAME')
        x_replit_token = None
        
        # Check for REPL_IDENTITY (repl token) or WEB_REPL_RENEWAL (deployment token)
        repl_identity = os.environ.get('REPL_IDENTITY')
        web_repl_renewal = os.environ.get('WEB_REPL_RENEWAL')
        
        if repl_identity:
            x_replit_token = 'repl ' + repl_identity
        elif web_repl_renewal:
            x_replit_token = 'depl ' + web_repl_renewal
        
        if not hostname or not x_replit_token:
            raise Exception('Replit connection environment variables not found')
        
        # Fetch connection settings from Replit
        url = f'https://{hostname}/api/v2/connection?include_secrets=true&connector_names=google-mail'
        headers = {
            'Accept': 'application/json',
            'X_REPLIT_TOKEN': x_replit_token
        }
        
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        connection_settings = data.get('items', [{}])[0]
        
        # Get access token from connection settings
        access_token = (
            connection_settings.get('settings', {}).get('access_token') or
            connection_settings.get('settings', {}).get('oauth', {}).get('credentials', {}).get('access_token')
        )
        
        if not access_token:
            raise Exception('Gmail access token not found in connection')
        
        return access_token
    
    except Exception as e:
        print(f"Error getting Gmail access token: {e}")
        return None

def create_message(sender, to, subject, body_text, body_html=None):
    """Create a message for an email"""
    if body_html:
        message = MIMEMultipart('alternative')
        part1 = MIMEText(body_text, 'plain')
        part2 = MIMEText(body_html, 'html')
        message.attach(part1)
        message.attach(part2)
    else:
        message = MIMEText(body_text)
    
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    
    # Encode as base64url
    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    return {'raw': raw}

def send_email(to_email, subject, body_text, body_html=None, from_email='me'):
    """Send an email using Gmail API"""
    try:
        # Get access token
        access_token = get_gmail_access_token()
        if not access_token:
            return False, "Failed to get Gmail access token"
        
        # Create credentials from access token
        creds = Credentials(token=access_token)
        
        # Build Gmail API service
        service = build('gmail', 'v1', credentials=creds)
        
        # Create message
        message = create_message(from_email, to_email, subject, body_text, body_html)
        
        # Send message
        result = service.users().messages().send(userId='me', body=message).execute()
        
        return True, f"Email sent successfully! Message ID: {result['id']}"
    
    except HttpError as error:
        return False, f"Gmail API error: {error}"
    except Exception as e:
        return False, f"Error sending email: {e}"

def send_feedback_email(user_name, user_email, feedback_text, assessment_score=None):
    """Send feedback email to T-Logic"""
    subject = f"Assessment Feedback from {user_name}"
    
    body_text = f"""
New Feedback Received from AI Process Readiness Assessment

From: {user_name}
Email: {user_email}
{f'Assessment Score: {assessment_score}' if assessment_score else ''}

Feedback:
{feedback_text}

---
Sent from AI Process Readiness Assessment Tool
"""
    
    body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <h2 style="color: #BF6A16;">New Feedback Received</h2>
    <p><strong>From:</strong> {user_name}</p>
    <p><strong>Email:</strong> {user_email}</p>
    {f'<p><strong>Assessment Score:</strong> {assessment_score}</p>' if assessment_score else ''}
    
    <h3>Feedback:</h3>
    <p style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
        {feedback_text.replace(chr(10), '<br>')}
    </p>
    
    <hr style="margin-top: 30px;">
    <p style="color: #666; font-size: 0.9em;">Sent from AI Process Readiness Assessment Tool</p>
</body>
</html>
"""
    
    return send_email('info@tlogic.consulting', subject, body_text, body_html)

def send_user_registration_email(user_name, user_email, user_title=None, user_company=None, user_phone=None, user_location=None):
    """Send user registration notification email to T-Logic"""
    subject = f"New Assessment Started - {user_name}"
    
    body_text = f"""
New User Started AI Process Readiness Assessment

Contact Information:
- Name: {user_name}
- Email: {user_email}
{f'- Title: {user_title}' if user_title else ''}
{f'- Company: {user_company}' if user_company else ''}
{f'- Phone: {user_phone}' if user_phone else ''}
{f'- Location: {user_location}' if user_location else ''}

The user has just started the assessment process.

---
Sent from AI Process Readiness Assessment Tool
"""
    
    body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <h2 style="color: #BF6A16;">📋 New Assessment Started</h2>
    
    <h3>Contact Information:</h3>
    <ul>
        <li><strong>Name:</strong> {user_name}</li>
        <li><strong>Email:</strong> {user_email}</li>
        {f'<li><strong>Title:</strong> {user_title}</li>' if user_title else ''}
        {f'<li><strong>Company:</strong> {user_company}</li>' if user_company else ''}
        {f'<li><strong>Phone:</strong> {user_phone}</li>' if user_phone else ''}
        {f'<li><strong>Location:</strong> {user_location}</li>' if user_location else ''}
    </ul>
    
    <p style="margin-top: 20px;">The user has just started the assessment process.</p>
    
    <hr style="margin-top: 30px;">
    <p style="color: #666; font-size: 0.9em;">Sent from AI Process Readiness Assessment Tool</p>
</body>
</html>
"""
    
    return send_email('info@tlogic.consulting', subject, body_text, body_html)

def send_assistance_request_email(user_name, user_email, query=None, assessment_results=None):
    """Send assistance request email to T-Logic"""
    subject = f"Assistance Request from {user_name}"
    
    total_score = assessment_results.get('total', 'N/A') if assessment_results else 'N/A'
    readiness_level = assessment_results.get('readiness_band', {}).get('label', 'N/A') if assessment_results else 'N/A'
    
    body_text = f"""
New Assistance Request from AI Process Readiness Assessment

Contact Information:
- Name: {user_name}
- Email: {user_email}

Query:
{query if query else 'No specific query provided'}

Assessment Results:
- Total Score: {total_score}/30
- Readiness Level: {readiness_level}

---
Sent from AI Process Readiness Assessment Tool
"""
    
    body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <h2 style="color: #BF6A16;">🚀 New Assistance Request</h2>
    
    <h3>Contact Information:</h3>
    <ul>
        <li><strong>Name:</strong> {user_name}</li>
        <li><strong>Email:</strong> {user_email}</li>
    </ul>
    
    <h3>Query:</h3>
    <p style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
        {query.replace(chr(10), '<br>') if query else 'No specific query provided'}
    </p>
    
    <h3>Assessment Results:</h3>
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin: 10px 0;">
        <p><strong>Total Score:</strong> {total_score}/30</p>
        <p><strong>Readiness Level:</strong> {readiness_level}</p>
    </div>
    
    <hr style="margin-top: 30px;">
    <p style="color: #666; font-size: 0.9em;">Sent from AI Process Readiness Assessment Tool</p>
</body>
</html>
"""
    
    return send_email('tej@tlogic.consulting', subject, body_text, body_html)

def generate_verification_code():
    """Generate a 6-digit verification code"""
    return ''.join(random.choices(string.digits, k=6))

def send_verification_code_email(user_email, verification_code):
    """Send verification code to user's email"""
    subject = "Your AI Readiness Assessment Report Verification Code"
    
    body_text = f"""
Verification Code: {verification_code}

This code is valid for 10 minutes. Please enter this code to download your AI Process Readiness Assessment Report.

If you did not request this code, please ignore this email.

---
Sent from AI Process Readiness Assessment Tool
"""
    
    body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <h2 style="color: #BF6A16;">Verify Your Email</h2>
    
    <p>Your verification code is:</p>
    <h1 style="text-align: center; color: #BF6A16; letter-spacing: 2px; font-size: 2rem;">{verification_code}</h1>
    
    <p>This code is valid for 10 minutes. Please enter this code in the dialog to download your AI Process Readiness Assessment Report.</p>
    
    <p style="color: #999; font-size: 0.9em; margin-top: 30px;">If you did not request this code, please ignore this email.</p>
    
    <hr style="margin-top: 30px;">
    <p style="color: #666; font-size: 0.9em;">Sent from AI Process Readiness Assessment Tool</p>
</body>
</html>
"""
    
    return send_email(user_email, subject, body_text, body_html)

def send_pdf_download_notification(user_email, assessment_results=None):
    """Send notification that PDF was downloaded"""
    subject = f"Assessment Report Downloaded"
    
    total_score = assessment_results.get('total', 'N/A') if assessment_results else 'N/A'
    readiness_level = assessment_results.get('readiness_band', {}).get('label', 'N/A') if assessment_results else 'N/A'
    
    body_text = f"""
AI Process Readiness Assessment Report Downloaded

User Email: {user_email}
Total Score: {total_score}/30
Readiness Level: {readiness_level}

A user has downloaded their assessment report after completing the AI Process Readiness Assessment.

---
Sent from AI Process Readiness Assessment Tool
"""
    
    body_html = f"""
<html>
<body style="font-family: Arial, sans-serif; color: #333;">
    <h2 style="color: #BF6A16;">📊 Assessment Report Downloaded</h2>
    
    <h3>User Information:</h3>
    <p><strong>Email:</strong> {user_email}</p>
    
    <h3>Assessment Results:</h3>
    <div style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">
        <p><strong>Total Score:</strong> {total_score}/30</p>
        <p><strong>Readiness Level:</strong> {readiness_level}</p>
    </div>
    
    <p style="margin-top: 20px;">A user has successfully downloaded their assessment report.</p>
    
    <hr style="margin-top: 30px;">
    <p style="color: #666; font-size: 0.9em;">Sent from AI Process Readiness Assessment Tool</p>
</body>
</html>
"""
    
    return send_email('tej@tlogic.consulting', subject, body_text, body_html)
