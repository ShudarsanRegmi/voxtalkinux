#!/bin/bash

# Exit on any error
set -e

echo "🔧 Starting installation of Voice Transcriber..."

# Define install directory
INSTALL_DIR="$HOME/.local/share/voice-transcriber"
echo "📁 Creating install directory at: $INSTALL_DIR"
mkdir -p "$INSTALL_DIR"

# Copy all project files to install directory
echo "📂 Copying project files to installation directory..."
cp -r ./* "$INSTALL_DIR/"

# Navigate into the install directory
cd "$INSTALL_DIR"

# Create a Python virtual environment
echo "🐍 Creating Python virtual environment..."
python3 -m venv venv

# Activate the virtual environment
echo "✅ Activating virtual environment..."
source venv/bin/activate

# Install dependencies using pip
echo "📦 Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

# Create systemd user service directory if it doesn't exist
SYSTEMD_DIR="$HOME/.config/systemd/user"
echo "🛠️  Creating systemd service directory at: $SYSTEMD_DIR"
mkdir -p "$SYSTEMD_DIR"

# Copy the systemd service file
echo "📄 Installing systemd service file..."
cp voice-transcriber.service "$SYSTEMD_DIR/"

# Reload systemd to recognize the new service
echo "🔄 Reloading systemd user daemon..."
systemctl --user daemon-reload

# Enable and start the voice transcriber service
echo "🚀 Enabling and starting the Voice Transcriber service..."
systemctl --user enable voice-transcriber
systemctl --user start voice-transcriber

# Final instructions
echo "✅ Installation complete!"
echo "🎤 The voice transcriber service is now running in the background."
echo "🛠️  Use Ctrl+Space to start/stop recording."
echo "📊 Check service status: systemctl --user status voice-transcriber"
echo "🛑 Stop the service: systemctl --user stop voice-transcriber"
echo "▶️  Start the service: systemctl --user start voice-transcriber"
