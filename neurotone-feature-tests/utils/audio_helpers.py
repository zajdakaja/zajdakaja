import numpy as np
import librosa
from pathlib import Path


def load_wav(path, sr=16000):
    """Load a WAV file and return audio time series and sampling rate."""
    path = Path(path)
    y, sr = librosa.load(path, sr=sr)
    return y, sr


def extract_mfcc(y, sr, n_mfcc=13):
    """Extract MFCC features from audio time series."""
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    return mfcc


def short_time_energy(y, frame_length=2048, hop_length=512):
    """Compute short-time energy of the signal."""
    rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)
    return rms


def estimate_pitch(y, sr, frame_length=2048, hop_length=512):
    """Estimate pitch using librosa's piptrack function."""
    pitches, magnitudes = librosa.piptrack(y=y, sr=sr, n_fft=frame_length, hop_length=hop_length)
    pitch_track = pitches[magnitudes.argmax(axis=0), range(magnitudes.shape[1])]
    return pitch_track
