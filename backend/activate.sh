#!/bin/bash
# Activation script for the semiconductor reliability calculator app

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "Virtual environment activated and dependencies installed!"
echo "To run the app:"
echo "  python -m app.main"
echo ""
echo "To deactivate the virtual environment when done:"
echo "  deactivate"