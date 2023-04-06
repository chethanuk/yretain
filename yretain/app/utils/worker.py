# worker.py

import os
import redis
from rq import Queue
from yretain.config import redis as redis_conf

REDIS_URL = os.getenv("REDIS_URL", redis_conf.REDIS_HOST)
redis_conn = redis.from_url(REDIS_URL)
queue = Queue(connection=redis_conn)


import os
import requests
from fastapi import FastAPI, Depends
from mailboxvalidator import SingleValidation, MBVApiKey

app = FastAPI()

# Define the MailboxValidator API key and object
mbv_api_key = MBVApiKey(os.environ.get("MAILBOXVALIDATOR_API_KEY"))
mbv = SingleValidation(mbv_api_key)

# Define the route for sending an email with validation and detection
@app.post("/send_email/", dependencies=[Depends(current_active_user)])
async def send_email(report: ReportFormat, email: str):
    # Validate the email address with MailboxValidator
    is_valid = mbv.ValidateEmail(email)
    if not is_valid:
        return {"message": "Invalid email address"}

    # Detect disposable and temporary email addresses with Disify HTTPS API
    response = requests.get(
        f"https://disify.com/check/{email}",
        headers={"X-API-Key": os.environ.get("DISIFY_API_KEY")}
    )
    if not response.ok:
        return {"message": "Error detecting email address"}
    result = response.json()
    if result["disposable"]:
        return {"message": "Disposable email address detected"}
    if result["temporary"]:
        return {"message": "Temporary email address detected"}

    # Send the email using the API
    response = requests.post(
        os.environ.get("EMAIL_API_URL"),
        headers={"Authorization": f"Bearer {os.environ.get('EMAIL_API_KEY')}"},
        json={
            "from": os.environ.get("EMAIL_FROM"),
            "to": email,
            "subject": report.name,
            "body": str(report),
        }
    )
    if not response.ok:
        return {"message": "Error sending email"}

    # Return a success message
    return {"message": "Email sent successfully"}

import os
import requests
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine, select
from .models import Customers, CustomersActivity, ReportFormat, coupons

# Define the FastAPI app
app = FastAPI()

# Define the database engine and session
engine = create_engine("mysql+mysqlconnector://{user}:{password}@{host}/{database}")
Session = sessionmaker(bind=engine)

# Define the route for sending an email with validation and detection
@app.post("/send_email/", dependencies=[Depends(current_active_user)])
async def send_email(report: ReportFormat, email: str):
    """
    Send an email with validation and detection using the mailboxlayer and isTempEmail APIs.

    implementation of the use case that validates email addresses using MailboxValidator's HTTPS API, detects disposable and temporary email addresses using Disify's HTTPS API, and sends the email
    """
    # Validate the email address with mailboxlayer API
    mailboxlayer_access_key = os.environ.get("MAILBOXLAYER_API_KEY")
    mailboxlayer_response = requests.get(f"http://apilayer.net/api/check?access_key={mailboxlayer_access_key}&email={email}")
    mailboxlayer_data = mailboxlayer_response.json()
    if not mailboxlayer_data["format_valid"] or not mailboxlayer_data["smtp_check"]:
        return {"message": "Invalid email address"}

    # Detect disposable and temporary email addresses with isTempEmail API
    istempemail_response = requests.get(f"https://api.istempemail.com/v1/email/{email}")
    istempemail_data = istempemail_response.json()
    if istempemail_data["is_temporary"] or istempemail_data["is_disposable"]:
        return {"message": "Temporary or disposable email address detected"}

    # Send the email using the API
    response = requests.post(
        os.environ.get("EMAIL_API_URL"),
        headers={"Authorization": f"Bearer {os.environ.get('EMAIL_API_KEY')}"},
        json={
            "from": os.environ.get("EMAIL_FROM"),
            "to": email,
            "subject": report.name,
            "body": str(report),
        }
    )
    if not response.ok:
        return {"message": "Error sending email"}

    # Return a success message
    return {"message": "Email sent successfully"}
