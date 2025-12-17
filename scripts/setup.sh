#!/usr/bin/env bash
set -euo pipefail
python -m venv venv
# Non-interactive activation and pip install
if [ -f "venv/bin/activate" ]; then
  # Unix
  source venv/bin/activate
else
  echo "Please activate venv manually on your OS"
fi
pip install --upgrade pip
pip install -r requirements.txt
echo "Setup complete."