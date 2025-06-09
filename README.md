# VoxTalkinux

VoxTalkinux is a voice transcription tool for Linux that allows you to transcribe speech to text in real-time and automatically type or copy the transcribed text. It features a sleek visualization window that provides visual feedback during recording.

## Demo
  ![image](https://github.com/user-attachments/assets/84b9dcfc-6c7f-47d3-b137-c280ee399a96)

 [Demo Video](./demo/demo.mp4)

## Features

- 🎙️ Real-time voice transcription
- ⌨️ Automatic typing of transcribed text
- 📋 Clipboard support as fallback
- 🎯 Global hotkey support (default: Ctrl+Alt+Space)
- 📊 Visual feedback with animated waveform
- 🔧 Configurable settings
- 🎨 Modern, minimalist UI

## Requirements

- Linux operating system
- Python 3.8 or higher
- PortAudio (for audio recording)
- X11 environment
- notify-send (for notifications)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/voxtalkinux.git
cd voxtalkinux
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

The installation script will:
- Create a virtual environment
- Install required Python packages
- Set up necessary system dependencies
- Configure the application
- Register and enable the service to start automatically on system boot

## Usage

The application runs automatically as a background service after installation and system restart. You don't need to manually start it.

1. Press `Ctrl+Space` to start recording (default hotkey)
2. Speak clearly into your microphone
3. Press `Ctrl+Space` again to stop recording
4. The transcribed text will be automatically typed or copied to clipboard

To check the service status, you can use:
```bash
systemctl --user status voxtalkinux
```

## Configuration

The configuration file is located at `~/.config/voxtalkinux/config.yaml`. You can customize:

- Hotkey combinations
- Output method (type/clipboard/auto)
- Typing speed and behavior
- Notification preferences
- Audio settings

Example configuration:
```yaml
hotkey:
  modifiers: ['ctrl', 'alt'] # modifiers: ['ctrl'] if you want ctrl + space
  key: 'space'

whisper:
  model_size: 'base'  # options: tiny, base, small, medium, large

output:
  type: 'auto'  # 'type', 'clipboard', or 'auto'
  notify: true
  typing:
    delay_between_chars: 0.001
    add_trailing_space: true
    retry_count: 3
```

## Troubleshooting

1. **No audio input detected**
   - Check if your microphone is properly connected
   - Verify microphone permissions
   - Run `pavucontrol` to check audio levels

2. **Typing not working**
   - Ensure you have proper accessibility permissions
   - Try increasing the `delay_between_chars` in config
   - Switch to clipboard mode temporarily

3. **Notifications not showing**
   - Verify `notify-send` is installed
   - Check if your desktop environment supports notifications

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- OpenAI Whisper for speech recognition
- The Python community for excellent libraries
- Contributors and users for feedback and suggestions 
