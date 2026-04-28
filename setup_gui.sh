#!/bin/bash
echo "🚀 Setting up Evidence Intelligence GUI..."

# Check for node
if ! command -v node &> /dev/null
then
    echo "❌ Node.js is not installed. Please install it to run the frontend."
    exit
fi

# Install backend deps
echo "📦 Installing backend dependencies..."
./venv/bin/pip install -r web/backend/requirements.txt

# Install frontend deps
echo "📦 Installing frontend dependencies..."
cd web/frontend
npm install

echo "✅ Setup complete!"
echo "To start the system:"
echo "1. Run backend: ./venv/bin/python web/backend/run.py"
echo "2. Run frontend: cd web/frontend && npm run dev"
