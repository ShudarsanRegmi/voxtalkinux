import whisper
from pathlib import Path
from config_loader import Config

class Transcriber:
    def __init__(self):
        self.config = Config()
        self._model = None
        self._model_size = None
        self._load_model()

    def _load_model(self):
        """Load or reload the Whisper model if needed"""
        model_size = self.config.whisper['model_size']
        if self._model is None or self._model_size != model_size:
            self._model = whisper.load_model(model_size)
            self._model_size = model_size

    def transcribe(self, audio_file: str) -> str:
        """
        Transcribe the given audio file to text
        
        Args:
            audio_file: Path to the audio file to transcribe
            
        Returns:
            Transcribed text
        """
        self._load_model()  # Ensure model is loaded with current config
        
        result = self._model.transcribe(
            audio_file,
            language=self.config.whisper['language'] or None,
            fp16=False  # Use CPU-friendly settings
        )
        
        return result["text"].strip()

    def reload_model(self):
        """Force reload the model (e.g., after config change)"""
        self._model = None
        self._load_model() 