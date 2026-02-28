#!/bin/bash

echo "================================================="
echo "       STARTING UPSC SAGA: RAGNAROK EDITION"
echo "================================================="

# Start backend in the background
echo "Starting Backend (Flask)..."
cd backend
nohup python3 app.py > ../backend_log.txt 2>&1 &
BACKEND_PID=$!
cd ..

# Start frontend in the background
echo "Starting Frontend (Vite)..."
cd frontend
nohup npm run dev > ../frontend_log.txt 2>&1 &
FRONTEND_PID=$!
cd ..

echo "Both realms are opening in the background..."
echo "Backend PID: $BACKEND_PID"
echo "Frontend PID: $FRONTEND_PID"
echo "To stop them later, run: kill $BACKEND_PID $FRONTEND_PID"
