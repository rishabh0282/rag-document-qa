#!/usr/bin/env bash
set -euo pipefail

echo "=== RAG Document QA - Full Setup ==="
echo ""

# Create and activate venv
echo "1. Setting up Python virtual environment..."
python -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "2. Installing backend dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install frontend dependencies
echo "3. Installing frontend dependencies..."
cd frontend
npm install
echo "4. Building frontend..."
npm run build
cd ..

# Create .env if not exists
if [ ! -f .env ]; then
  echo "5. Creating .env file from .env.example..."
  cp .env.example .env
  echo "   ??  Update .env with your OPENAI_API_KEY"
fi

echo ""
echo "=== Setup Complete ==="
echo ""
echo "To start the application:"
echo "  source venv/bin/activate"
echo "  uvicorn src.api:app --host 0.0.0.0 --port 8000"
echo ""
echo "Then open: http://localhost:8000"
