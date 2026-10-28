import smtplib
from email.message import EmailMessage
from datetime import datetime
from getpass import getpass

SMTP_HOST = "smtp.office365.com"
SMTP_PORT = 587


def send_email():
    sender_email = input("Sender email: ").strip()
    sender_password = getpass("SMTP password: ")
    recipient_email = input("Recipient email: ").strip()

    now = datetime.now()

    msg = EmailMessage()
    msg["Subject"] = f"Scheduled notification - {now:%Y-%m-%d %H:%M}"
    msg["From"] = sender_email
    msg["To"] = recipient_email

    msg.set_content(
        f"""Hello,

This is an automatically generated notification email.

Sent at: {now:%Y-%m-%d %H:%M:%S}

Best regards.
"""
    )

    try:
        with smtplib.SMTP(
            SMTP_HOST, SMTP_PORT, timeout=30
        ) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            server.login(sender_email, sender_password)
            server.send_message(msg)

        print(f"\n[+] Email sent successfully at {now}")

    except smtplib.SMTPAuthenticationError:
        print(
            "\n[!] Authentication failed. "
            "Check SMTP AUTH and the authentication method "
            "allowed by Microsoft 365."
        )
    except Exception as e:
        print(f"\n[!] Failed to send email: {e}")


if __name__ == "__main__":
    send_email()
