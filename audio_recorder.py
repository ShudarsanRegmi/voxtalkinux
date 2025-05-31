import sounddevice as sd
import numpy as np
import threading
from pathlib import Path
import wave
from typing import Optional
from config_loader import Config

class AudioRecorder:
    def __init__(self):
        self.config = Config()
        self.recording = False
        self.audio_data = []
        self._lock = threading.Lock()

    def _audio_callback(self, indata, frames, time, status):
        """Callback for sounddevice's InputStream"""
        if status:
            print(f"Status: {status}")
        if self.recording:
            with self._lock:
                self.audio_data.append(indata.copy())

    def start_recording(self):
        """Start recording audio from the default microphone"""
        self.recording = True
        self.audio_data = []
        
        # Create input stream
        self.stream = sd.InputStream(
            channels=self.config.audio['channels'],
            samplerate=self.config.audio['sample_rate'],
            callback=self._audio_callback
        )
        self.stream.start()

    def stop_recording(self) -> Optional[str]:
        """Stop recording and save the audio to a WAV file"""
        if not self.recording:
            return None

        self.recording = False
        self.stream.stop()
        self.stream.close()

        if not self.audio_data:
            return None

        # Combine all audio chunks
        with self._lock:
            audio = np.concatenate(self.audio_data, axis=0)

        # Save to temporary WAV file
        temp_path = Path(__file__).parent / "temp_recording.wav"
        with wave.open(str(temp_path), 'wb') as wf:
            wf.setnchannels(self.config.audio['channels'])
            wf.setsampwidth(2)  # 16-bit audio
            wf.setframerate(self.config.audio['sample_rate'])
            wf.writeframes((audio * 32767).astype(np.int16).tobytes())

        return str(temp_path)

    def is_silent(self, audio_chunk, silence_threshold=None):
        """Check if an audio chunk is silent"""
        if silence_threshold is None:
            silence_threshold = self.config.audio['silence_threshold']
        return np.abs(audio_chunk).mean() < silence_threshold 