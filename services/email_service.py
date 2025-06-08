import smtplib
from email.message import EmailMessage
import logging
from config import settings

def send_contact_email(name: str, email: str, whatsapp: str, message_body: str):
    try:
        logging.info("Preparing to send contact email...")
        logging.info(f"Name: {name}")
        logging.info(f"Email: {email}")
        logging.info(f"WhatsApp: {whatsapp}")
        logging.info(f"SMTP_SERVER: {settings.SMTP_SERVER}")
        logging.info(f"SMTP_PORT: {settings.SMTP_PORT}")
        logging.info(f"SMTP_USERNAME: {settings.SMTP_USERNAME}")
        logging.info(f"ADMIN_EMAIL: {settings.ADMIN_EMAIL}")

        msg = EmailMessage()
        msg["Subject"] = f"New Contact Form Submission from {name}"
        msg["From"] = 'Nomadroof <no-reply@nomadroof.com>'
        msg["To"] = settings.ADMIN_EMAIL

        msg.set_content(
            f"""New contact form submitted:\n\nName: {name}\nEmail: {email}\nWhatsApp: {whatsapp}\nMessage:\n{message_body}"""
        )

        logging.info("Connecting using SMTP_SSL...")

        with smtplib.SMTP_SSL(settings.SMTP_SERVER, settings.SMTP_PORT, timeout=10) as smtp:
            smtp.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            smtp.send_message(msg)
            logging.info("✅ Email sent successfully.")

    except Exception as e:
        logging.error(f"❌ Failed to send email: {e}")
        raise Exception("An error ocurred trying to send this message.")
