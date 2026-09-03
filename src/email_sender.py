import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from dotenv import load_dotenv


load_dotenv()

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")
DIGEST_TO = os.getenv("DIGEST_TO")


def send_email(subject, html_content):
    """
    Send an HTML email using Gmail SMTP.
    """

    message = MIMEMultipart("alternative")

    message["From"] = GMAIL_ADDRESS
    message["To"] = DIGEST_TO
    message["Subject"] = subject

    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()

            server.login(
                GMAIL_ADDRESS,
                GMAIL_APP_PASSWORD,
            )

            server.sendmail(
                GMAIL_ADDRESS,
                DIGEST_TO,
                message.as_string(),
            )

        print("Email sent successfully!")

    except Exception as e:
        print(f"[ERROR] Failed to send email: {e}")


if __name__ == "__main__":
    send_email(
        "Tech Digest - Test Email",
        """
        <html>
        <body>
            <h1>🎉 Tech Digest Test</h1>

            <p>
                If you received this email, Gmail SMTP is working correctly!
            </p>

        </body>
        </html>
        """,
    )