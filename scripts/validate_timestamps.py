#!/usr/bin/env python3
"""
Automated validation of generated timestamps
"""

import json
import librosa
import numpy as np

def validate_timestamps(audio_path, timestamps_path):
    """
    Run all automated checks on generated song
    """
    
    # Load data
    y, sr = librosa.load(audio_path, sr=22050)
    with open(timestamps_path) as f:
        timestamps = json.load(f)['words']
    
    checks = {}
    
    # 1. No negative durations
    checks['no_negative_durations'] = all(
        w['end'] > w['start'] for w in timestamps
    )
    
    # 2. No overlaps
    checks['no_overlaps'] = all(
        timestamps[i]['end'] <= timestamps[i+1]['start']
        for i in range(len(timestamps)-1)
    )
    
    # 3. Realistic durations (50ms to 5 seconds)
    checks['realistic_durations'] = all(
        0.05 < (w['end'] - w['start']) < 5.0
        for w in timestamps
    )
    
    # 4. Within audio bounds
    audio_duration = len(y) / sr
    checks['within_bounds'] = all(
        0 <= w['start'] < audio_duration and
        0 < w['end'] <= audio_duration
        for w in timestamps
    )
    
    # 5. Monotonic (always increasing)
    checks['monotonic'] = all(
        timestamps[i]['start'] < timestamps[i+1]['start']
        for i in range(len(timestamps)-1)
    )
    
    # 6. Energy synchronization (basic check)
    energy_sync = check_energy_at_words(y, sr, timestamps)
    checks['energy_sync'] = energy_sync > 0.90
    
    # Print results
    print(f"\n{'='*50}")
    print(f"VALIDATION RESULTS: {audio_path}")
    print(f"{'='*50}")
    for check, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{check:30s}: {status}")
    print(f"{'='*50}\n")
    
    # Overall result
    all_passed = all(checks.values())
    if all_passed:
        print("🎉 All validation checks PASSED!")
    else:
        print("⚠️ Some validation checks FAILED!")
        exit(1)
    
    return all_passed

def check_energy_at_words(audio, sr, timestamps):
    """
    Verify that there's vocal energy where words should be
    """
    hop_length = 512
    rms = librosa.feature.rms(y=audio, hop_length=hop_length)[0]
    times = librosa.frames_to_time(range(len(rms)), sr=sr, hop_length=hop_length)
    
    vocal_energy_scores = []
    
    for word in timestamps:
        # Get RMS energy during word
        mask = (times >= word['start']) & (times <= word['end'])
        word_energy = np.mean(rms[mask]) if mask.any() else 0
        
        # Should have some energy (not silent)
        vocal_energy_scores.append(word_energy > 0.01)
    
    return np.mean(vocal_energy_scores)

if __name__ == '__main__':
    import sys
    audio_path = sys.argv[1]
    timestamps_path = sys.argv[2]
    
    validate_timestamps(audio_path, timestamps_path)
