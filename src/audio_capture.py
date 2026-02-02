#!/usr/bin/env python3
"""
Audio Capture Module for Larynx ASR Tool.

Handles continuous microphone recording with proper parameters for Vosk.
Implements thread-safe audio queue for real-time processing.
"""

import pyaudio
import queue
import threading
import time
import numpy as np

class AudioCapture:
    """
    Audio capture class for continuous microphone recording.

    Provides thread-safe audio streaming with configurable parameters
    optimized for Vosk speech recognition.
    """

    def __init__(self, sample_rate=16000, chunk_size=4000, device_index=None):
        """
        Initialize audio capture.

        Args:
            sample_rate (int): Audio sample rate in Hz (default: 16000 for Vosk)
            chunk_size (int): Number of frames per chunk (default: 4000)
            device_index (int): Audio device index (None for auto-select)
        """
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.device_index = device_index

        # Audio components
        self.audio = None
        self.stream = None
        self.audio_queue = queue.Queue(maxsize=100)  # Thread-safe queue

        # Threading
        self.recording_thread = None
        self.is_recording_flag = False

        # Auto-select device if not specified
        if self.device_index is None:
            self.device_index = self._select_preferred_device()

    def _select_preferred_device(self):
        """Select the best available input device (prioritize PulseAudio)."""
        try:
            temp_audio = pyaudio.PyAudio()
            devices = []

            for i in range(temp_audio.get_device_count()):
                device_info = temp_audio.get_device_info_by_index(i)
                if device_info.get('maxInputChannels') > 0:
                    devices.append((i, device_info))

            temp_audio.terminate()

            # Prefer PulseAudio device
            preferred_patterns = ['pulse', 'default', 'sysdefault']
            for pattern in preferred_patterns:
                for idx, info in devices:
                    name = info.get('name', '').lower()
                    if pattern in name:
                        return idx

            # Fallback to first device
            return devices[0][0] if devices else None

        except Exception as e:
            print(f"Warning: Could not select device: {e}")
            return None

    def _recording_worker(self):
        """Worker thread for continuous audio recording."""
        try:
            self.audio = pyaudio.PyAudio()
            self.stream = self.audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=self.sample_rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk_size
            )

            print(f"🎤 Started recording on device {self.device_index} at {self.sample_rate}Hz")

            while self.is_recording_flag:
                try:
                    # Read audio chunk
                    data = self.stream.read(self.chunk_size, exception_on_overflow=False)

                    # Put in queue (non-blocking, drop if full to avoid lag)
                    try:
                        self.audio_queue.put(data, timeout=0.1)
                    except queue.Full:
                        # Remove oldest chunk if queue is full
                        try:
                            self.audio_queue.get_nowait()
                            self.audio_queue.put(data, timeout=0.1)
                        except:
                            pass  # Skip if can't manage queue

                except Exception as e:
                    print(f"Audio read error: {e}")
                    time.sleep(0.01)  # Brief pause on error

        except Exception as e:
            print(f"Recording thread error: {e}")
        finally:
            self._cleanup()

    def _cleanup(self):
        """Clean up audio resources."""
        try:
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
            if self.audio:
                self.audio.terminate()
        except Exception as e:
            print(f"Cleanup error: {e}")

    def start_recording(self):
        """Start continuous audio recording in a background thread."""
        if self.is_recording_flag:
            print("Already recording")
            return

        self.is_recording_flag = True
        self.recording_thread = threading.Thread(target=self._recording_worker, daemon=True)
        self.recording_thread.start()

    def stop_recording(self):
        """Stop audio recording and clean up."""
        if not self.is_recording_flag:
            return

        print("🛑 Stopping recording...")
        self.is_recording_flag = False

        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)

        self._cleanup()
        print("Recording stopped")

    def get_audio_chunk(self, timeout=0.1):
        """
        Get the next audio chunk from the queue.

        Args:
            timeout (float): Timeout in seconds to wait for chunk

        Returns:
            bytes: Audio data chunk, or None if no data available
        """
        try:
            return self.audio_queue.get(timeout=timeout)
        except queue.Empty:
            return None

    def is_recording(self):
        """Check if currently recording."""
        return self.is_recording_flag

    def get_queue_size(self):
        """Get current queue size (for debugging)."""
        return self.audio_queue.qsize()

    def clear_queue(self):
        """Clear all pending audio chunks from queue."""
        while not self.audio_queue.empty():
            try:
                self.audio_queue.get_nowait()
            except queue.Empty:
                break


# Test function for standalone testing
def test_audio_capture():
    """Test the audio capture module."""
    print("Testing AudioCapture module...")

    capture = AudioCapture()

    print("Starting recording for 5 seconds...")
    capture.start_recording()

    chunks_received = 0
    start_time = time.time()

    while time.time() - start_time < 5:
        chunk = capture.get_audio_chunk(timeout=0.1)
        if chunk:
            chunks_received += 1
            # Convert to numpy for analysis
            audio_data = np.frombuffer(chunk, dtype=np.int16)
            max_amp = np.max(np.abs(audio_data))
            print(".1f")

    capture.stop_recording()

    print(f"Test complete. Received {chunks_received} chunks in 5 seconds")
    expected_chunks = 5 / (capture.chunk_size / capture.sample_rate)
    print(".1f")


if __name__ == "__main__":
    test_audio_capture()