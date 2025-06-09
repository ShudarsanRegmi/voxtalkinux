import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk
import os
from pathlib import Path
import math
import threading
import queue

class RecordingVisualizer:
    def __init__(self):
        self.window = None
        self.canvas = None
        self.waveform_points = []
        self.is_recording = False
        self.animation_frame = 0
        self.mic_photo = None
        self.command_queue = queue.Queue()
        
        # Constants for waveform animation
        self.WAVE_WIDTH = 200
        self.WAVE_HEIGHT = 60
        self.WAVE_POINTS = 20
        self.ANIMATION_SPEED = 50  # milliseconds
        
        # Initialize Tkinter in the main thread
        self.root = tk.Tk()
        self.root.withdraw()  # Hide the root window
        
        # Prepare icon path
        self.icon_path = Path(__file__).parent / "assets" / "microphone.png"
        if not self.icon_path.parent.exists():
            os.makedirs(self.icon_path.parent)
            self._create_default_icon(self.icon_path)
        
        # Pre-load the image in main thread
        self._load_mic_image()

    def _create_default_icon(self, icon_path):
        """Create a simple default microphone icon if none exists"""
        img = Image.new('RGBA', (32, 32), (0, 0, 0, 0))
        # Create a simple microphone shape
        from PIL import ImageDraw
        draw = ImageDraw.Draw(img)
        # Draw microphone body
        draw.rectangle([12, 8, 20, 20], fill='black')
        # Draw base
        draw.rectangle([8, 20, 24, 22], fill='black')
        # Draw stand
        draw.rectangle([14, 22, 18, 26], fill='black')
        img.save(icon_path)

    def _load_mic_image(self):
        """Load microphone image when needed"""
        if self.mic_photo is None:
            mic_image = Image.open(self.icon_path)
            mic_image = mic_image.resize((32, 32), Image.Resampling.LANCZOS)
            self.mic_photo = ImageTk.PhotoImage(mic_image)

    def show(self):
        """Queue show command to be executed in main thread"""
        self.command_queue.put(('show', None))

    def hide(self):
        """Queue hide command to be executed in main thread"""
        self.command_queue.put(('hide', None))

    def _show_window(self):
        """Actually show the window (must be called from main thread)"""
        if self.window is None:
            self.window = tk.Toplevel(self.root)
            self.window.title("")
            self.window.overrideredirect(True)  # Remove window decorations
            
            # Keep window on top
            self.window.attributes('-topmost', True)
            
            # Set window size and position
            window_width = 250
            window_height = 150
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Make window semi-transparent
            self.window.attributes('-alpha', 0.9)
            
            # Create main frame
            main_frame = ttk.Frame(self.window)
            main_frame.pack(expand=True, fill='both')
            
            # Add microphone icon
            icon_label = ttk.Label(main_frame, image=self.mic_photo)
            icon_label.pack(pady=10)
            
            # Add canvas for waveform
            self.canvas = tk.Canvas(main_frame, width=self.WAVE_WIDTH, 
                                  height=self.WAVE_HEIGHT, bg='white',
                                  highlightthickness=0)
            self.canvas.pack(pady=5)
            
            # Initialize waveform points
            self._init_waveform()
            
            # Start animation
            self.is_recording = True
            self._animate_waveform()

    def _hide_window(self):
        """Actually hide the window (must be called from main thread)"""
        if self.window:
            self.is_recording = False
            self.window.destroy()
            self.window = None
            self.canvas = None

    def _init_waveform(self):
        """Initialize waveform points"""
        x_step = self.WAVE_WIDTH / (self.WAVE_POINTS - 1)
        self.waveform_points = []
        for i in range(self.WAVE_POINTS):
            x = i * x_step
            y = self.WAVE_HEIGHT / 2
            self.waveform_points.append((x, y))

    def _animate_waveform(self):
        """Animate the waveform"""
        if not self.is_recording or not self.canvas:
            return
        
        try:
            # Clear canvas
            self.canvas.delete('all')
            
            # Update points
            amplitude = 20
            frequency = 2
            phase = self.animation_frame * 0.2
            
            for i in range(len(self.waveform_points)):
                x = self.waveform_points[i][0]
                # Create a smooth wave pattern
                y = (self.WAVE_HEIGHT / 2) + amplitude * math.sin(
                    frequency * (x / self.WAVE_WIDTH) * math.pi + phase
                )
                self.waveform_points[i] = (x, y)
            
            # Draw waveform
            points = []
            for x, y in self.waveform_points:
                points.extend([x, y])
            
            # Draw smooth curve
            if len(points) >= 4:
                self.canvas.create_line(points, smooth=True, fill='#2196F3', width=2)
            
            self.animation_frame += 1
            
            if self.is_recording:
                self.window.after(self.ANIMATION_SPEED, self._animate_waveform)
        except tk.TclError:
            # Window was closed
            pass

    def process_commands(self):
        """Process any pending commands in the queue"""
        try:
            while True:
                command, args = self.command_queue.get_nowait()
                if command == 'show':
                    self._show_window()
                elif command == 'hide':
                    self._hide_window()
        except queue.Empty:
            pass
        
        # Update the root window
        try:
            self.root.update()
        except tk.TclError:
            # Window was closed
            pass 