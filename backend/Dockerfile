# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory to /app
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    libffi-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . .

# Expose port 5000
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PORT=5000

# Run app.py when the container launches
# 1. Initialize DB (single process)
# 2. Run Gunicorn (skip init, reduce workers for memory safety)
CMD ["sh", "-c", "python3 -c 'from app import create_app; create_app()' && SKIP_DB_INIT=true gunicorn -w 2 -b 0.0.0.0:${PORT} app:create_app()"]
