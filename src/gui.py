#!/usr/bin/env python3
"""
Larynx GUI - Modern Tkinter Interface for Real-Time Speech Transcription.

Provides a clean, modern interface for speech-to-text transcription with
real-time updates, clipboard integration, and professional styling.
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import time

class LarynxGUI:
    """
    Modern GUI for Larynx speech transcription application.

    Features dark theme, real-time text updates, and intuitive controls.
    """

    def __init__(self, root=None):
        """
        Initialize the GUI.

        Args:
            root: Tkinter root window (creates new if None)
        """
        self.root = root or tk.Tk()
        self.root.title("Larynx - Real-Time Speech Transcription")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Theme colors (dark mode)
        self.colors = {
            'bg': '#2b2b2b',           # Dark background
            'fg': '#ffffff',           # Light text
            'accent': '#007acc',       # Blue accent
            'accent_hover': '#005999', # Darker blue
            'secondary': '#404040',    # Dark gray
            'text_bg': '#1e1e1e',      # Text area background
            'button_bg': '#404040',    # Button background
            'recording': '#ff6b6b',    # Red for recording
            'idle': '#4ecdc4'          # Teal for idle
        }

        # Configure root
        self.root.configure(bg=self.colors['bg'])
        self._setup_styles()

        # GUI state
        self.is_recording = False
        self.word_count = 0

        # Create widgets
        self.create_widgets()

        # Bind events
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def _setup_styles(self):
        """Configure ttk styles for modern appearance."""
        style = ttk.Style()

        # Button style
        style.configure('Modern.TButton',
                       background=self.colors['button_bg'],
                       foreground=self.colors['fg'],
                       borderwidth=0,
                       focusthickness=0,
                       relief='flat',
                       font=('Segoe UI', 10, 'bold'))

        style.map('Modern.TButton',
                 background=[('active', self.colors['accent_hover']),
                           ('pressed', self.colors['accent'])])

        # Label style
        style.configure('Modern.TLabel',
                       background=self.colors['bg'],
                       foreground=self.colors['fg'],
                       font=('Segoe UI', 10))

        # Frame style
        style.configure('Modern.TFrame',
                       background=self.colors['bg'])

    def create_widgets(self):
        """Create and layout all GUI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, style='Modern.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        title_label = ttk.Label(main_frame,
                               text="🎤 Larynx - Real-Time Transcription",
                               font=('Segoe UI', 16, 'bold'),
                               style='Modern.TLabel')
        title_label.pack(pady=(0, 20))

        # Control buttons frame
        controls_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        controls_frame.pack(fill=tk.X, pady=(0, 15))

        # Buttons
        self.start_btn = ttk.Button(controls_frame, text="▶ Start",
                                   command=self.start_recording,
                                   style='Modern.TButton')
        self.start_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.stop_btn = ttk.Button(controls_frame, text="⏹ Stop",
                                  command=self.stop_recording,
                                  style='Modern.TButton',
                                  state='disabled')
        self.stop_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.clear_btn = ttk.Button(controls_frame, text="🗑 Clear",
                                   command=self.clear_text,
                                   style='Modern.TButton')
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.copy_btn = ttk.Button(controls_frame, text="📋 Copy",
                                  command=self.copy_to_clipboard,
                                  style='Modern.TButton')
        self.copy_btn.pack(side=tk.LEFT)

        # Status frame
        status_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        status_frame.pack(fill=tk.X, pady=(0, 15))

        # Status indicator
        self.status_indicator = tk.Canvas(status_frame, width=16, height=16,
                                        bg=self.colors['bg'], highlightthickness=0)
        self.status_indicator.pack(side=tk.LEFT, padx=(0, 10))
        self._update_status_indicator()

        # Status text
        self.status_label = ttk.Label(status_frame,
                                     text="Status: Idle | Words: 0",
                                     style='Modern.TLabel')
        self.status_label.pack(side=tk.LEFT)

        # Text display area
        text_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        text_frame.pack(fill=tk.BOTH, expand=True)

        # Scrolled text widget
        self.text_area = scrolledtext.ScrolledText(
            text_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),  # Monospace for readability
            bg=self.colors['text_bg'],
            fg=self.colors['fg'],
            insertbackground=self.colors['fg'],  # Cursor color
            selectbackground=self.colors['accent'],  # Selection color
            selectforeground=self.colors['fg'],
            borderwidth=0,
            highlightthickness=1,
            highlightbackground=self.colors['secondary'],
            highlightcolor=self.colors['accent']
        )
        self.text_area.pack(fill=tk.BOTH, expand=True)

        # Placeholder text
        self.text_area.insert(tk.END, "Transcribed text will appear here...\n\nClick 'Start' to begin recording.")
        self.text_area.config(state='disabled')  # Initially disabled

    def _update_status_indicator(self):
        """Update the status indicator circle."""
        self.status_indicator.delete("all")
        color = self.colors['recording'] if self.is_recording else self.colors['idle']
        self.status_indicator.create_oval(2, 2, 14, 14, fill=color, outline=color)

    def start_recording(self):
        """Handle start recording button click."""
        if self.is_recording:
            return

        self.is_recording = True
        self.start_btn.config(state='disabled')
        self.stop_btn.config(state='normal')
        self._update_status_indicator()
        self._update_status_text()

        # Clear placeholder text on first start
        if "Transcribed text will appear here" in self.text_area.get(1.0, tk.END):
            self.text_area.config(state='normal')
            self.text_area.delete(1.0, tk.END)
            self.text_area.config(state='disabled')

        print("🎤 Recording started")

    def stop_recording(self):
        """Handle stop recording button click."""
        if not self.is_recording:
            return

        self.is_recording = False
        self.start_btn.config(state='normal')
        self.stop_btn.config(state='disabled')
        self._update_status_indicator()
        self._update_status_text()

        print("🛑 Recording stopped")

    def update_text_display(self, text):
        """
        Update the transcription text display.

        Args:
            text (str): New text to display
        """
        def update():
            self.text_area.config(state='normal')
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, text)
            self.text_area.config(state='disabled')

            # Auto-scroll to bottom
            self.text_area.see(tk.END)

            # Update word count
            self.word_count = len(text.split()) if text.strip() else 0
            self._update_status_text()

        # Schedule update on main thread
        self.root.after(0, update)

    def _update_status_text(self):
        """Update the status label text."""
        status = "Recording" if self.is_recording else "Idle"
        self.status_label.config(text=f"Status: {status} | Words: {self.word_count}")

    def copy_to_clipboard(self):
        """Copy all text to clipboard."""
        text = self.text_area.get(1.0, tk.END).strip()
        if text:
            self.root.clipboard_clear()
            self.root.clipboard_append(text)
            # Visual feedback
            original_text = self.copy_btn.cget('text')
            self.copy_btn.config(text="✅ Copied!")
            self.root.after(1500, lambda: self.copy_btn.config(text=original_text))
        else:
            messagebox.showinfo("Copy", "No text to copy")

    def clear_text(self):
        """Clear all transcribed text."""
        if messagebox.askyesno("Clear Text", "Are you sure you want to clear all text?"):
            self.text_area.config(state='normal')
            self.text_area.delete(1.0, tk.END)
            self.text_area.insert(tk.END, "Transcribed text will appear here...\n\nClick 'Start' to begin recording.")
            self.text_area.config(state='disabled')
            self.word_count = 0
            self._update_status_text()

    def on_closing(self):
        """Handle window close event."""
        if self.is_recording:
            if messagebox.askyesno("Quit", "Recording is in progress. Stop and quit?"):
                self.stop_recording()
                self.root.destroy()
        else:
            self.root.destroy()

    def run(self):
        """Start the GUI main loop."""
        self.root.mainloop()


# Test function for standalone GUI testing
def test_gui():
    """Test the GUI independently."""
    gui = LarynxGUI()

    # Simulate some text updates
    def simulate_updates():
        texts = [
            "Hello world",
            "Hello world this is a test",
            "Hello world this is a test of the transcription system",
            "Hello world this is a test of the transcription system working properly"
        ]

        for i, text in enumerate(texts):
            gui.root.after(i * 2000, lambda t=text: gui.update_text_display(t))

    gui.root.after(1000, simulate_updates)
    gui.run()


if __name__ == "__main__":
    test_gui()