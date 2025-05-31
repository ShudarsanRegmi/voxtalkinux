import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    _instance = None
    _config = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Config, cls).__new__(cls)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config_path = Path(__file__).parent / 'config.yaml'
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)

    @property
    def hotkey(self) -> Dict[str, Any]:
        return self._config['hotkey']

    @property
    def audio(self) -> Dict[str, Any]:
        return self._config['audio']

    @property
    def whisper(self) -> Dict[str, Any]:
        return self._config['whisper']

    @property
    def output(self) -> Dict[str, Any]:
        return self._config.get('output', {
            'type': 'auto',
            'notify': True,
            'typing': {
                'delay_between_chars': 0.01,
                'add_trailing_space': True,
                'retry_count': 3
            }
        })

    @property
    def typing(self) -> Dict[str, Any]:
        return self.output['typing']

    def reload(self):
        """Reload configuration from file"""
        self._load_config() 