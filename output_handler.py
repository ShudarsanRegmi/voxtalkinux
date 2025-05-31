import pyperclip
import pyautogui
import subprocess
from config_loader import Config
from typing import Optional

class OutputHandler:
    def __init__(self):
        self.config = Config()
        # Ensure PyAutoGUI fails safe
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0

    def _show_notification(self, message: str):
        """Show a desktop notification"""
        try:
            subprocess.run([
                'notify-send',
                'Voice Transcriber',
                message,
                '--icon=dialog-information'
            ])
        except Exception:
            # Fail silently if notifications aren't available
            pass

    def _try_typing(self, text: str) -> bool:
        """Attempt to type the text"""
        if not text:
            return False

        config = self.config.output['typing']
        delay = config['delay_between_chars']
        add_space = config['add_trailing_space']
        retry_count = config['retry_count']

        for attempt in range(retry_count):
            try:
                # Type the text character by character
                for char in text:
                    pyautogui.write(char, interval=delay)

                # Add trailing space if configured
                if add_space:
                    pyautogui.write(' ', interval=delay)
                return True
            except Exception as e:
                print(f"Typing attempt {attempt + 1} failed: {e}")
                if attempt == retry_count - 1:
                    return False

    def _copy_to_clipboard(self, text: str) -> bool:
        """Copy the text to clipboard"""
        try:
            pyperclip.copy(text)
            return True
        except Exception as e:
            print(f"Failed to copy to clipboard: {e}")
            return False

    def output_text(self, text: str) -> bool:
        """
        Output the text according to configuration
        Returns True if successful, False otherwise
        """
        if not text:
            return False

        output_type = self.config.output['type']
        notify = self.config.output['notify']

        success = False
        message = ""

        if output_type in ['type', 'auto']:
            success = self._try_typing(text)
            if success:
                message = "Text typed successfully"
            elif output_type == 'auto':
                # Fall back to clipboard
                success = self._copy_to_clipboard(text)
                message = "Text copied to clipboard (typing failed)"
        
        if output_type == 'clipboard' or (output_type == 'auto' and not success):
            success = self._copy_to_clipboard(text)
            message = "Text copied to clipboard"

        if notify and message:
            self._show_notification(message)

        return success 