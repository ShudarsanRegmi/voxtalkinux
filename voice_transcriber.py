#!/usr/bin/env python3

import os
import sys
import signal
import subprocess
from pathlib import Path
from pynput import keyboard
from config_loader import Config
from audio_recorder import AudioRecorder
from transcriber import Transcriber
from output_handler import OutputHandler
from visualization import RecordingVisualizer
import threading
import time

class VoiceTranscriber:
    def __init__(self):
        print("Initializing Voice Transcriber...")  # Debug
        self.config = Config()
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.output_handler = OutputHandler()
        self.visualizer = RecordingVisualizer()
        self.is_recording = False
        self.running = True
        print("Loading configuration...")  # Debug
        print(f"Hotkey config: {self.config.hotkey}")  # Debug
        self._setup_hotkey()
        # Show startup notification only for initial launch
        self._show_notification("Voice Transcriber Started", "Press Ctrl+Alt+Space to start/stop recording")
        print("Initialization complete!")  # Debug

    def _show_notification(self, title: str, message: str):
        """Show a desktop notification - only used for startup/shutdown"""
        try:
            subprocess.run([
                'notify-send',
                title,
                message,
                '--icon=dialog-information'
            ])
            print(f"Notification sent: {title} - {message}")  # Debug
        except Exception as e:
            print(f"Could not show notification: {e}")

    def _setup_hotkey(self):
        """Set up the global hotkey listener"""
        hotkey = self.config.hotkey
        print(f"Setting up hotkey with config: {hotkey}")  # Debug
        
        # Convert modifier strings to actual Key objects
        modifiers = set()
        for mod in hotkey['modifiers']:
            if hasattr(keyboard.Key, mod):
                modifiers.add(getattr(keyboard.Key, mod))
                print(f"Added modifier: {mod} -> {getattr(keyboard.Key, mod)}")  # Debug
            else:
                key_code = keyboard.KeyCode.from_char(mod)
                modifiers.add(key_code)
                print(f"Added modifier as char: {mod} -> {key_code}")  # Debug

        # Convert key to actual Key object
        if hasattr(keyboard.Key, hotkey['key']):
            key = getattr(keyboard.Key, hotkey['key'])
        else:
            key = keyboard.KeyCode.from_char(hotkey['key'])
        print(f"Target key: {hotkey['key']} -> {key}")  # Debug
        
        self.current_keys = set()
        
        def on_press(k):
            # print(f"Key pressed: {k}")  # Debug
            self.current_keys.add(k)
            # print(f"Current keys held: {self.current_keys}")  # Debug
            # print(f"Looking for modifiers: {modifiers} and key: {key}")  # Debug
            if all(m in self.current_keys for m in modifiers) and key in self.current_keys:
                print("Hotkey combination detected!")  # Debug
                self.toggle_recording()

        def on_release(k):
            try:
                self.current_keys.remove(k)
                # print(f"Key released: {k}")  # Debug
                # print(f"Current keys held: {self.current_keys}")  # Debug
            except KeyError:
                pass

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    def toggle_recording(self):
        """Toggle recording state"""
        if not self.is_recording:
            print("Starting recording...")
            self.visualizer.show()  # Show visualization window
            self.visualizer.set_message("Speak now...")
            self.recorder.start_recording()
            self.is_recording = True
        else:
            print("Stopping recording...")
            self.visualizer.set_message("Processing speech...")
            audio_file = self.recorder.stop_recording()
            self.is_recording = False
            
            if audio_file:
                print("Transcribing...")
                self.visualizer.set_message("Transcribing...")
                text = self.transcriber.transcribe(audio_file)
                print(f"Transcribed text: {text}")
                
                print("Processing output...")
                self.visualizer.set_message("Typing text...")
                success = self.output_handler.output_text(text)
                
                # Clean up temporary audio file
                try:
                    Path(audio_file).unlink()
                except Exception as e:
                    print(f"Warning: Could not delete temporary file: {e}")
                
                # Hide visualization after a short delay
                time.sleep(0.5)
                self.visualizer.hide()

    def run(self):
        """Start the voice transcriber service"""
        print("Starting Voice Transcriber...")
        print(f"Press {' + '.join(self.config.hotkey['modifiers'])} + {self.config.hotkey['key']} to toggle recording")
        
        # Handle graceful shutdown
        def signal_handler(signum, frame):
            print("\nShutting down...")
            self.running = False
            if self.is_recording:
                self.recorder.stop_recording()
            self.listener.stop()
            self._show_notification("Voice Transcriber", "Service stopped")
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the hotkey listener in a separate thread
        self.listener.start()
        
        # Main event loop - process visualization commands and update GUI
        try:
            while self.running:
                # Process any pending visualization commands
                self.visualizer.process_commands()
                # Small sleep to prevent high CPU usage
                time.sleep(0.01)
        except KeyboardInterrupt:
            signal_handler(None, None)
        finally:
            self.listener.stop()
            self.listener.join()

if __name__ == "__main__":
    transcriber = VoiceTranscriber()
    transcriber.run() 