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

# Expose port 5000 (though Render ignores this and uses PORT)
EXPOSE 5000

# Define environment variable
ENV FLASK_APP=wsgi.py
ENV FLASK_ENV=production

# Run gunicorn, binding to the PORT environment variable provided by Render, or 5000 by default.
# Using shell form (no brackets) to allow variable expansion.
CMD gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} wsgi:app
