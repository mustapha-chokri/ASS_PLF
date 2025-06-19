import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from flask import current_app

def send_email(subject, message):
    """إرسال بريد إلكتروني"""
    try:
        msg = MIMEMultipart()
        msg['From'] = current_app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = current_app.config['MAIL_RECIPIENTS']
        msg['Subject'] = subject
        
        msg.attach(MIMEText(message, 'plain'))
        
        server = smtplib.SMTP(current_app.config['MAIL_SERVER'], current_app.config['MAIL_PORT'])
        server.starttls()
        server.login(current_app.config['MAIL_USERNAME'], current_app.config['MAIL_PASSWORD'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending email: {str(e)}")
        return False

def send_whatsapp(message):
    """إرسال رسالة واتساب"""
    try:
        # يمكنك استخدام خدمة مثل Twilio أو WhatsApp Business API
        # هذا مثال باستخدام Twilio
        account_sid = current_app.config['TWILIO_ACCOUNT_SID']
        auth_token = current_app.config['TWILIO_AUTH_TOKEN']
        from_number = current_app.config['TWILIO_WHATSAPP_NUMBER']
        to_number = current_app.config['WHATSAPP_RECIPIENT']
        
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=message,
            from_=f'whatsapp:{from_number}',
            to=f'whatsapp:{to_number}'
        )
        return True
    except Exception as e:
        current_app.logger.error(f"Error sending WhatsApp message: {str(e)}")
        return False