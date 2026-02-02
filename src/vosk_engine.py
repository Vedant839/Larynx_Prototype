#!/usr/bin/env python3
"""
Vosk ASR Engine for Larynx.

Handles speech-to-text conversion using Vosk offline ASR.
Provides streaming recognition with partial and final results.
"""

import os
import json
import vosk
import time

class VoskEngine:
    """
    Vosk-based speech recognition engine.

    Loads the Vosk model and provides streaming transcription
    with real-time partial results and final confirmed text.
    """

    def __init__(self, model_path):
        """
        Initialize Vosk engine with model path.

        Args:
            model_path (str): Path to the Vosk model directory
        """
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.is_active = False

        # Load model on initialization
        self._load_model()

    def _load_model(self):
        """Load the Vosk model from disk."""
        if not os.path.exists(self.model_path):
            raise FileNotFoundError(f"Vosk model not found at: {self.model_path}")

        print(f"Loading Vosk model from: {self.model_path}")
        start_time = time.time()

        try:
            self.model = vosk.Model(self.model_path)
            load_time = time.time() - start_time
            print(".2f")
        except Exception as e:
            raise RuntimeError(f"Failed to load Vosk model: {e}")

    def start(self):
        """Initialize the recognizer for streaming recognition."""
        if self.model is None:
            raise RuntimeError("Model not loaded")

        if self.recognizer is not None:
            self.reset()

        # Create recognizer with 16kHz sample rate
        self.recognizer = vosk.KaldiRecognizer(self.model, 16000)
        self.is_active = True
        print("Vosk recognizer started")

    def process_audio(self, audio_data):
        """
        Process audio chunk and return any recognition results.

        Args:
            audio_data (bytes): Raw audio data (16-bit PCM, 16kHz, mono)

        Returns:
            dict: Recognition results with keys:
                - 'partial': str or None (real-time partial transcription)
                - 'final': str or None (confirmed final text)
        """
        if not self.is_active or self.recognizer is None:
            return {'partial': None, 'final': None}

        results = {'partial': None, 'final': None}

        try:
            # Feed audio data to recognizer
            if self.recognizer.AcceptWaveform(audio_data):
                # Final result available
                result_json = self.recognizer.Result()
                result = json.loads(result_json)
                results['final'] = result.get('text', '').strip()
            else:
                # Partial result
                partial_json = self.recognizer.PartialResult()
                partial = json.loads(partial_json)
                results['partial'] = partial.get('partial', '').strip()

        except Exception as e:
            print(f"Vosk processing error: {e}")
            # Continue processing despite errors

        return results

    def get_partial_result(self):
        """
        Get current partial recognition result.

        Returns:
            str: Current partial transcription text
        """
        if not self.is_active or self.recognizer is None:
            return ""

        try:
            partial_json = self.recognizer.PartialResult()
            partial = json.loads(partial_json)
            return partial.get('partial', '').strip()
        except Exception as e:
            print(f"Error getting partial result: {e}")
            return ""

    def get_final_result(self):
        """
        Get final recognition result if available.

        Returns:
            str: Final confirmed transcription text, or empty string
        """
        if not self.is_active or self.recognizer is None:
            return ""

        try:
            result_json = self.recognizer.Result()
            result = json.loads(result_json)
            return result.get('text', '').strip()
        except Exception as e:
            print(f"Error getting final result: {e}")
            return ""

    def reset(self):
        """Reset the recognizer state."""
        if self.recognizer:
            # Vosk doesn't have explicit reset, create new recognizer
            self.recognizer = None
        self.is_active = False
        print("Vosk recognizer reset")

    def is_recognizing(self):
        """Check if recognizer is active."""
        return self.is_active


# Test function for standalone testing
def test_vosk_engine():
    """Test the Vosk engine with sample audio."""
    print("Testing VoskEngine...")

    model_path = "models/vosk-model-en-us-0.22"
    engine = VoskEngine(model_path)
    engine.start()

    # Create some dummy audio data (silence)
    sample_rate = 16000
    duration = 1.0  # 1 second
    samples = int(sample_rate * duration)
    # Generate silence (all zeros)
    audio_data = b'\x00\x00' * samples

    print("Processing 1 second of silence...")
    results = engine.process_audio(audio_data)
    print(f"Results: {results}")

    # Test with some noise (random data)
    import random
    noise_data = bytes([random.randint(0, 255) for _ in range(samples * 2)])
    print("Processing 1 second of noise...")
    results = engine.process_audio(noise_data)
    print(f"Results: {results}")

    print("Vosk engine test complete")


if __name__ == "__main__":
    test_vosk_engine()