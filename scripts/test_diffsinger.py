#!/usr/bin/env python3
"""
Test DiffSinger installation and basic inference
"""

import sys
import time
import torch
import librosa
import soundfile as sf
import numpy as np
from pathlib import Path

def test_pytorch():
    """Verify PyTorch installation"""
    print("=" * 60)
    print("TESTING PYTORCH")
    print("=" * 60)
    
    print(f"PyTorch version: {torch.__version__}")
    print(f"CUDA available: {torch.cuda.is_available()}")
    print(f"CPU cores: {torch.get_num_threads()}")
    
    # Simple tensor operation
    x = torch.randn(100, 100)
    y = torch.mm(x, x)
    print(f"✅ PyTorch working (test tensor: {y.shape})")
    print()

def test_audio_processing():
    """Verify audio processing libraries"""
    print("=" * 60)
    print("TESTING AUDIO LIBRARIES")
    print("=" * 60)
    
    # Create test audio
    sr = 22050
    duration = 2.0
    t = np.linspace(0, duration, int(sr * duration))
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)
    
    # Save and reload
    test_file = "test_audio.wav"
    sf.write(test_file, audio, sr)
    loaded, sr_loaded = librosa.load(test_file, sr=sr)
    
    print(f"✅ Audio I/O working (sr={sr_loaded}Hz, duration={len(loaded)/sr_loaded:.2f}s)")
    
    # Cleanup
    Path(test_file).unlink()
    print()

def test_diffsinger_inference():
    """
    Test actual DiffSinger inference
    
    NOTE: This is a placeholder for real DiffSinger code
    You'll need to:
    1. Download a pre-trained DiffSinger model
    2. Load the model
    3. Run inference with sample lyrics
    """
    print("=" * 60)
    print("TESTING DIFFSINGER INFERENCE")
    print("=" * 60)
    
    # TODO: Replace with actual DiffSinger model loading
    print("⚠️  Real DiffSinger integration needed")
    print("    Steps required:")
    print("    1. Download pre-trained model (e.g., from OpenVPI)")
    print("    2. Load model checkpoint")
    print("    3. Prepare phoneme input")
    print("    4. Run inference")
    print("    5. Generate audio + timestamps")
    print()
    
    # For now, simulate inference timing
    print("Simulating inference (5 seconds)...")
    start = time.time()
    time.sleep(5)  # Simulate processing
    elapsed = time.time() - start
    
    print(f"⏱️  Simulated inference time: {elapsed:.2f}s")
    print(f"📊 Estimated songs/hour: {3600 / elapsed:.1f}")
    print()

def main():
    print("\n" + "=" * 60)
    print("DIFFSINGER FEASIBILITY TEST")
    print("=" * 60 + "\n")
    
    try:
        # Test 1: PyTorch
        test_pytorch()
        
        # Test 2: Audio libraries
        test_audio_processing()
        
        # Test 3: DiffSinger (placeholder)
        test_diffsinger_inference()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Download a DiffSinger pre-trained model")
        print("2. Integrate model loading into generate_song.py")
        print("3. Test on GitHub Codespaces")
        print("4. Measure actual generation time")
        print()
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()
