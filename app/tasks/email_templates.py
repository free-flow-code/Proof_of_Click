from email.message import EmailMessage
from pydantic import EmailStr

from app.config import settings


def create_email_confirmation_template(verification_code: str, email_to: EmailStr):
    email = EmailMessage()
    email["Subject"] = "Verification of email."
    email["From"] = settings.SMTP_USER
    email["To"] = email_to
    verification_link = f"{settings.FRONTEND_DOMAIN}/verify.html?code={verification_code}"

    email.set_content(
        f"""
        <html>
        <body>
        <h3>
            <p>To confirm your registration in the <b>Proof of Click</b> project,
            follow <a href="{verification_link}"><b>this link</b></a>.</p>
            <p>If you have not registered, simply do not reply to this message.</p>
        </h3>
        </body>
        </html>
        """,
        subtype="html"
    )
    return email


def create_restore_password_template(username: str, password: str, email_to: EmailStr):
    email = EmailMessage()
    email["Subject"] = "Restore password."
    email["From"] = settings.SMTP_USER
    email["To"] = email_to

    email.set_content(
        f"""
            <html>
            <body>
            <h3>
                <p>Your account login details:</p>
                <p>username: <b>{username}</b></p>
                <p>password: <b>{password}</b></p>
            </h3>
            </body>
            </html>
            """,
        subtype="html"
    )
    return email
