from typing import Tuple

import numpy as np
from scipy import signal

from .utils import clamp_frequency_range, validate_window_name

EPS = np.finfo(np.float32).eps


def _power_to_db(magnitude: np.ndarray, db_range: float) -> np.ndarray:
    reference = np.maximum(np.max(magnitude), EPS)
    db = 20.0 * np.log10(np.maximum(magnitude, EPS) / reference)
    floor = -abs(db_range)
    return np.clip(db, floor, 0.0)


def compute_spectrogram(
    audio: np.ndarray,
    sample_rate: int,
    n_fft: int,
    hop_length: int,
    window: str,
    fmin: float = None,
    fmax: float = None,
    per_freq_norm: bool = False,
    db_range: float = 60.0,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Compute a linear STFT spectrogram with optional per-frequency normalization.
    Returns (freqs, times, db_spectrogram).
    """
    if audio.ndim != 1:
        raise ValueError("audio must be mono")

    window_name = validate_window_name(window, ("hann", "blackman", "hamming"))
    overlap = n_fft - hop_length
    freqs, times, stft = signal.stft(
        audio,
        fs=sample_rate,
        window=window_name,
        nperseg=n_fft,
        noverlap=overlap,
        boundary=None,
        padded=False,
    )

    magnitude = np.abs(stft)

    if per_freq_norm:
        scale = magnitude.mean(axis=1, keepdims=True)
        magnitude = magnitude / (scale + EPS)

    db_spectrogram = _power_to_db(magnitude, db_range=db_range)

    low, high = clamp_frequency_range(fmin or 0.0, fmax or (sample_rate / 2.0), sample_rate)
    mask = (freqs >= low) & (freqs <= high)
    return freqs[mask], times, db_spectrogram[mask, :]
