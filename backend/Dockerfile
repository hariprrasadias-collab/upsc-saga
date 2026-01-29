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
ENV FLASK_APP=app
ENV FLASK_ENV=production

# Run app.py when the container launches
CMD ["/bin/sh", "-c", "exec gunicorn -w 4 -b 0.0.0.0:${PORT:-5000} 'app:create_app()'"]
