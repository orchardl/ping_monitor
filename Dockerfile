# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Install cron and ping utility
RUN apt-get update && \
    apt-get install -y cron iputils-ping dnsutils && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /usr/src/app

# Copy the Python script into the container
COPY ping_monitor.py .

# Install any needed packages specified in requirements.txt (if you have any)
# RUN pip install --no-cache-dir -r requirements.txt

# Create a directory for logs
RUN mkdir -p /logs

# Add the cron job directly into the crontab
RUN echo "*/2 * * * * /usr/local/bin/python /usr/src/app/ping_monitor.py >> /var/log/cron.log 2>&1" > /etc/cron.d/ping_cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/ping_cron

# Apply the cron job
RUN crontab /etc/cron.d/ping_cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the cron and the python script
CMD cron && tail -f /var/log/cron.log
