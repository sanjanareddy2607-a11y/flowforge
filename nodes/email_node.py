# nodes/email_node.py

# WHAT THIS DOES:
# Sends an email with the previous node's output as the body.
# Uses Python's built-in smtplib — no extra library needed.

import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
from nodes.base_node import BaseNode

load_dotenv()

class EmailNode(BaseNode):
    """
    Sends email with pipeline output.
    
    Config options:
        to          : Recipient email address
        subject     : Email subject line
        input_key   : Which key from previous node to use as body
    
    Example config:
        {
            "id": "send_report",
            "type": "email",
            "config": {
                "to": "you@example.com",
                "subject": "FlowForge Daily Digest",
                "input_key": "summary"
            }
        }
    """

    def run(self, input_data: dict) -> dict:
        to_email  = self.config.get("to", "")
        subject   = self.config.get("subject", "FlowForge Output")
        input_key = self.config.get("input_key", "ai_response")
        body      = str(input_data.get(input_key, str(input_data)))

        sender   = os.getenv("EMAIL_SENDER")
        password = os.getenv("EMAIL_PASSWORD")

        try:
            # Build the email message
            msg             = MIMEMultipart()
            msg["From"]     = sender
            msg["To"]       = to_email
            msg["Subject"]  = subject
            msg.attach(MIMEText(body, "plain"))

            # Connect to Gmail's SMTP server and send
            # Port 587 = TLS (secure) connection
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()                    # Upgrade to secure connection
            server.login(sender, password)       # Login with app password
            server.send_message(msg)             # Send the email
            server.quit()

            status = f"Email sent to {to_email}"

        except Exception as e:
            status = f"Email node error: {str(e)}"

        # Return original data + email status
        result = dict(input_data)
        result["email_status"] = status
        return result 