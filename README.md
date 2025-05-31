# Voice Transcriber

A lightweight, offline voice transcription tool for Ubuntu that runs in the background and transcribes speech to text using OpenAI's Whisper model.

## Features

- Global hotkey activation (default: Ctrl + Alt + Space)
- Local offline transcription using Whisper
- Automatic text input after transcription
- Configurable settings (hotkey, model size, audio parameters)
- Runs as a background service
- Completely offline - no cloud APIs required

## Requirements

- Python 3.8 or higher
- Ubuntu Linux (or other Linux distributions)
- PortAudio (for audio recording)
- FFmpeg (for audio processing)

## Installation

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install python3-pip python3-venv portaudio19-dev ffmpeg
```

2. Clone the repository and set up a virtual environment:
```bash
git clone <repository-url>
cd voice-transcriber
python3 -m venv venv
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Activate the virtual environment if not already active:
```bash
source venv/bin/activate
```

2. Run the transcriber:
```bash
python voice_transcriber.py
```

3. Use the hotkey (default: Ctrl + Alt + Space) to start/stop recording. The transcribed text will be automatically typed at your cursor position.

## Configuration

Edit `config.yaml` to customize:

- Hotkey combination
- Whisper model size (tiny, base, small, medium, large)
- Audio recording parameters
- Typing behavior

Example configuration:
```yaml
hotkey:
  modifiers: ['ctrl', 'alt']
  key: 'space'

whisper:
  model_size: 'tiny'  # Change to 'base', 'small', 'medium', or 'large' for better accuracy
```

## Running as a System Service

To run the transcriber as a system service on startup:

1. Create a systemd service file:
```bash
sudo nano /etc/systemd/system/voice-transcriber.service
```

2. Add the following content (adjust paths as needed):
```ini
[Unit]
Description=Voice Transcriber Service
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
Environment=DISPLAY=:0
Environment=XAUTHORITY=/home/YOUR_USERNAME/.Xauthority
WorkingDirectory=/path/to/voice-transcriber
ExecStart=/path/to/voice-transcriber/venv/bin/python voice_transcriber.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Enable and start the service:
```bash
sudo systemctl enable voice-transcriber
sudo systemctl start voice-transcriber
```

## Troubleshooting

1. If you get PortAudio errors:
   - Ensure portaudio19-dev is installed
   - Check your microphone permissions

2. If the hotkey doesn't work:
   - Ensure no other application is using the same hotkey
   - Try running with sudo for global hotkey access

3. If transcription is slow:
   - Consider using a smaller Whisper model
   - Ensure you have sufficient CPU power

## License

MIT License 