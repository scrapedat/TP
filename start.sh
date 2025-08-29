#!/bin/bash
# ToolLlama Startup Script
# ========================

echo "🤖 ToolLlama Startup Script"
echo "============================"

# Check if we're in the right directory
if [ ! -d "venv" ]; then
    echo "❌ Error: Virtual environment not found. Please run this from the toollama directory."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
. venv/bin/activate

# Check if Python dependencies are installed
echo "📦 Checking Python dependencies..."
python -c "import fastapi, uvicorn" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "❌ Python dependencies not found. Installing..."
    pip install -r backend/requirements.txt
fi

# Check if npm dependencies are installed
echo "📦 Checking npm dependencies..."
if [ ! -d "node_modules" ]; then
    echo "❌ npm dependencies not found. Installing..."
    npm install
fi

# Install Playwright browsers
echo "🎭 Installing Playwright browsers..."
python -m playwright install chromium

echo ""
echo "🚀 Starting ToolLlama System"
echo "============================"

# Start backend in background
echo "🔧 Starting backend server..."
python backend/main.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start frontend in background
echo "🎨 Starting frontend..."
npm run dev &
FRONTEND_PID=$!

# Wait a moment for frontend to start
sleep 5

echo ""
echo "🎉 ToolLlama Started Successfully!"
echo "=================================="
echo "🌐 Frontend: http://localhost:5173"
echo "🔧 Backend: http://localhost:8000"
echo "📊 Health: http://localhost:8000/health"
echo ""
echo "🧪 Test the system:"
echo "   • Open http://localhost:5173 in your browser"
echo "   • Try the browser control panel"
echo "   • Add custom website presets"
echo ""
echo "🛑 To stop: Press Ctrl+C or run: kill $BACKEND_PID $FRONTEND_PID"

# Wait for user interrupt
trap "echo '🛑 Shutting down...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait