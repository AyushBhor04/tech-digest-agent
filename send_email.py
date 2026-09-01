import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

from compose_email import build_digest_html
from db import mark_articles_as_sent

load_dotenv()  # reads .env file into environment variables

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587


def send_digest_email(html_content, subject="Your Tech Digest"):
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = GMAIL_ADDRESS  # sending to yourself

    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()  # upgrade connection to encrypted TLS
        server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
        server.send_message(msg)


def send_pending_digest():
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        print("Missing GMAIL_ADDRESS or GMAIL_APP_PASSWORD in .env file. Aborting.")
        return

    html_content, article_ids = build_digest_html()

    if html_content is None:
        print("No unsent articles — nothing to send.")
        return

    print(f"Sending digest with {len(article_ids)} articles...")
    try:
        send_digest_email(html_content)
        print("Email sent successfully.")
        mark_articles_as_sent(article_ids)
        print(f"Marked {len(article_ids)} articles as sent.")
    except smtplib.SMTPAuthenticationError:
        print("Authentication failed — check your Gmail address and App Password in .env.")
    except Exception as e:
        print(f"Failed to send email: {e}")


if __name__ == "__main__":
    send_pending_digest()