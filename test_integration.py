#!/usr/bin/env python3
"""
Combined test: Audio Capture + Vosk ASR Integration.

Tests the full audio pipeline: microphone → Vosk → transcription.
"""

import time
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from audio_capture import AudioCapture
from vosk_engine import VoskEngine

def test_audio_to_text():
    """Test end-to-end audio capture to text transcription."""
    print("🎤 Testing Audio Capture + Vosk ASR Integration")
    print("=" * 50)

    # Initialize components
    print("Initializing audio capture...")
    capture = AudioCapture()

    print("Initializing Vosk engine...")
    model_path = "models/vosk-model-en-us-0.22"
    engine = VoskEngine(model_path)
    engine.start()

    print("\n🚀 Starting 10-second recording and transcription test...")
    print("👉 SPEAK CLEARLY INTO THE MICROPHONE NOW!")

    # Start recording
    capture.start_recording()
    start_time = time.time()

    partial_text = ""
    final_text = ""

    try:
        while time.time() - start_time < 10:  # 10 seconds test
            # Get audio chunk
            chunk = capture.get_audio_chunk(timeout=0.1)
            if chunk:
                # Process with Vosk
                results = engine.process_audio(chunk)
                
                # Debug: print chunk info
                print(f"Chunk: {len(chunk)} bytes, Partial: '{results['partial']}', Final: '{results['final']}'")
                
                # Handle partial results
                if results['partial'] and results['partial'] != partial_text:
                    partial_text = results['partial']
                    print(f"🔄 Partial: {partial_text}")

                # Handle final results
                if results['final']:
                    final_text += results['final'] + " "
                    print(f"✅ Final: {results['final']}")
                    # Reset partial after final
                    partial_text = ""

            time.sleep(0.01)  # Small delay to prevent busy loop

    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")

    finally:
        # Stop recording
        capture.stop_recording()

        # Get any remaining final result
        remaining = engine.get_final_result()
        if remaining:
            final_text += remaining + " "

        print("\n" + "=" * 50)
        print("📝 TRANSCRIPTION RESULTS:")
        print(f"Final text: '{final_text.strip()}'")
        print(f"Word count: {len(final_text.split()) if final_text.strip() else 0}")

        if final_text.strip():
            print("✅ SUCCESS: Speech detected and transcribed!")
        else:
            print("⚠️  No speech detected. Try speaking louder or closer to mic.")

        print("\nTest complete!")

if __name__ == "__main__":
    test_audio_to_text()