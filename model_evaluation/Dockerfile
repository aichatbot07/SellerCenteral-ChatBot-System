# Base image with Python
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set working directory
WORKDIR /app

# Copy all files into the container
COPY . /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt
# # Set the environment variable for Google Cloud credentials
# ENV GOOGLE_APPLICATION_CREDENTIALS="/app/service_account.json"

# Run all step scripts
CMD ["sh", "-c", "python Pipeline/step_01.py && \
                  python Pipeline/step_02.py && \
                  python Pipeline/step_03.py && \
                  python Pipeline/step_04.py"]

