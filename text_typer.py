import pyautogui
import time
from config_loader import Config

class TextTyper:
    def __init__(self):
        self.config = Config()
        # Ensure PyAutoGUI fails safe
        pyautogui.FAILSAFE = True
        # No pause between actions
        pyautogui.PAUSE = 0

    def type_text(self, text: str):
        """
        Type the given text at the current cursor position
        
        Args:
            text: The text to type
        """
        if not text:
            return

        # Get typing configuration
        delay = self.config.typing['delay_between_chars']
        add_space = self.config.typing['add_trailing_space']

        # Type the text character by character
        for char in text:
            pyautogui.write(char, interval=delay)

        # Add trailing space if configured
        if add_space:
            pyautogui.write(' ', interval=delay) 