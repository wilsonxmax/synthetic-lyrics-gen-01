#!/usr/bin/env python3
"""
Validate generated timestamps against audio
"""

import json
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path

def validate_timestamps(audio_path, timestamps_path):
    """
    Run all automated validation checks
    """
    
    print(f"\n{'='*60}")
    print(f"VALIDATING: {Path(audio_path).name}")
    print(f"{'='*60}\n")
    
    # Load audio
    try:
        audio, sr = sf.read(audio_path)
        audio_duration = len(audio) / sr
        print(f"✅ Audio loaded: {audio_duration:.2f}s @ {sr}Hz")
    except Exception as e:
        print(f"❌ Failed to load audio: {e}")
        return False
    
    # Load timestamps
    try:
        with open(timestamps_path) as f:
            data = json.load(f)
        timestamps = data['words']
        print(f"✅ Timestamps loaded: {len(timestamps)} words")
    except Exception as e:
        print(f"❌ Failed to load timestamps: {e}")
        return False
    
    # Run validation checks
    checks = {}
    
    # 1. No negative durations
    negative_durations = [
        w for w in timestamps if w['end'] <= w['start']
    ]
    checks['no_negative_durations'] = len(negative_durations) == 0
    if negative_durations:
        print(f"⚠️  Found {len(negative_durations)} negative durations")
    
    # 2. No overlaps
    overlaps = []
    for i in range(len(timestamps) - 1):
        if timestamps[i]['end'] > timestamps[i+1]['start']:
            overlaps.append((i, i+1))
    checks['no_overlaps'] = len(overlaps) == 0
    if overlaps:
        print(f"⚠️  Found {len(overlaps)} overlapping words")
    
    # 3. Realistic durations (50ms to 10 seconds)
    unrealistic = [
        w for w in timestamps 
        if (w['end'] - w['start']) < 0.05 or (w['end'] - w['start']) > 10.0
    ]
    checks['realistic_durations'] = len(unrealistic) == 0
    if unrealistic:
        print(f"⚠️  Found {len(unrealistic)} unrealistic durations")
    
    # 4. Within audio bounds
    out_of_bounds = [
        w for w in timestamps
        if w['start'] < 0 or w['end'] > audio_duration
    ]
    checks['within_bounds'] = len(out_of_bounds) == 0
    if out_of_bounds:
        print(f"⚠️  Found {len(out_of_bounds)} timestamps outside audio bounds")
    
    # 5. Monotonic (always increasing)
    non_monotonic = []
    for i in range(len(timestamps) - 1):
        if timestamps[i]['start'] >= timestamps[i+1]['start']:
            non_monotonic.append(i)
    checks['monotonic'] = len(non_monotonic) == 0
    if non_monotonic:
        print(f"⚠️  Found {len(non_monotonic)} non-monotonic timestamps")
    
    # 6. Basic energy check (words should have audio)
    silent_words = []
    for word in timestamps:
        start_sample = int(word['start'] * sr)
        end_sample = int(word['end'] * sr)
        segment = audio[start_sample:end_sample]
        energy = np.mean(np.abs(segment))
        
        if energy < 0.001:  # Very quiet
            silent_words.append(word['text'])
    
    checks['has_audio_energy'] = len(silent_words) < len(timestamps) * 0.1  # Allow 10% silent
    if silent_words:
        print(f"⚠️  Found {len(silent_words)} potentially silent words")
    
    # Print results
    print(f"\n{'='*60}")
    print("VALIDATION RESULTS:")
    print(f"{'='*60}")
    
    for check_name, passed in checks.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {check_name:30s}: {status}")
    
    print(f"{'='*60}\n")
    
    # Overall result
    all_passed = all(checks.values())
    
    if all_passed:
        print("🎉 ALL VALIDATION CHECKS PASSED!\n")
    else:
        print("⚠️  SOME VALIDATION CHECKS FAILED\n")
        failed = [name for name, passed in checks.items() if not passed]
        print(f"Failed checks: {', '.join(failed)}\n")
        exit(1)
    
    return all_passed

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Validate song timestamps')
    parser.add_argument('--audio', type=str, required=True, help='Path to audio file')
    parser.add_argument('--timestamps', type=str, required=True, help='Path to timestamps JSON')
    
    args = parser.parse_args()
    
    try:
        validate_timestamps(args.audio, args.timestamps)
    except Exception as e:
        print(f"❌ VALIDATION ERROR: {e}")
        exit(1)
```

---

## **🚀 COMPLETE REPOSITORY STRUCTURE**
```
synthetic-lyrics-gen-01/
├── .github/
│   └── workflows/
│       └── generate-songs.yml          # ✅ Updated to v4
├── scripts/
│   ├── generate_song.py                # Mock generator (replace later)
│   └── validate_timestamps.py          # Validation suite
├── outputs/                             # Created during workflow
│   ├── song_1.mp3
│   ├── song_1.json
│   └── ...
├── README.md
└── requirements.txt                     # Dependencies
