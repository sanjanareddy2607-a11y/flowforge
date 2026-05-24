import os
import resend
from dotenv import load_dotenv
from nodes.base_node import BaseNode

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

class EmailNode(BaseNode):
    def run(self, input_data: dict) -> dict:
        to_email  = self.config.get("to", "")
        subject   = self.config.get("subject", "FlowForge Output")
        input_key = self.config.get("input_key", "ai_response")
        body      = str(input_data.get(input_key, str(input_data)))

        try:
            params = {
                "from":    "FlowForge <onboarding@resend.dev>",
                "to":      [to_email],
                "subject": subject,
                "text":    body
            }
            email = resend.Emails.send(params)
            status = f"Email sent successfully. ID: {email['id']}"

        except Exception as e:
            status = f"Email node error: {str(e)}"

        result = dict(input_data)
        result["email_status"] = status
        return result
