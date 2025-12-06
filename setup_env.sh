#!/bin/bash

# setup_env.sh
# Installs dependencies for the media restoration pipeline

echo "--- Checking System Dependencies ---"

# Check for FFmpeg
if ! command -v ffmpeg &>/dev/null; then
  echo "FFmpeg not found. Installing..."
  sudo dnf update && sudo dnf install -y ffmpeg python3-pip
else
  echo "✅ FFmpeg is installed."
fi

echo "--- Setting up Python Environment for Whisper ---"

# Create a virtual environment to avoid system conflicts
if [ ! -d "venv" ]; then
  python3 -m venv venv
fi

# Activate environment and install OpenAI Whisper
source venv/bin/activate
pip install -U -r requirements.txt

echo "✅ Installation Complete."
echo "You can now run ./process_batch.sh"
