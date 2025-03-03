import pandas as pd
import numpy as np
from slack_sdk import WebClient
import smtplib
from email.mime.text import MIMEText

def detect_anomalies(df):
    anomalies = {
        'missing_values': {},
        'duplicate_rows': 0
    }

    # Check for missing values in text and title columns
    missing_values = df[['title', 'text']].isnull().sum().to_dict()
    anomalies['missing_values'] = {k: v for k, v in missing_values.items() if v > 0}

    # Check for duplicate rows (excluding the 'images' column)
    columns_to_check = [col for col in df.columns if col != 'images']
    duplicate_rows = df.duplicated(subset=columns_to_check, keep='first').sum()
    anomalies['duplicate_rows'] = duplicate_rows

    return anomalies

# def send_slack_alert(message):
#     slack_token = 'YOUR_SLACK_TOKEN'
#     client = WebClient(token=slack_token)
#     client.chat_postMessage(channel='#anomaly-alerts', text=message)

def send_email_alert(subject, body):
    sender = 'ram903055@gmail.com'
    recipients = ['basakran.ra@northeastern.edu']
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)

    smtp_server = 'smtp.gmail.com'
    smtp_port = 587
    smtp_username = 'ram903055@gmail.com'
    smtp_password = 'Raghuram@20000'

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(sender, recipients, msg.as_string())

def process_data_pipeline():
    # Load your data
    data = {
        'rating': 5.0,
        'title': 'Such a lovely scent but not overpowering.',
        'text': "This spray is really nice. It smells really good, goes on really fine, and does the trick. I will say it feels like you need a lot of it though to get the texture I want. I have a lot of hair, medium thickness. I am comparing to other brands with yucky chemicals so I'm gonna stick with this. Try it!",
        'images': [],
        'asin': 'B00YQ6X8EO',
        'parent_asin': 'B00YQ6X8EO',
        'user_id': 'AGKHLEW2SOWHNMFQIJGBECAF7INQ',
        'timestamp': 1588687728923,
        'helpful_vote': 0,
        'verified_purchase': True
    }
    
    # Create a DataFrame with multiple rows (including a duplicate) for demonstration
    df = pd.DataFrame([data, data, {**data, 'title': None}])
    print(df)
    # Detect anomalies
    anomalies = detect_anomalies(df)

    # Check for anomalies and trigger alerts
    if any(anomalies.values()):
        alert_message = "Data anomalies detected:\n"
        for anomaly_type, details in anomalies.items():
            if details:
                alert_message += f"\n{anomaly_type.capitalize()}:\n"
                alert_message += str(details)

        print(alert_message)  # Print to console for demonstration

        # Send Slack alert
        # send_slack_alert(alert_message)

        # Send email alert
        send_email_alert("Data Anomalies Detected", alert_message)
    else:
        print("No anomalies detected.")

if __name__ == "__main__":
    process_data_pipeline()
