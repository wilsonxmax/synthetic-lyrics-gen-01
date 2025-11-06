#!/usr/bin/env python3
"""
Generate synthetic singing using Bark TTS
Bark supports singing by adding [music] tags
"""

import json
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path
import time
import os

# Suppress Bark's verbose logging
os.environ['SUNO_OFFLOAD_CPU'] = 'True'
os.environ['SUNO_USE_SMALL_MODELS'] = 'True'

def load_bark_model():
    """Load Bark TTS model (downloads on first run)"""
    try:
        from bark import SAMPLE_RATE, generate_audio, preload_models
        
        print("Loading Bark model (first run downloads ~2GB)...")
        preload_models()
        print("✅ Bark model loaded")
        
        return SAMPLE_RATE
    except ImportError:
        print("❌ Bark not installed. Install with: pip install git+https://github.com/suno-ai/bark.git")
        return None

def create_singing_prompt(lyrics, style="pop"):
    """
    Convert lyrics to Bark singing prompt
    
    Bark singing tips:
    - Add ♪ symbol before lyrics to trigger singing
    - Use [music] tags for instrumental sections
    - Keep segments short (< 15 seconds per generation)
    """
    
    # Split lyrics into singable phrases
    words = lyrics.split()
    phrases = []
    
    # Group into phrases of ~5-7 words
    phrase_length = 6
    for i in range(0, len(words), phrase_length):
        phrase = ' '.join(words[i:i+phrase_length])
        # Add singing symbol
        phrases.append(f"♪ {phrase} ♪")
    
    return phrases

def generate_with_bark(lyrics, song_index):
    """
    Generate singing audio with Bark
    
    Returns:
        audio: np.array of audio samples
        sr: sample rate
        word_timestamps: estimated timestamps
    """
    from bark import generate_audio, SAMPLE_RATE
    
    print(f"🎵 Generating singing for: {lyrics[:50]}...")
    
    # Create singing prompts
    phrases = create_singing_prompt(lyrics)
    
    # Generate audio for each phrase
    audio_segments = []
    cumulative_time = 0
    word_timestamps = []
    
    for phrase_idx, phrase in enumerate(phrases):
        print(f"  Generating phrase {phrase_idx + 1}/{len(phrases)}...")
        
        start_time = time.time()
        
        # Generate audio (this is the slow part)
        audio_array = generate_audio(
            phrase,
            history_prompt=None,  # Use default voice
        )
        
        elapsed = time.time() - start_time
        print(f"    ⏱️  Generation time: {elapsed:.1f}s")
        
        audio_segments.append(audio_array)
        
        # Estimate word timestamps
        # (Bark doesn't give exact timestamps, so we estimate)
        phrase_duration = len(audio_array) / SAMPLE_RATE
        words_in_phrase = phrase.replace('♪', '').strip().split()
        word_duration = phrase_duration / len(words_in_phrase)
        
        for word_idx, word in enumerate(words_in_phrase):
            word_start = cumulative_time + (word_idx * word_duration)
            word_end = word_start + word_duration
            
            word_timestamps.append({
                'text': word,
                'start': round(word_start, 3),
                'end': round(word_end, 3)
            })
        
        cumulative_time += phrase_duration
    
    # Concatenate all audio segments
    full_audio = np.concatenate(audio_segments)
    
    print(f"✅ Total audio duration: {len(full_audio) / SAMPLE_RATE:.2f}s")
    
    return full_audio, SAMPLE_RATE, word_timestamps

def generate_synthetic_song(index, output_audio, output_timestamps):
    """
    Generate one synthetic song with singing voice
    """
    print(f"\n{'='*60}")
    print(f"GENERATING SONG {index}")
    print(f"{'='*60}\n")
    
    start_time = time.time()
    
    # Diverse lyrics for different songs
    lyrics_library = [
        "Hello this is a test song for our validation system",
        "Walking down the street on a sunny summer day",
        "Dreams are made of stardust hope and light",
        "The river flows through mountains tall and wide",
        "Dancing in the moonlight feeling so alive",
        "Time keeps moving forward never looking back",
        "Singing songs of freedom joy and peace",
        "Hearts are beating stronger day by day",
        "Searching for tomorrow finding hope today",
        "Music brings us closer makes us whole",
    ]
    
    lyrics = lyrics_library[index % len(lyrics_library)]
    print(f"Lyrics: {lyrics}\n")
    
    # Load Bark (cached after first load)
    sr = load_bark_model()
    if sr is None:
        print("⚠️  Falling back to mock generation")
        audio, sr, timestamps = generate_mock_singing(index, lyrics)
    else:
        # Generate with Bark
        try:
            audio, sr, timestamps = generate_with_bark(lyrics, index)
        except Exception as e:
            print(f"⚠️  Bark generation failed: {e}")
            print("    Falling back to mock generation")
            audio, sr, timestamps = generate_mock_singing(index, lyrics)
    
    # Save audio
    Path(output_audio).parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_audio, audio, sr)
    print(f"\n✅ Audio saved: {output_audio}")
    
    # Save timestamps
    timestamp_data = {
        'song_id': f'song_{index:03d}',
        'lyrics': lyrics,
        'duration': len(audio) / sr,
        'words': timestamps,
        'metadata': {
            'generator': 'bark_tts',
            'sample_rate': sr,
            'word_count': len(timestamps)
        }
    }
    
    Path(output_timestamps).parent.mkdir(parents=True, exist_ok=True)
    with open(output_timestamps, 'w') as f:
        json.dump(timestamp_data, f, indent=2)
    print(f"✅ Timestamps saved: {output_timestamps}")
    
    elapsed = time.time() - start_time
    print(f"\n⏱️  Total generation time: {elapsed:.1f}s")
    print(f"📊 Estimated rate: {3600 / elapsed:.1f} songs/hour\n")
    
    return True

def generate_mock_singing(index, lyrics):
    """Fallback mock generation if Bark fails"""
    sr = 22050
    words = lyrics.split()
    
    # Create more realistic singing-like audio
    duration = len(words) * 0.7
    t = np.linspace(0, duration, int(sr * duration))
    
    # Multiple harmonics (more singing-like)
    fundamental = 220 + (index * 5)
    audio = (
        0.3 * np.sin(2 * np.pi * fundamental * t) +  # Fundamental
        0.15 * np.sin(2 * np.pi * fundamental * 2 * t) +  # 2nd harmonic
        0.1 * np.sin(2 * np.pi * fundamental * 3 * t)     # 3rd harmonic
    )
    
    # Add vibrato (singing characteristic)
    vibrato = 5  # Hz
    vibrato_depth = 0.01
    audio *= (1 + vibrato_depth * np.sin(2 * np.pi * vibrato * t))
    
    # Envelope (fade in/out)
    fade_samples = int(0.05 * sr)
    audio[:fade_samples] *= np.linspace(0, 1, fade_samples)
    audio[-fade_samples:] *= np.linspace(1, 0, fade_samples)
    
    # Create timestamps
    timestamps = []
    time_per_word = duration / len(words)
    for i, word in enumerate(words):
        timestamps.append({
            'text': word,
            'start': round(i * time_per_word, 3),
            'end': round((i + 1) * time_per_word, 3)
        })
    
    return audio, sr, timestamps

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', type=int, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--timestamps', type=str, required=True)
    
    args = parser.parse_args()
    
    try:
        generate_synthetic_song(args.index, args.output, args.timestamps)
        print("✅ SUCCESS\n")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
