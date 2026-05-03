import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

def send_outreach_email(target_email, subject, body):
    # Pulling credentials from the vault
    sender_email = os.getenv("AGENCY_EMAIL")
    sender_password = os.getenv("AGENCY_EMAIL_PASSWORD") 
    
    msg = MIMEMultipart()
    msg['From'] = f"NexGen Builds <{sender_email}>"
    msg['To'] = target_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))
    
    try:
        # Configured for Zoho Mail's SSL port
        server = smtplib.SMTP_SSL('smtp.zoho.com', 465)
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        return True, "Email dispatched successfully."
    except Exception as e:
        return False, f"Failed to send: {str(e)}"