import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import re
import socket
import base64
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
import os

# SendGrid configuration from environment variables
SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY", "your-sendgrid-api-key-here")
SENDER_EMAIL = os.getenv("SENDER_EMAIL", "your-email@example.com")

def send_report_email(recipient_email, csv_data, chart1_path, chart2_path):
    """Send email using SendGrid API"""
    try:
        # Verify chart files exist
        if not os.path.exists(chart1_path):
            return False, f"Chart file not found: {chart1_path}"
        if not os.path.exists(chart2_path):
            return False, f"Chart file not found: {chart2_path}"
        
        # Read chart images
        with open(chart1_path, 'rb') as f:
            chart1_data = base64.b64encode(f.read()).decode()
        with open(chart2_path, 'rb') as f:
            chart2_data = base64.b64encode(f.read()).decode()
        
        # Create message
        message = Mail(
            from_email=SENDER_EMAIL,
            to_emails=recipient_email,
            subject='Amazon Review Analysis Report',
            html_content='<p>Hello,</p><p>Please find attached your Amazon Review Analysis Report with charts.</p><p>Best regards,<br>Amazon Review Analyzer</p>'
        )
        
        # Attach CSV - FIXED: Use add_attachment() instead of assignment
        csv_attachment = Attachment(
            FileContent(base64.b64encode(csv_data).decode()),
            FileName('review_report.csv'),
            FileType('text/csv'),
            Disposition('attachment')
        )
        message.add_attachment(csv_attachment)
        
        # Attach charts
        chart1_attachment = Attachment(
            FileContent(chart1_data),
            FileName('category_chart.png'),
            FileType('image/png'),
            Disposition('attachment')
        )
        message.add_attachment(chart1_attachment)
        
        chart2_attachment = Attachment(
            FileContent(chart2_data),
            FileName('score_chart.png'),
            FileType('image/png'),
            Disposition('attachment')
        )
        message.add_attachment(chart2_attachment)
        
        # Send email
        sg = SendGridAPIClient(SENDGRID_API_KEY)
        response = sg.send(message)
        
        print(f"SendGrid Response: Status {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")
        
        if response.status_code in [200, 202]:
            return True, "Email sent successfully"
        else:
            return False, f"SendGrid returned status code: {response.status_code}"
    
    except FileNotFoundError as e:
        return False, f"File not found: {str(e)}"
    except Exception as e:
        return False, f"Error: {str(e)}"

def validate_email(email):
    """Validate email format"""
    return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email) is not None