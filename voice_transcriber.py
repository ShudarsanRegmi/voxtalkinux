#!/usr/bin/env python3

import os
import sys
import signal
from pathlib import Path
from pynput import keyboard
from config_loader import Config
from audio_recorder import AudioRecorder
from transcriber import Transcriber
from text_typer import TextTyper

class VoiceTranscriber:
    def __init__(self):
        self.config = Config()
        self.recorder = AudioRecorder()
        self.transcriber = Transcriber()
        self.typer = TextTyper()
        self.is_recording = False
        self._setup_hotkey()

    def _setup_hotkey(self):
        """Set up the global hotkey listener"""
        hotkey = self.config.hotkey
        modifiers = set(getattr(keyboard.Key, mod) if hasattr(keyboard.Key, mod) else 
                       keyboard.KeyCode.from_char(mod) for mod in hotkey['modifiers'])
        key = (getattr(keyboard.Key, hotkey['key']) if hasattr(keyboard.Key, hotkey['key']) 
               else keyboard.KeyCode.from_char(hotkey['key']))
        
        self.current_keys = set()
        
        def on_press(k):
            self.current_keys.add(k)
            if all(k in self.current_keys for k in modifiers) and key in self.current_keys:
                self.toggle_recording()

        def on_release(k):
            try:
                self.current_keys.remove(k)
            except KeyError:
                pass

        self.listener = keyboard.Listener(on_press=on_press, on_release=on_release)

    def toggle_recording(self):
        """Toggle recording state"""
        if not self.is_recording:
            print("Starting recording...")
            self.recorder.start_recording()
            self.is_recording = True
        else:
            print("Stopping recording...")
            audio_file = self.recorder.stop_recording()
            self.is_recording = False
            
            if audio_file:
                print("Transcribing...")
                text = self.transcriber.transcribe(audio_file)
                print(f"Transcribed text: {text}")
                
                print("Typing text...")
                self.typer.type_text(text)
                
                # Clean up temporary audio file
                try:
                    Path(audio_file).unlink()
                except Exception as e:
                    print(f"Warning: Could not delete temporary file: {e}")

    def run(self):
        """Start the voice transcriber service"""
        print("Starting Voice Transcriber...")
        print(f"Press {' + '.join(self.config.hotkey['modifiers'])} + {self.config.hotkey['key']} to toggle recording")
        
        # Handle graceful shutdown
        def signal_handler(signum, frame):
            print("\nShutting down...")
            if self.is_recording:
                self.recorder.stop_recording()
            self.listener.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start the hotkey listener
        self.listener.start()
        self.listener.join()

if __name__ == "__main__":
    transcriber = VoiceTranscriber()
    transcriber.run() 