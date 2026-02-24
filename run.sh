#!/bin/bash

# Navigate to the project root directory
cd "$(dirname "$0")"

echo "========================================="
echo "🚀 Starting SellSmart Platform..."
echo "========================================="

docker compose up -d --build

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
trap "echo -e '\n🛑 Stopping services...'; kill -9 $FRONTEND_PID 2>/dev/null; docker compose stop; exit 0" SIGINT SIGTERM

# Keep script running to wait for Ctrl+C
wait
