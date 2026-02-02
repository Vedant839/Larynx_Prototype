#!/usr/bin/env python3
"""
Detailed microphone test with device selection.
"""

import pyaudio
import numpy as np
import time

def list_audio_devices():
    """List all available input devices."""
    p = pyaudio.PyAudio()
    print("\n=== Available Input Devices ===")
    
    input_devices = []
    for i in range(p.get_device_count()):
        device_info = p.get_device_info_by_index(i)
        if device_info.get('maxInputChannels') > 0:
            input_devices.append((i, device_info))
            print(f"\nDevice {i}: {device_info.get('name')}")
            print(f"  Max Input Channels: {device_info.get('maxInputChannels')}")
            print(f"  Default Sample Rate: {device_info.get('defaultSampleRate')}")
    
    p.terminate()
    return input_devices

def test_microphone(device_index=None):
    """Test a specific microphone."""
    try:
        p = pyaudio.PyAudio()
        
        print(f"\n=== Testing Device {device_index if device_index else 'default'} ===")
        
        # Get device info to use supported sample rate
        if device_index is not None:
            device_info = p.get_device_info_by_index(device_index)
            sample_rate = int(device_info.get('defaultSampleRate'))
        else:
            sample_rate = 16000  # Default fallback
        
        print(f"Using sample rate: {sample_rate} Hz")
        
        # Open stream
        stream = p.open(
            format=pyaudio.paInt16,
            channels=1,
            rate=sample_rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=4000
        )
        
        print("\n🎤 Recording for 3 seconds...")
        print("👉 START SPEAKING NOW!")
        
        for i in range(3, 0, -1):
            print(f"   {i}...")
            time.sleep(1)
        
        # Record 3 seconds of audio
        frames = []
        chunks_per_second = sample_rate // 4000
        total_chunks = chunks_per_second * 3
        for _ in range(total_chunks):
            data = stream.read(4000)
            frames.append(data)
        
        stream.stop_stream()
        stream.close()
        p.terminate()
        
        # Convert to numpy array
        audio_data = np.frombuffer(b''.join(frames), dtype=np.int16)
        
        # Analyze audio
        max_amplitude = np.max(np.abs(audio_data))
        mean_amplitude = np.mean(np.abs(audio_data))
        
        print(f"\n📊 Results:")
        print(f"   Max amplitude: {max_amplitude:.2f}")
        print(f"   Mean amplitude: {mean_amplitude:.2f}")
        
        if max_amplitude > 1000:  # Reasonable threshold for speech
            print("\n✅ SUCCESS: Strong audio signal detected!")
            return True
        elif max_amplitude > 100:
            print("\n⚠️  WEAK: Audio detected but very quiet. Speak louder or move closer to mic.")
            return True
        else:
            print("\n❌ FAILED: No significant audio detected.")
            print("   Try:")
            print("   - Speaking louder")
            print("   - Selecting a different device")
            print("   - Checking microphone permissions")
            return False
            
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        return False

if __name__ == "__main__":
    # List all devices
    devices = list_audio_devices()
    
    if not devices:
        print("\n❌ No input devices found!")
        exit(1)
    
    print("\n" + "="*50)
    # Find the preferred device (pulse > default > sysdefault)
    preferred_patterns = ['pulse', 'default', 'sysdefault']
    device_index = None
    for pattern in preferred_patterns:
        for idx, info in devices:
            name = info.get('name', '').lower()
            if pattern in name:
                device_index = idx
                print(f"Found preferred device: {info.get('name')} (Device {idx}) using pattern '{pattern}'")
                break
        if device_index is not None:
            break
    
    if device_index is None:
        device_index = devices[0][0]  # Fallback to first
        print(f"Using first available device (Device {device_index})...")
    
    if device_index is None:
        device_index = devices[0][0]  # Fallback to first
        print(f"Using first available device (Device {device_index})...")
    
    # Test the device
    test_microphone(device_index)