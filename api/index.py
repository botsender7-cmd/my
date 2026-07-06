import os
import smtplib

from email.mime.text import MIMEText

from fastapi import FastAPI, HTTPException, Header, Depends, Request
from pydantic import BaseModel, EmailStr

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from fastapi.responses import JSONResponse

app = FastAPI(title="SMTP API")

# ===========================
# RATE LIMIT
# ===========================

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_middleware(SlowAPIMiddleware)


@app.exception_handler(RateLimitExceeded)
async def rate_limit_handler(request, exc):
    return JSONResponse(
        status_code=429,
        content={
            "success": False,
            "message": "Too many requests"
        }
    )


# ===========================
# ENV
# ===========================

SMTP_HOST = os.getenv("SMTP_HOST")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASS = os.getenv("SMTP_PASS")

API_KEY = os.getenv("API_KEY")


# ===========================
# API KEY
# ===========================

def verify_api_key(x_api_key: str = Header(None)):
    if x_api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="Invalid API Key"
        )


# ===========================
# MODEL
# ===========================

class EmailRequest(BaseModel):
    email: EmailStr
    subject: str
    message: str


# ===========================
# HOME
# ===========================

@app.get("/")
def home():
    return {
        "success": True,
        "service": "SMTP API"
    }


# ===========================
# SEND EMAIL
# ===========================

@app.post("/send-email")
@limiter.limit("10/minute")
def send_email(
    request: Request,
    data: EmailRequest,
    _: str = Depends(verify_api_key)
):

    msg = MIMEText(data.message)

    msg["Subject"] = data.subject
    msg["From"] = SMTP_USER
    msg["To"] = data.email

    try:

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=30) as smtp:

            smtp.starttls()

            smtp.login(
                SMTP_USER,
                SMTP_PASS
            )

            smtp.send_message(msg)

        return {
            "success": True,
            "message": "Email Sent"
        }

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )
