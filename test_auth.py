import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Test Email Settings
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
EMAIL_ADDRESS = "srivastava.vaibha@dalmiabharat.com"  # Replace with your Outlook email
APP_PASSWORD = "vylwscmnzwtvqhhf"  # Replace with your App Password


def send_test_email():
    try:
        # Set up the email
        subject = "Test Email"
        body = "Hello! This is a test email using an App Password."

        msg = MIMEMultipart()
        msg["From"] = EMAIL_ADDRESS
        msg["To"] = "das.rajesh@dalmiabharat.com"  # Replace with recipient email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        # Connect to the SMTP server
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Start TLS encryption
        server.login(EMAIL_ADDRESS, APP_PASSWORD)  # Login with App Password

        # Send the email
        server.send_message(msg)
        print("Test email sent successfully!")
        server.quit()
    except Exception as e:
        print("Error sending email:", e)


# Run the test
send_test_email()
