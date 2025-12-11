# Build Frontend
FROM node:18-alpine as frontend_build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Build Backend
FROM python:3.10-slim
WORKDIR /app/backend

# Install system dependencies if needed (e.g. for sqlite)
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn

COPY backend/ .
COPY --from=frontend_build /app/frontend/dist ../frontend/dist

# Expose port
EXPOSE 5000

# Run
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]
