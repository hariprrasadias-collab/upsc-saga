#!/bin/bash

echo "================================================="
echo "       STARTING UPSC SAGA + OPENCLAW"
echo "================================================="

# Start OpenClaw Docker containers
echo "Starting OpenClaw Docker containers..."
docker start openclaw-openclaw-gateway-1 || echo "Warning: Could not start openclaw-openclaw-gateway-1"
docker start openclaw-openclaw-cli-1 || echo "Warning: Could not start openclaw-openclaw-cli-1"

# Start Backend
echo "Starting Backend (Flask)..."
cd backend
nohup python3 app.py > ../backend_log.txt 2>&1 &
BACKEND_PID=$!
cd ..

# Start Frontend
echo "Starting Frontend (Vite)..."
cd frontend
nohup npm run dev > ../frontend_log.txt 2>&1 &
FRONTEND_PID=$!
cd ..

echo "Everything is started in the background!"
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "To stop backend & frontend, run: kill $BACKEND_PID $FRONTEND_PID"
echo "To stop openclaw docker containers, run: docker stop openclaw-openclaw-gateway-1 openclaw-openclaw-cli-1"
