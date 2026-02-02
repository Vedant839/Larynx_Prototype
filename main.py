#!/usr/bin/env python3
"""
Larynx - Real-Time Speech Transcription Application

Main application file that integrates all modules:
- Audio Capture (microphone streaming)
- Vosk ASR Engine (speech-to-text)
- Text Buffer (formatting and accumulation)
- GUI (user interface)

Provides real-time transcription with professional threading architecture.
"""

import sys
import os
import threading
import queue
import time
from typing import Optional

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from audio_capture import AudioCapture
from vosk_engine import VoskEngine
from text_buffer import TextBuffer
from gui import LarynxGUI

class LarynxApp:
    """
    Main application class for Larynx speech transcription.

    Manages threading, inter-module communication, and application lifecycle.
    """

    def __init__(self):
        """Initialize the application and all modules."""
        print("🎤 Initializing Larynx...")

        # Threading components
        self.audio_thread: Optional[threading.Thread] = None
        self.asr_thread: Optional[threading.Thread] = None
        self.gui_update_thread: Optional[threading.Thread] = None

        # Queues for thread communication
        self.audio_queue = queue.Queue(maxsize=100)  # Audio chunks
        self.text_queue = queue.Queue(maxsize=50)    # Text updates for GUI

        # Control flags
        self.running = False
        self.recording = False
        self.shutdown_event = threading.Event()

        # Modules
        self.audio_capture: Optional[AudioCapture] = None
        self.vosk_engine: Optional[VoskEngine] = None
        self.text_buffer: Optional[TextBuffer] = None
        self.gui: Optional[LarynxGUI] = None

        # Initialize modules
        self._init_modules()

    def _init_modules(self):
        """Initialize all application modules."""
        try:
            # Audio Capture
            print("Initializing audio capture...")
            self.audio_capture = AudioCapture()

            # Vosk Engine
            print("Initializing Vosk ASR engine...")
            model_path = "models/vosk-model-en-us-0.22"
            self.vosk_engine = VoskEngine(model_path)
            self.vosk_engine.start()

            # Text Buffer
            print("Initializing text buffer...")
            self.text_buffer = TextBuffer()

            # GUI
            print("Initializing GUI...")
            self.gui = LarynxGUI()

            # Connect GUI buttons to app methods
            self.gui.start_btn.config(command=self.start_recording)
            self.gui.stop_btn.config(command=self.stop_recording)
            self.gui.clear_btn.config(command=self.clear_text)

            print("✅ All modules initialized successfully")

        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            sys.exit(1)

    def start(self):
        """Launch the application."""
        print("🚀 Starting Larynx application...")

        self.running = True

        # Start GUI update thread
        self.gui_update_thread = threading.Thread(
            target=self._gui_update_worker,
            daemon=True,
            name="GUI-Update"
        )
        self.gui_update_thread.start()

        # Start GUI main loop (blocking)
        try:
            self.gui.run()
        except KeyboardInterrupt:
            print("\n⏹️  Application interrupted by user")
        finally:
            self.shutdown()

    def start_recording(self):
        """Start audio recording and transcription."""
        if self.recording:
            return

        print("🎤 Starting recording...")
        self.recording = True

        # Clear any previous text
        self.text_buffer.clear()
        self.text_buffer.add_partial_text("")  # Reset display

        # Clear queues
        self._clear_queues()

        # Restart Vosk engine if needed
        if not self.vosk_engine.is_recognizing():
            self.vosk_engine.start()

        # Start audio capture thread
        self.audio_thread = threading.Thread(
            target=self._audio_capture_worker,
            daemon=True,
            name="Audio-Capture"
        )
        self.audio_thread.start()

        # Start ASR processing thread
        self.asr_thread = threading.Thread(
            target=self._asr_worker,
            daemon=True,
            name="ASR-Processing"
        )
        self.asr_thread.start()

        # Update GUI
        self.gui.start_recording()

    def _clear_queues(self):
        """Clear all queues to prevent stale data."""
        # Clear audio queue
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break

        # Clear text queue
        while not self.text_queue.empty():
            try:
                self.text_queue.get_nowait()
            except queue.Empty:
                break

    def stop_recording(self):
        """Stop audio recording and transcription."""
        if not self.recording:
            return

        print("🛑 Stopping recording...")
        self.recording = False

        # Stop audio capture
        if self.audio_capture:
            self.audio_capture.stop_recording()

        # Wait for threads to finish
        if self.audio_thread and self.audio_thread.is_alive():
            self.audio_thread.join(timeout=2.0)

        if self.asr_thread and self.asr_thread.is_alive():
            self.asr_thread.join(timeout=2.0)

        # Get any remaining final results
        self._finalize_transcription()

        # Update GUI
        self.gui.stop_recording()

    def _audio_capture_worker(self):
        """Audio capture thread: continuously capture and queue audio chunks."""
        print("🎵 Audio capture thread started")

        # Start audio recording
        self.audio_capture.start_recording()

        while self.recording and not self.shutdown_event.is_set():
            try:
                # Get audio chunk with timeout
                chunk = self.audio_capture.get_audio_chunk(timeout=0.1)

                if chunk:
                    # Put in queue for ASR processing
                    try:
                        self.audio_queue.put(chunk, timeout=0.1)
                    except queue.Full:
                        # Remove oldest if queue full
                        try:
                            self.audio_queue.get_nowait()
                            self.audio_queue.put(chunk, timeout=0.1)
                        except:
                            pass  # Skip if can't manage

            except Exception as e:
                print(f"Audio capture error: {e}")
                time.sleep(0.01)

        print("🎵 Audio capture thread stopped")

    def _asr_worker(self):
        """ASR processing thread: process audio chunks and generate text."""
        print("🧠 ASR processing thread started")

        while self.recording and not self.shutdown_event.is_set():
            try:
                # Get audio chunk from queue
                chunk = self.audio_queue.get(timeout=0.1)

                # Process with Vosk
                results = self.vosk_engine.process_audio(chunk)

                # Handle partial results
                if results['partial']:
                    self.text_buffer.add_partial_text(results['partial'])
                    # Send update to GUI
                    self._send_text_update('partial', self.text_buffer.get_full_text())

                # Handle final results
                if results['final']:
                    self.text_buffer.add_final_text(results['final'])
                    # Send update to GUI
                    self._send_text_update('final', self.text_buffer.get_full_text())

            except queue.Empty:
                continue
            except Exception as e:
                print(f"ASR processing error: {e}")
                time.sleep(0.01)

        # Finalize any remaining transcription
        self._finalize_transcription()

        print("🧠 ASR processing thread stopped")

    def _finalize_transcription(self):
        """Finalize any remaining transcription results."""
        try:
            # Get any remaining final result from Vosk
            final_result = self.vosk_engine.get_final_result()
            if final_result:
                self.text_buffer.add_final_text(final_result)
                self._send_text_update('final', self.text_buffer.get_full_text())

            # Don't reset Vosk here - let it be reset on next start if needed

        except Exception as e:
            print(f"Finalization error: {e}")

    def _send_text_update(self, update_type: str, text: str):
        """Send text update to GUI queue."""
        try:
            update = {
                'type': update_type,
                'text': text,
                'word_count': self.text_buffer.get_word_count()
            }
            self.text_queue.put(update, timeout=0.1)
        except queue.Full:
            pass  # Skip if GUI queue full

    def _gui_update_worker(self):
        """GUI update thread: process text updates and update display."""
        print("🖥️  GUI update thread started")

        while not self.shutdown_event.is_set():
            try:
                # Get text update from queue
                update = self.text_queue.get(timeout=0.1)

                # Update GUI
                if self.gui:
                    self.gui.update_text_display(update['text'])
                    # Update word count in status
                    self.gui.word_count = update['word_count']
                    self.gui._update_status_text()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"GUI update error: {e}")
                time.sleep(0.01)

        print("🖥️  GUI update thread stopped")

    def clear_text(self):
        """Clear all transcribed text."""
        if self.text_buffer:
            self.text_buffer.clear()
            self._send_text_update('clear', "")

    def shutdown(self):
        """Gracefully shutdown the application."""
        print("🔄 Shutting down Larynx...")

        self.running = False
        self.recording = False
        self.shutdown_event.set()

        # Stop recording if active
        if self.recording:
            self.stop_recording()

        # Wait for threads
        threads = [self.audio_thread, self.asr_thread, self.gui_update_thread]
        for thread in threads:
            if thread and thread.is_alive():
                thread.join(timeout=2.0)

        # Clean up modules
        if self.audio_capture:
            self.audio_capture.stop_recording()

        if self.vosk_engine:
            self.vosk_engine.reset()

        print("✅ Larynx shutdown complete")


def main():
    """Main entry point."""
    try:
        app = LarynxApp()
        app.start()
    except KeyboardInterrupt:
        print("\n👋 Application terminated")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
