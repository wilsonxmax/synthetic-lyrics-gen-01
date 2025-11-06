#!/usr/bin/env python3
"""
Generate synthetic singing using Bark TTS
"""

import json
import argparse
import numpy as np
import soundfile as sf
from pathlib import Path
import time
import os
import sys

# Bark environment configuration
os.environ['SUNO_OFFLOAD_CPU'] = 'True'
os.environ['SUNO_USE_SMALL_MODELS'] = 'True'

def load_bark_model():
    """Load Bark TTS model"""
    try:
        from bark import SAMPLE_RATE, generate_audio, preload_models
        
        print("🔧 Loading Bark model...")
        print("   (First run downloads ~2GB of model files)")
        start = time.time()
        
        preload_models()
        
        elapsed = time.time() - start
        print(f"✅ Bark model loaded in {elapsed:.1f}s\n")
        
        return SAMPLE_RATE
    except ImportError as e:
        print(f"❌ Failed to import Bark: {e}")
        print("   Falling back to mock generation")
        return None
    except Exception as e:
        print(f"⚠️  Bark model loading failed: {e}")
        print("   Falling back to mock generation")
        return None

def create_singing_prompt(lyrics, style="pop"):
    """Convert lyrics to Bark singing prompt"""
    words = lyrics.split()
    phrases = []
    
    # Group into phrases of ~6 words
    phrase_length = 6
    for i in range(0, len(words), phrase_length):
        phrase = ' '.join(words[i:i+phrase_length])
        phrases.append(f"♪ {phrase} ♪")
    
    return phrases

def generate_with_bark(lyrics, song_index):
    """Generate singing audio with Bark"""
    from bark import generate_audio, SAMPLE_RATE
    
    print(f"🎵 Generating singing audio...")
    print(f"   Lyrics: {lyrics}\n")
    
    phrases = create_singing_prompt(lyrics)
    
    audio_segments = []
    cumulative_time = 0
    word_timestamps = []
    
    for phrase_idx, phrase in enumerate(phrases):
        print(f"  📝 Phrase {phrase_idx + 1}/{len(phrases)}: {phrase}")
        
        start_time = time.time()
        
        try:
            # Generate audio
            audio_array = generate_audio(
                phrase,
                history_prompt=None,
            )
            
            elapsed = time.time() - start_time
            duration = len(audio_array) / SAMPLE_RATE
            
            print(f"     ⏱️  Generation time: {elapsed:.1f}s")
            print(f"     🎵 Audio duration: {duration:.2f}s")
            print(f"     📊 Realtime factor: {duration/elapsed:.2f}x\n")
            
            audio_segments.append(audio_array)
            
            # Estimate word timestamps
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
            
        except Exception as e:
            print(f"     ⚠️  Phrase generation failed: {e}")
            raise
    
    # Concatenate all audio
    full_audio = np.concatenate(audio_segments)
    
    total_duration = len(full_audio) / SAMPLE_RATE
    print(f"✅ Generation complete!")
    print(f"   Total duration: {total_duration:.2f}s")
    print(f"   Words generated: {len(word_timestamps)}\n")
    
    return full_audio, SAMPLE_RATE, word_timestamps

def generate_mock_singing(index, lyrics):
    """Enhanced mock generation with singing-like characteristics"""
    print("⚠️  Using enhanced mock generation (Bark fallback)")
    
    sr = 22050
    words = lyrics.split()
    
    # More realistic timing
    duration = len(words) * 0.8  # 0.8s per word
    t = np.linspace(0, duration, int(sr * duration))
    
    # Create harmonics (singing-like)
    fundamental = 220 + (index * 5)
    audio = (
        0.30 * np.sin(2 * np.pi * fundamental * t) +
        0.15 * np.sin(2 * np.pi * fundamental * 2 * t) +
        0.08 * np.sin(2 * np.pi * fundamental * 3 * t)
    )
    
    # Add vibrato
    vibrato_rate = 5.5
    vibrato_depth = 0.015
    audio *= (1 + vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t))
    
    # Envelope
    fade = int(0.05 * sr)
    audio[:fade] *= np.linspace(0, 1, fade)
    audio[-fade:] *= np.linspace(1, 0, fade)
    
    # Timestamps
    timestamps = []
    time_per_word = duration / len(words)
    for i, word in enumerate(words):
        timestamps.append({
            'text': word,
            'start': round(i * time_per_word, 3),
            'end': round((i + 1) * time_per_word, 3)
        })
    
    return audio, sr, timestamps

def generate_synthetic_song(index, output_audio, output_timestamps):
    """Generate one synthetic song"""
    print("\n" + "="*60)
    print(f"GENERATING SONG {index}")
    print("="*60 + "\n")
    
    overall_start = time.time()
    
    # Diverse lyrics library
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
        "Music brings us closer makes us whole and free",
    ]
    
    lyrics = lyrics_library[(index - 1) % len(lyrics_library)]
    
    # Try Bark, fallback to mock
    sr = load_bark_model()
    
    if sr is not None:
        try:
            audio, sr, timestamps = generate_with_bark(lyrics, index)
            generator = "bark_tts"
        except Exception as e:
            print(f"\n⚠️  Bark generation failed: {e}")
            print("   Falling back to mock generation\n")
            audio, sr, timestamps = generate_mock_singing(index, lyrics)
            generator = "mock_fallback"
    else:
        audio, sr, timestamps = generate_mock_singing(index, lyrics)
        generator = "mock_no_bark"
    
    # Save audio
    Path(output_audio).parent.mkdir(parents=True, exist_ok=True)
    sf.write(output_audio, audio, sr)
    print(f"💾 Audio saved: {output_audio}")
    
    # Save timestamps
    timestamp_data = {
        'song_id': f'song_{index:03d}',
        'lyrics': lyrics,
        'duration': round(len(audio) / sr, 3),
        'words': timestamps,
        'metadata': {
            'generator': generator,
            'sample_rate': sr,
            'word_count': len(timestamps),
            'generation_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
        }
    }
    
    Path(output_timestamps).parent.mkdir(parents=True, exist_ok=True)
    with open(output_timestamps, 'w') as f:
        json.dump(timestamp_data, f, indent=2)
    print(f"💾 Timestamps saved: {output_timestamps}")
    
    # Final stats
    overall_elapsed = time.time() - overall_start
    audio_duration = len(audio) / sr
    
    print("\n" + "="*60)
    print("GENERATION COMPLETE")
    print("="*60)
    print(f"⏱️  Total time: {overall_elapsed:.1f}s")
    print(f"🎵 Audio duration: {audio_duration:.2f}s")
    print(f"📊 Realtime factor: {audio_duration / overall_elapsed:.2f}x")
    print(f"📊 Estimated rate: {3600 / overall_elapsed:.1f} songs/hour")
    print(f"📊 Time for 100 songs: {(100 * overall_elapsed) / 3600:.1f} hours")
    print("="*60 + "\n")
    
    return True

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', type=int, required=True)
    parser.add_argument('--output', type=str, required=True)
    parser.add_argument('--timestamps', type=str, required=True)
    
    args = parser.parse_args()
    
    try:
        generate_synthetic_song(args.index, args.output, args.timestamps)
        print("✅ SUCCESS\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ GENERATION FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
