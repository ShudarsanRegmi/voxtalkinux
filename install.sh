#!/bin/bash

# Exit on any error
set -e

# Create installation directory
INSTALL_DIR="$HOME/.local/share/voice-transcriber"
mkdir -p "$INSTALL_DIR"

# Copy project files
cp -r ./* "$INSTALL_DIR/"

# Create virtual environment
cd "$INSTALL_DIR"
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create systemd user directory if it doesn't exist
mkdir -p "$HOME/.config/systemd/user"

# Install service file
cp voice-transcriber.service "$HOME/.config/systemd/user/"

# Reload systemd user daemon
systemctl --user daemon-reload

# Enable and start the service
systemctl --user enable voice-transcriber
systemctl --user start voice-transcriber

echo "Installation complete!"
echo "The voice transcriber service is now running in the background."
echo "Use Ctrl+Space to start/stop recording."
echo "To check service status: systemctl --user status voice-transcriber"
echo "To stop the service: systemctl --user stop voice-transcriber"
echo "To start the service: systemctl --user start voice-transcriber" 