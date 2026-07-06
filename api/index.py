import os
import smtplib
from email.mime.text import MIMEText
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(title="SMTP API")


class EmailRequest(BaseModel):
    email: str
    subject: str
    message: str


SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")


@app.get("/")
def home():
    return {
        "status": "running",
        "service": "SMTP API"
    }


@app.post("/send-email")
def send_email(data: EmailRequest):

    msg = MIMEText(data.message, "plain", "utf-8")
    msg["Subject"] = data.subject
    msg["From"] = SMTP_USER
    msg["To"] = data.email

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()

            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)

        return {
            "success": True,
            "message": "Email Sent Successfully"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
