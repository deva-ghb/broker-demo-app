#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")"

echo "========================================="
echo "🚀 Starting SellSmart Platform..."
echo "========================================="

echo "1️⃣ Starting Docker Infrastructure (MongoDB & Qdrant)..."
docker-compose up -d mongodb qdrant

echo "2️⃣ Preparing Backend (Clearing port 8000)..."
# Stop trailing Docker containers that might be hogging the port
docker-compose stop api 2>/dev/null || true
docker-compose rm -f api 2>/dev/null || true

# Silently kill any local process stuck on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

echo "3️⃣ Starting Backend Server..."
# Run FastAPI via the local v-env (no conda required)
./v-env/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

echo "4️⃣ Starting Frontend Server..."
cd webapp
npm install > /dev/null 2>&1 # Ensure deps are installed quietly
npm run dev &
FRONTEND_PID=$!
cd ..

echo "========================================="
echo "✅ All systems are running!"
echo "📡 Backend: http://localhost:8000"
echo "🖥️  Frontend: http://localhost:5173 (or 5174 if busy)"
echo "========================================="
echo "Press [Ctrl+C] to gracefully stop all services."

# Trap Ctrl+C (SIGINT) and stop processes cleanly
trap "echo -e '\n🛑 Stopping services...'; kill -9 $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit 0" SIGINT SIGTERM

# Keep script running to wait for Ctrl+C
wait
