#!/usr/bin/env python3
"""
Mock synthetic song generator for testing infrastructure
Replace this with actual DiffSinger/Suno integration once infrastructure works
"""

import json
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path

def generate_mock_song(index, output_audio, output_timestamps):
    """
    Generate a mock song for infrastructure testing
    
    This creates:
    1. A simple audio file (tone + noise to simulate singing)
    2. Perfect timestamps for mock lyrics
    
    Once this works, replace with real DiffSinger/Suno
    """
    
    print(f"🎵 Generating mock song {index}...")
    
    # Mock lyrics (10 words)
    lyrics = [
        "Hello", "this", "is", "song", "number",
        str(index), "for", "testing", "our", "system"
    ]
    
    # Generate mock audio (44.1kHz, 10 seconds)
    sr = 44100
    duration = 10  # seconds
    samples = sr * duration
    
    # Simple audio: tone + noise (simulates singing)
    t = np.linspace(0, duration, samples)
    frequency = 440 + (index * 10)  # Different pitch per song
    audio = 0.3 * np.sin(2 * np.pi * frequency * t)  # Sine wave
    audio += 0.05 * np.random.randn(samples)  # Add noise
    
    # Create timestamps (1 second per word)
    timestamps = []
    for i, word in enumerate(lyrics):
        start_time = i * 1.0
        end_time = (i + 1) * 1.0
        timestamps.append({
            'text': word,
            'start': start_time,
            'end': end_time
        })
    
    # Save audio
    Path(output_audio).parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_audio, audio, sr)
    print(f"✅ Audio saved: {output_audio}")
    
    # Save timestamps
    timestamp_data = {
        'song_id': f'song_{index:03d}',
        'duration': duration,
        'words': timestamps,
        'metadata': {
            'generator': 'mock_v1',
            'frequency_hz': frequency,
            'sample_rate': sr
        }
    }
    
    Path(output_timestamps).parent.mkdir(parents=True, exist_ok=True)
    with open(output_timestamps, 'w') as f:
        json.dump(timestamp_data, f, indent=2)
    print(f"✅ Timestamps saved: {output_timestamps}")
    
    print(f"🎉 Song {index} generation complete!\n")
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate mock synthetic song')
    parser.add_argument('--index', type=int, required=True, help='Song index number')
    parser.add_argument('--output', type=str, required=True, help='Output audio path')
    parser.add_argument('--timestamps', type=str, required=True, help='Output timestamps path')
    
    args = parser.parse_args()
    
    try:
        generate_mock_song(args.index, args.output, args.timestamps)
        print("✅ SUCCESS")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        raise
