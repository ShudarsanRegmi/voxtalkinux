import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk, ImageDraw
import os
from pathlib import Path
import math
import threading
import queue
import sounddevice as sd

class RecordingVisualizer:
    def __init__(self):
        self.window = None
        self.canvas = None
        self.waveform_points = []
        self.is_recording = False
        self.animation_frame = 0
        self.mic_photo = None
        self.command_queue = queue.Queue()
        self.audio_data = queue.Queue(maxsize=10)
        
        # Constants for waveform animation
        self.WAVE_WIDTH = 160
        self.WAVE_HEIGHT = 40
        self.WAVE_POINTS = 40
        self.ANIMATION_SPEED = 30  # milliseconds
        
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
        
        # Audio input stream
        self.audio_stream = None

    def _create_default_icon(self, icon_path):
        """Create a modern microphone icon"""
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Create a modern microphone shape
        # Main body (rounded rectangle)
        body_width = size // 3
        body_height = size // 2
        body_left = (size - body_width) // 2
        body_top = size // 6
        
        # Draw microphone body with gradient
        for y in range(body_height):
            color = (41, 128, 185, int(255 * (0.8 + 0.2 * (y / body_height))))  # Blue gradient
            draw.rectangle(
                [body_left, body_top + y, body_left + body_width, body_top + y + 1],
                fill=color
            )
        
        # Draw rounded corners
        corner_radius = body_width // 3
        draw.ellipse([body_left, body_top, body_left + corner_radius * 2, body_top + corner_radius * 2],
                    fill=(41, 128, 185, 255))
        draw.ellipse([body_left + body_width - corner_radius * 2, body_top,
                     body_left + body_width, body_top + corner_radius * 2],
                    fill=(41, 128, 185, 255))
        
        # Stand base
        base_width = body_width * 1.5
        base_height = size // 10
        base_left = (size - base_width) // 2
        base_top = body_top + body_height + size // 8
        
        # Draw stand with gradient
        for y in range(base_height):
            alpha = int(255 * (0.7 + 0.3 * (1 - y / base_height)))
            draw.rectangle(
                [base_left, base_top + y, base_left + base_width, base_top + y + 1],
                fill=(41, 128, 185, alpha)
            )
        
        # Stand connector
        connector_width = body_width // 3
        connector_left = (size - connector_width) // 2
        draw.rectangle(
            [connector_left, body_top + body_height,
             connector_left + connector_width, base_top],
            fill=(41, 128, 185, 200)
        )
        
        img.save(icon_path)

    def _load_mic_image(self):
        """Load microphone image when needed"""
        if self.mic_photo is None:
            mic_image = Image.open(self.icon_path)
            mic_image = mic_image.resize((48, 48), Image.Resampling.LANCZOS)
            self.mic_photo = ImageTk.PhotoImage(mic_image)

    def _setup_audio_stream(self):
        """Setup audio input stream for visualization"""
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            if self.is_recording:
                # Calculate audio level (RMS)
                audio_level = np.sqrt(np.mean(indata**2))
                try:
                    self.audio_data.put_nowait(audio_level)
                except queue.Full:
                    pass  # Skip if queue is full

        self.audio_stream = sd.InputStream(
            channels=1,
            samplerate=16000,
            callback=audio_callback
        )
        self.audio_stream.start()

    def _create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        """Draw a rounded rectangle on the canvas"""
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1
        ]
        return canvas.create_polygon(points, smooth=True, **kwargs)

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
            self.window.overrideredirect(True)
            
            # Keep window on top
            self.window.attributes('-topmost', True)
            
            # Set window size and position
            window_width = 200
            window_height = 100
            screen_width = self.window.winfo_screenwidth()
            screen_height = self.window.winfo_screenheight()
            x = (screen_width - window_width) // 2
            y = (screen_height - window_height) // 2
            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            
            # Make window semi-transparent
            self.window.attributes('-alpha', 0.95)
            
            # Configure window background
            self.window.configure(bg='#2c3e50')
            
            # Create main canvas
            self.canvas = tk.Canvas(
                self.window,
                width=window_width,
                height=window_height,
                bg='#2c3e50',
                highlightthickness=0
            )
            self.canvas.pack(fill='both', expand=True)
            
            # Create background with rounded corners
            self._create_rounded_rectangle(
                self.canvas, 2, 2, window_width-2, window_height-2, 20,
                fill='#34495e', outline='#3498db', width=2
            )
            
            # Add microphone icon
            icon_x = window_width // 2
            self.canvas.create_image(icon_x, 15, anchor='n', image=self.mic_photo)
            
            # Initialize waveform
            self._init_waveform()
            
            # Start audio stream
            self._setup_audio_stream()
            
            # Start animation
            self.is_recording = True
            self._animate_waveform()

    def _hide_window(self):
        """Actually hide the window (must be called from main thread)"""
        if self.window:
            self.is_recording = False
            if self.audio_stream:
                self.audio_stream.stop()
                self.audio_stream.close()
                self.audio_stream = None
            self.window.destroy()
            self.window = None
            self.canvas = None

    def _init_waveform(self):
        """Initialize waveform points"""
        self.current_amplitude = 0
        self.target_amplitude = 0

    def _animate_waveform(self):
        """Animate the waveform"""
        if not self.is_recording or not self.canvas:
            return
        
        try:
            # Get latest audio level
            try:
                audio_level = self.audio_data.get_nowait() * 100  # Scale factor for amplitude
                self.target_amplitude = min(30, audio_level)  # Cap maximum amplitude
            except queue.Empty:
                # Slowly reduce target amplitude when no audio
                self.target_amplitude *= 0.95

            # Smooth amplitude transition
            self.current_amplitude = self.current_amplitude * 0.8 + self.target_amplitude * 0.2
            
            # Clear previous waveform
            self.canvas.delete('waveform')
            
            # Calculate points for a simple sine wave
            points = []
            width = self.WAVE_WIDTH
            start_x = (self.window.winfo_width() - width) // 2
            base_y = self.window.winfo_height() - 25
            
            # Create smooth sine wave
            num_points = 50  # Number of points for the wave
            for i in range(num_points):
                x = start_x + (width * i / (num_points - 1))
                # Create sine wave with current amplitude and animation
                phase = self.animation_frame * 0.1
                y = base_y - self.current_amplitude * math.sin(
                    (i / num_points) * math.pi * 2 + phase
                )
                points.extend([x, y])
            
            # Draw main wave
            if len(points) >= 4:
                # Main waveform with glow
                for width, alpha in [(5, 0.3), (3, 0.6), (2, 1.0)]:
                    color = self._adjust_color('#3498db', alpha)
                    self.canvas.create_line(
                        points,
                        smooth=True,
                        fill=color,
                        width=width,
                        tags='waveform',
                        capstyle=tk.ROUND,
                        joinstyle=tk.ROUND
                    )
            
            self.animation_frame += 1
            
            if self.is_recording:
                self.window.after(self.ANIMATION_SPEED, self._animate_waveform)
        except tk.TclError:
            # Window was closed
            pass

    def _adjust_color(self, color, alpha):
        """Adjust color transparency"""
        # Convert hex color to RGB
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        
        # Blend with background color (#2c3e50)
        bg_r, bg_g, bg_b = 44, 62, 80
        r = int(r * alpha + bg_r * (1 - alpha))
        g = int(g * alpha + bg_g * (1 - alpha))
        b = int(b * alpha + bg_b * (1 - alpha))
        
        return f'#{r:02x}{g:02x}{b:02x}'

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