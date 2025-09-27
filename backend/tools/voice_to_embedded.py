import librosa
import numpy as np
import json
import hashlib
from pathlib import Path
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_audio_hash(file_path):
    """Generate a hash of the audio file for consistency"""
    with open(file_path, 'rb') as f:
        audio_data = f.read()
        return hashlib.md5(audio_data).hexdigest()

def generate_100d_voice_embedding(file_path):
    """Generate consistent 100-dimensional voice embedding based on audio features"""
    try:
        print(f"Processing audio file: {file_path}")
        
        # Load audio file (limit to 30 seconds for consistency)
        y, sr = librosa.load(file_path, duration=30)
        print(f"Loaded audio: {len(y)} samples at {sr} Hz")
        
        features = []
        
        # 1-13: MFCC features (mean values)
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
        for i in range(13):
            features.append(np.mean(mfcc[i]))
        
        # 14-26: MFCC standard deviations
        for i in range(13):
            features.append(np.std(mfcc[i]))
        
        # 27-38: Chroma features (pitch class profiles)
        chroma = librosa.feature.chroma(y=y, sr=sr)
        for i in range(12):
            features.append(np.mean(chroma[i]))
        
        # 39-45: Spectral features
        spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
        spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
        spectral_bandwidth = librosa.feature.spectral_bandwidth(y=y, sr=sr)
        zero_crossings = librosa.feature.zero_crossing_rate(y)
        
        features.extend([
            np.mean(spectral_centroids),
            np.std(spectral_centroids),
            np.mean(spectral_rolloff),
            np.std(spectral_rolloff),
            np.mean(spectral_bandwidth),
            np.std(spectral_bandwidth),
            np.mean(zero_crossings)
        ])
        
        # 46-52: Tempo and rhythm features
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        onset_frames = librosa.onset.onset_detect(y=y, sr=sr)
        features.extend([
            tempo / 200.0,  # Normalized tempo
            len(beats) / (len(y) / sr) if len(y) > 0 else 0,  # Beat density
            len(onset_frames) / (len(y) / sr) if len(y) > 0 else 0,  # Onset density
            np.std(np.diff(beats)) if len(beats) > 1 else 0,  # Beat consistency
            np.mean(librosa.onset.onset_strength(y=y, sr=sr)),  # Onset strength
            np.std(librosa.onset.onset_strength(y=y, sr=sr)),
            np.mean(np.diff(onset_frames)) if len(onset_frames) > 1 else 0
        ])
        
        # 53-65: Energy and amplitude features
        rms = librosa.feature.rms(y=y)
        features.extend([
            np.mean(rms),
            np.std(rms),
            np.mean(y**2),  # Power
            np.std(y**2),
            np.max(np.abs(y)),  # Peak amplitude
            np.mean(np.abs(y)),  # Mean amplitude
            np.percentile(y, 95),  # 95th percentile
            np.percentile(y, 75),  # 75th percentile
            np.percentile(y, 25),  # 25th percentile
            np.percentile(y, 5),   # 5th percentile
            len(y) / sr,  # Duration
            np.mean(np.abs(np.diff(y))),  # Spectral flux
            np.std(np.abs(np.diff(y)))
        ])
        
        # 66-78: Mel-scale spectral features
        mel_spectrogram = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=13)
        for i in range(13):
            features.append(np.mean(mel_spectrogram[i]))
        
        # 79-85: Harmonic and percussive features
        y_harmonic, y_percussive = librosa.effects.hpss(y)
        features.extend([
            np.mean(y_harmonic**2),  # Harmonic energy
            np.mean(y_percussive**2),  # Percussive energy
            np.std(y_harmonic),
            np.std(y_percussive),
            np.corrcoef(y_harmonic, y_percussive)[0,1] if len(y_harmonic) == len(y_percussive) else 0,
            np.mean(np.abs(y_harmonic)),
            np.mean(np.abs(y_percussive))
        ])
        
        # 86-90: Pitch features (F0)
        f0 = librosa.yin(y, fmin=50, fmax=400)  # Typical human voice range
        f0_clean = f0[f0 > 0]  # Remove unvoiced frames
        
        if len(f0_clean) > 0:
            features.extend([
                np.mean(f0_clean),  # Average pitch
                np.std(f0_clean),   # Pitch variance
                np.min(f0_clean),   # Lowest pitch
                np.max(f0_clean),   # Highest pitch
                np.percentile(f0_clean, 75) - np.percentile(f0_clean, 25),  # Pitch range
            ])
        else:
            features.extend([0, 0, 0, 0, 0])
        
        # 91-94: Additional spectral features
        stft = librosa.stft(y)
        magnitude = np.abs(stft)
        features.extend([
            np.mean(magnitude),
            np.std(magnitude),
            np.mean(np.sum(magnitude, axis=0)),  # Spectral energy per frame
            np.std(np.sum(magnitude, axis=0))
        ])
        
        # 95-100: Voice quality indicators
        # Jitter approximation (pitch period variation)
        if len(f0_clean) > 1:
            features.append(np.std(np.diff(f0_clean)) / np.mean(f0_clean) if np.mean(f0_clean) > 0 else 0)
        else:
            features.append(0)
        
        # Shimmer approximation (amplitude variation)
        frame_energies = np.sum(magnitude**2, axis=0)
        if len(frame_energies) > 1:
            features.append(np.std(np.diff(frame_energies)) / np.mean(frame_energies) if np.mean(frame_energies) > 0 else 0)
        else:
            features.append(0)
        
        # Harmonics-to-noise ratio approximation
        harmonic_energy = np.mean(y_harmonic**2)
        noise_energy = np.mean((y - y_harmonic)**2)
        hnr = harmonic_energy / (noise_energy + 1e-10)
        features.append(np.log10(hnr + 1e-10))
        
        # Spectral slope
        freqs = librosa.fft_frequencies(sr=sr)
        spectral_slope = np.polyfit(freqs[:len(freqs)//2], 
                                  np.mean(magnitude[:len(freqs)//2], axis=1), 1)[0]
        features.append(spectral_slope)
        
        # Voice activity (speech vs silence ratio)
        voice_activity = np.mean(rms > np.percentile(rms, 30))
        features.append(voice_activity)
        
        # Spectral centroid variation
        features.append(np.var(spectral_centroids))
        
        # Ensure exactly 100 features
        features = features[:100]
        while len(features) < 100:
            features.append(0.0)
        
        print(f"Extracted {len(features)} audio features")
        
        # Normalize to [-1, 1] range and handle any NaN/inf values
        features = np.array(features, dtype=np.float64)
        features = np.nan_to_num(features, nan=0.0, posinf=1.0, neginf=-1.0)
        
        # Z-score normalization then clip to [-1, 1]
        if np.std(features) > 0:
            features = (features - np.mean(features)) / np.std(features)
        features = np.clip(features, -1, 1)
        
        print(f"Successfully generated 100D embedding")
        
        return {
            "voice_embedding": features.round(6).tolist(),
            "method": "audio_features",
            "dimensions": len(features),
            "file_hash": get_audio_hash(file_path)
        }
        
    except ImportError:
        print("Error: librosa not installed. Install with: pip install librosa")
        return generate_hash_based_embedding(file_path, "librosa not installed")
    except Exception as e:
        print(f"Audio feature extraction failed: {e}")
        return generate_hash_based_embedding(file_path, str(e))

def generate_hash_based_embedding(file_path, error_msg=""):
    """Generate a deterministic 100-dimensional embedding based on file hash"""
    print(f"Using hash-based fallback embedding for: {file_path}")
    
    audio_hash = get_audio_hash(file_path)
    
    # Use hash to seed deterministic values
    import random
    random.seed(int(audio_hash[:8], 16))  # Use first 8 chars of hash as seed
    
    embedding = [round(random.uniform(-1.0, 1.0), 6) for _ in range(100)]
    
    result = {
        "voice_embedding": embedding,
        "method": "hash_based",
        "dimensions": 100,
        "file_hash": audio_hash
    }
    
    if error_msg:
        result["error"] = error_msg
        
    return result

def main():
    # Generate 100-dimensional voice embedding
    print("=== Generating 100D Voice Embedding ===")
    
    file_path = '../prototype/Voice1.mp3'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return
    
    result = generate_100d_voice_embedding(file_path)
    
    print(f"Embedding dimensions: {len(result.get('voice_embedding', []))}")
    print(f"Method: {result.get('method', 'unknown')}")
    print(f"First 10 values: {result['voice_embedding'][:10]}")
    print(f"Last 10 values: {result['voice_embedding'][-10:]}")
    
    # Test consistency - run same file multiple times
    print("\n=== Testing Consistency ===")
    result2 = generate_100d_voice_embedding(file_path)
    result3 = generate_100d_voice_embedding(file_path)
    
    consistent = (result['voice_embedding'] == result2['voice_embedding'] == result3['voice_embedding'])
    print(f"Three runs identical: {consistent}")
    
    if consistent:
        print("✅ Embeddings are perfectly consistent!")
    else:
        print("❌ Embeddings differ between runs")
        
        # Show differences for debugging
        diff_12 = sum(1 for a, b in zip(result['voice_embedding'], result2['voice_embedding']) if a != b)
        diff_13 = sum(1 for a, b in zip(result['voice_embedding'], result3['voice_embedding']) if a != b)
        print(f"Differences: Run1 vs Run2: {diff_12}/100, Run1 vs Run3: {diff_13}/100")
    
    # Display sample of full embedding
    print(f"\n=== Sample Embedding (for database storage) ===")
    sample_result = {
        "voice_embedding": result['voice_embedding'],
        "method": result['method'],
        "dimensions": result['dimensions'],
        "file_hash": result.get('file_hash', 'unknown')[:8]  # Show first 8 chars of hash
    }
    print("JSON format (truncated):")
    print(json.dumps(sample_result, indent=2))
    
    return result

if __name__ == "__main__":
    main()