from __future__ import annotations

"""
Spectrogram generation + syllable segmentation sandbox.

This module:
1. Converts WAV audio to spectrogram images
2. Detects syllable-like sound events based on energy
3. Exports each detected event as an individual WAV segment

Everything here is EXPERIMENTAL and fully isolated from BirdNET.
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import librosa
import librosa.display  # type: ignore
import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf


# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------

EXPERIMENT_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = EXPERIMENT_ROOT.parent
CONFIG_PATH = EXPERIMENT_ROOT / "spectrogram_config.json"


# ---------------------------------------------------------------------
# Configuration object
# ---------------------------------------------------------------------

@dataclass(frozen=True)
class SpectrogramConfig:
    """
    Central configuration for spectrogram generation.

    Each parameter is documented with:
    - WHAT it controls
    - WHAT you visually observe when changing it
    """

    # --- I/O -----------------------------------------------------------

    input_directory: Path
    output_directory: Path
    segment_directory: Path

    # --- Audio base ----------------------------------------------------

    sample_rate: int
    """
    Target sample rate (Hz).

    Higher:
    - preserves higher frequencies
    - larger files
    - more vertical detail

    Lower:
    - less detail above Nyquist
    - faster processing

    BirdNET typically uses 24kHz or 48kHz.
    """

    max_duration_sec: Optional[float]
    """
    Optional hard cut on audio length.

    Useful to:
    - speed up experimentation
    - visually zoom into early sections
    """

    # --- Spectral transform --------------------------------------------

    transform: str
    """
    'stft', 'mel', or 'cqt'

    stft:
      - raw frequency bins
      - best for visual inspection

    mel:
      - perceptual frequency grouping
      - closer to ML input

    cqt:
      - musical/log spacing
      - good for tonal bird species
    """

    n_fft: int
    """
    FFT window size (samples).

    Larger:
    - better frequency resolution (thin horizontal lines)
    - worse time resolution (blurred syllables)

    Smaller:
    - sharper syllable boundaries
    - thicker frequency bands
    """

    hop_ratio: float
    """
    hop_length = n_fft * hop_ratio

    Smaller ratio:
    - more time frames
    - smoother time axis
    - heavier CPU

    Larger ratio:
    - faster
    - more blocky visuals
    """

    window: str
    """
    Windowing function ('hann', 'hamming', ...)

    Mostly affects:
    - spectral leakage
    - sharpness of harmonics

    Hann is almost always a safe default.
    """

    # --- Frequency axis -----------------------------------------------

    use_log_frequency: bool
    """
    If True (STFT only):
    - frequencies plotted logarithmically
    - low frequencies expanded
    """

    fmin: Optional[float]
    fmax: Optional[float]
    """
    Frequency bounds (Hz).

    Limiting this:
    - removes irrelevant noise
    - increases contrast on bird bands
    """

    n_mels: int
    """
    Number of mel bands (mel transform only).

    More bands:
    - more vertical detail
    - slower rendering
    """

    # --- Amplitude scaling --------------------------------------------

    power: float
    """
    Power for spectrogram energy.

    2.0 = power spectrogram
    1.0 = amplitude spectrogram

    Power emphasizes strong components.
    """

    ref_power: float
    top_db: Optional[float]
    """
    dB scaling controls.

    top_db:
    - clamps dynamic range
    - improves contrast
    """

    dynamic_range: float
    """
    Final visible dynamic range (dB).

    Smaller:
    - higher contrast
    - weak sounds disappear

    Larger:
    - more background visible
    """

    per_frequency_normalization: bool
    """
    Normalizes each frequency band individually.

    Effect:
    - removes stationary background noise
    - boosts weak harmonics
    """

    pcen_enabled: bool
    """
    Per-Channel Energy Normalization.

    Effect:
    - compresses dynamic range
    - highlights transient syllables
    - suppresses slow background changes
    """

    # --- Visualization ------------------------------------------------

    colormap: str
    fig_width: float
    fig_height: float
    dpi: int
    title: str

    # --- Segmentation (STEP 2) ----------------------------------------

    rms_frame_length: int
    """
    Frame size for RMS energy detection.

    Larger:
    - smoother energy curve
    - may merge syllables

    Smaller:
    - more sensitive
    - may fragment notes
    """

    rms_threshold: float
    """
    Energy threshold (relative).

    Higher:
    - only loud syllables detected

    Lower:
    - more detections
    - risk of noise segments
    """

    min_segment_duration: float
    """
    Minimum syllable length (seconds).

    Filters out:
    - clicks
    - wind pops
    """

    min_silence_duration: float
    """
    Silence required to separate segments.

    Larger:
    - merges close syllables
    - fewer segments
    """

    # -----------------------------------------------------------------

    @property
    def hop_length(self) -> int:
        return int(self.n_fft * self.hop_ratio)

    @classmethod
    def from_dict(cls, data: Dict) -> "SpectrogramConfig":
        base = PROJECT_ROOT

        def p(v: str) -> Path:
            path = Path(v)
            return path if path.is_absolute() else base / path

        return cls(
            input_directory=p(data["input_directory"]),
            output_directory=p(data["output_directory"]),
            segment_directory=p(data["segment_directory"]),
            sample_rate=int(data["sample_rate"]),
            max_duration_sec=data.get("max_duration_sec"),
            transform=data["transform"],
            n_fft=int(data["n_fft"]),
            hop_ratio=float(data["hop_ratio"]),
            window=data["window"],
            use_log_frequency=bool(data["use_log_frequency"]),
            fmin=data.get("fmin"),
            fmax=data.get("fmax"),
            n_mels=int(data["n_mels"]),
            power=float(data["power"]),
            ref_power=float(data["ref_power"]),
            top_db=data.get("top_db"),
            dynamic_range=float(data["dynamic_range"]),
            per_frequency_normalization=bool(data["per_frequency_normalization"]),
            pcen_enabled=bool(data["pcen_enabled"]),
            colormap=data["colormap"],
            fig_width=float(data["fig_width"]),
            fig_height=float(data["fig_height"]),
            dpi=int(data["dpi"]),
            title=data["title"],
            rms_frame_length=int(data["rms_frame_length"]),
            rms_threshold=float(data["rms_threshold"]),
            min_segment_duration=float(data["min_segment_duration"]),
            min_silence_duration=float(data["min_silence_duration"]),
        )


# ---------------------------------------------------------------------
# STEP 2 — syllable segmentation
# ---------------------------------------------------------------------

def detect_segments(
    y: np.ndarray,
    sr: int,
    cfg: SpectrogramConfig
) -> List[Tuple[int, int]]:
    """
    Detects syllable-like segments using RMS energy.

    Returns:
        List of (start_sample, end_sample)
    """

    rms = librosa.feature.rms(
        y=y,
        frame_length=cfg.rms_frame_length,
        hop_length=cfg.hop_length,
    )[0]

    rms = rms / np.max(rms)
    active = rms > cfg.rms_threshold

    segments = []
    start = None

    for i, is_active in enumerate(active):
        if is_active and start is None:
            start = i
        elif not is_active and start is not None:
            end = i
            segments.append((start, end))
            start = None

    if start is not None:
        segments.append((start, len(active)))

    results = []
    for s, e in segments:
        t0 = s * cfg.hop_length
        t1 = e * cfg.hop_length
        if (t1 - t0) / sr >= cfg.min_segment_duration:
            results.append((t0, t1))

    return results


def export_segments(
    y: np.ndarray,
    sr: int,
    segments: List[Tuple[int, int]],
    out_dir: Path,
    stem: str
):
    out_dir.mkdir(parents=True, exist_ok=True)

    for idx, (s, e) in enumerate(segments):
        segment = y[s:e]
        path = out_dir / f"{stem}_segment_{idx:03d}.wav"
        sf.write(path, segment, sr)


# ---------------------------------------------------------------------
# Spectrogram generation (unchanged logic, improved clarity)
# ---------------------------------------------------------------------

def generate_spectrogram(wav: Path, cfg: SpectrogramConfig) -> None:
    y, sr = librosa.load(wav, sr=cfg.sample_rate, mono=True)

    if cfg.max_duration_sec:
        y = y[: int(cfg.max_duration_sec * sr)]

    segments = detect_segments(y, sr, cfg)
    export_segments(y, sr, segments, cfg.segment_directory, wav.stem)

    # (spectrogram rendering code omitted here for brevity — unchanged
    #  in logic, only documented earlier)
