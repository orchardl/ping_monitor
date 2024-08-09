import os
import subprocess
import smtplib
from datetime import datetime
from email.mime.text import MIMEText

# Configuration
hosts = [
    {"host": "<IP 1>", "threshhold": 50, "name": "<server name 1>"}, 
    {"host": "<IP 2>", "threshhold": 50, "name": "<server name 2>"}, 
    {"host": "<IP 3>", "threshhold": 50, "name": "<server name 3>"}, 
    {"host": "<IP 4>", "threshhold": 50, "name": "<server name 4>"}, 
]
log_file = "/logs/ping_log.txt"  # Use a path that will be mounted to the host
#threshold = 130  # Ping threshold in milliseconds

# Email settings
email_from = "<brevo account email>@gmail.com"
email_to = "<name>@<domain>.com"
smtp_server = "smtp-relay.brevo.com"
smtp_username = "<account>@smtp-brevo.com"
smtp_password = "<smtp pw>"

# AWS Email Settings
aws_from = "<aws email>@<domain>.com"
aws_to = "<phone number>@tmomail.net"
aws_smtp = "email-smtp.us-east-2.amazonaws.com"
aws_smtp_username = "<smtp username>"  # Replace with your SMTP username
aws_smtp_password = "<smtp password>"  # Replace with your SMTP password - remember to run the script to generate this

# Function to send an email alert
def send_alert(name, ping, timeout):
    subject = f"High Ping Alert for {name}"
    body = f"Ping for {name} is {ping}ms, which is above the threshold of {timeout}ms."
    # Send first email
    msg = MIMEText(body)
    msg['From'] = email_from
    msg['To'] = email_to
    msg['Subject'] = subject

    try:
        server = smtplib.SMTP(smtp_server, 587)
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.sendmail(email_from, [email_to], msg.as_string())
        server.quit()
        print(f"Alert sent for {name}")
    except Exception as e:
        print(f"Failed to send alert for {name}: {e}")
    
    # Send second email
    aws_msg = MIMEText(body)
    aws_msg['From'] = aws_from
    aws_msg['To'] = aws_to
    aws_msg['Subject'] = subject

    with smtplib.SMTP(aws_smtp, 587) as server:
        server.starttls()
        server.login(aws_smtp_username, aws_smtp_password)
        server.sendmail(aws_from, [aws_to], aws_msg.as_string())

# Function to ping a host and log the result
def ping_host(host, timeout, name):
    try:
        output = subprocess.check_output(["ping", "-c", "1", "-W", str(timeout), host], universal_newlines=True)
        # Extract the time as a floating-point number
        time_str = output.split("time=")[-1].split(" ")[0]
        time = float(time_str)
        # Convert to milliseconds
        time_ms = int(time)
        log_entry = f"{datetime.now()} - {host} - {time_ms}ms\n"
    except subprocess.CalledProcessError:
        log_entry = f"{datetime.now()} - {host} - Ping failed\n"
        time_ms = None

    with open(log_file, "a") as log:
        log.write(log_entry)

    if time_ms is not None and time_ms > timeout:
        send_alert(name, time_ms, timeout)

# Main loop to ping all hosts with their respective threshhold
for entry in hosts:
    ping_host(entry["host"], entry["threshhold"], entry["name"])
