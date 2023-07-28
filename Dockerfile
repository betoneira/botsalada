# Use the official Python base image
FROM python:3.10-slim-buster

# Set environment variables for Telethon and FFmpeg
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

# Install required system packages for Telethon and FFmpeg
RUN apt-get update && apt-get install -y ffmpeg curl

# Create and set the working directory in the container
WORKDIR /app

# Copy the Python code and the bot_token.json file to the working directory
COPY your_python_code.py /app/

# Install the required Python packages
RUN pip install python-telegram-bot==13.15 telethon telebot pytz tzlocal

# Run the Python script
CMD ["python", "your_python_code.py"]
