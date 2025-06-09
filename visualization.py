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
        self.message = ""

        self.WAVE_WIDTH = 120
        self.WAVE_HEIGHT = 40
        self.WAVE_POINTS = 40
        self.ANIMATION_SPEED = 30

        self.root = tk.Tk()
        self.root.withdraw()

        self.icon_path = Path(__file__).parent / "assets" / "mic.png"
        if not self.icon_path.parent.exists():
            os.makedirs(self.icon_path.parent)
            self._create_default_icon(self.icon_path)

        self._load_mic_image()
        self.audio_stream = None

    def _create_default_icon(self, icon_path):
        size = 64
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        body_width = size // 3
        body_height = size // 2
        body_left = (size - body_width) // 2
        body_top = size // 6
        for y in range(body_height):
            color = (41, 128, 185, int(255 * (0.8 + 0.2 * (y / body_height))))
            draw.rectangle(
                [body_left, body_top + y, body_left + body_width, body_top + y + 1],
                fill=color
            )
        corner_radius = body_width // 3
        draw.ellipse([body_left, body_top, body_left + corner_radius * 2, body_top + corner_radius * 2],
                    fill=(41, 128, 185, 255))
        draw.ellipse([body_left + body_width - corner_radius * 2, body_top,
                     body_left + body_width, body_top + corner_radius * 2],
                    fill=(41, 128, 185, 255))
        base_width = body_width * 1.5
        base_height = size // 10
        base_left = (size - base_width) // 2
        base_top = body_top + body_height + size // 8
        for y in range(base_height):
            alpha = int(255 * (0.7 + 0.3 * (1 - y / base_height)))
            draw.rectangle(
                [base_left, base_top + y, base_left + base_width, base_top + y + 1],
                fill=(41, 128, 185, alpha)
            )
        connector_width = body_width // 3
        connector_left = (size - connector_width) // 2
        draw.rectangle(
            [connector_left, body_top + body_height,
             connector_left + connector_width, base_top],
            fill=(41, 128, 185, 200)
        )
        img.save(icon_path)

    def _load_mic_image(self):
        if self.mic_photo is None:
            mic_image = Image.open(self.icon_path)
            mic_image = mic_image.resize((48, 48), Image.Resampling.LANCZOS)
            self.mic_photo = ImageTk.PhotoImage(mic_image)

    def _setup_audio_stream(self):
        def audio_callback(indata, frames, time, status):
            if status:
                print(f"Audio status: {status}")
            if self.is_recording:
                audio_level = np.sqrt(np.mean(indata**2))
                try:
                    self.audio_data.put_nowait(audio_level)
                except queue.Full:
                    pass

        self.audio_stream = sd.InputStream(
            channels=1,
            samplerate=16000,
            callback=audio_callback
        )
        self.audio_stream.start()

    def _create_rounded_rectangle(self, canvas, x1, y1, x2, y2, radius, **kwargs):
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
        self.command_queue.put(('show', None))

    def hide(self):
        self.command_queue.put(('hide', None))

    def set_message(self, message):
        """Queue a message update to be executed in main thread"""
        self.command_queue.put(('message', message))

    def _show_window(self):
        if self.window is None:
            self.window = tk.Toplevel(self.root)
            self.window.title("")
            self.window.overrideredirect(True)
            self.window.attributes('-topmost', True)
            window_width = 250
            window_height = 120  # Increased height for message
            x, y = 10, 10
            self.window.geometry(f"{window_width}x{window_height}+{x}+{y}")
            self.window.attributes('-alpha', 0.95)
            self.window.configure(bg='#2c3e50')

            self.canvas = tk.Canvas(
                self.window,
                width=window_width,
                height=window_height,
                bg='#2c3e50',
                highlightthickness=0
            )
            self.canvas.pack(fill='both', expand=True)

            self._create_rounded_rectangle(
                self.canvas, 2, 2, window_width-2, window_height-2, 20,
                fill='#34495e', outline='#3498db', width=2
            )

            # Add message text at the bottom
            self.message_id = self.canvas.create_text(
                window_width//2, window_height-15,
                text=self.message,
                fill='#bdc3c7',
                font=('Arial', 9),
                anchor='s',
                width=window_width-20  # Allow text wrapping
            )

            self.canvas.create_image(30, window_height//2 - 10, anchor='center', image=self.mic_photo)
            self._init_waveform()
            self._setup_audio_stream()
            self.is_recording = True
            self._animate_waveform()

    def _hide_window(self):
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
        self.current_amplitude = 0
        self.target_amplitude = 0

    def _animate_waveform(self):
        if not self.is_recording or not self.canvas:
            return

        try:
            try:
                audio_level = self.audio_data.get_nowait() * 300  # <-- Amplified
                self.target_amplitude = min(70, audio_level)  # <-- Allow more visible peaks
            except queue.Empty:
                self.target_amplitude *= 0.9

            self.current_amplitude = self.current_amplitude * 0.6 + self.target_amplitude * 0.4
            self.canvas.delete('waveform')

            points = []
            start_x = 80
            base_y = self.window.winfo_height() // 2
            num_points = 80
            for i in range(num_points):
                x = start_x + (self.WAVE_WIDTH * i / (num_points - 1))
                phase = self.animation_frame * 0.12
                y = base_y - self.current_amplitude * math.sin(
                    (i / num_points) * math.pi * 2 + phase
                )
                points.extend([x, y])

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
            pass

    def _adjust_color(self, color, alpha):
        r = int(color[1:3], 16)
        g = int(color[3:5], 16)
        b = int(color[5:7], 16)
        bg_r, bg_g, bg_b = 44, 62, 80
        r = int(r * alpha + bg_r * (1 - alpha))
        g = int(g * alpha + bg_g * (1 - alpha))
        b = int(b * alpha + bg_b * (1 - alpha))
        return f'#{r:02x}{g:02x}{b:02x}'

    def _update_message(self, message):
        """Update the message text in the window"""
        self.message = message
        if self.window and hasattr(self, 'message_id'):
            self.canvas.itemconfig(self.message_id, text=message)

    def process_commands(self):
        try:
            while True:
                command, args = self.command_queue.get_nowait()
                if command == 'show':
                    self._show_window()
                elif command == 'hide':
                    self._hide_window()
                elif command == 'message':
                    self._update_message(args)
        except queue.Empty:
            pass

        try:
            self.root.update()
        except tk.TclError:
            pass