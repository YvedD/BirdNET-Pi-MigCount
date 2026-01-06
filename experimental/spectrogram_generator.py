from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional
import numpy as np
import librosa
import librosa.display
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import soundfile as sf  # Voor segment export

EXPERIMENT_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = EXPERIMENT_ROOT.parent
CONFIG_PATH = EXPERIMENT_ROOT / "spectrogram_config.json"


@dataclass
class SpectrogramConfig:
    """All spectrogram and segmentation parameters with full explanation."""
    input_directory: Path
    output_directory: Path
    segment_directory: Path
    transform: str
    sample_rate: int
    n_fft: int
    hop_ratio: float
    hop_length: int
    window: str
    use_log_frequency: bool
    fmin: Optional[float]
    fmax: Optional[float]
    n_mels: int
    power: float
    pcen_enabled: bool
    per_frequency_normalization: bool
    ref_power: float
    top_db: Optional[float]
    dynamic_range: float
    contrast_percentile: Optional[float]
    colormap: str
    fig_width: float
    fig_height: float
    dpi: int
    max_duration_sec: Optional[float]
    title: str
    # Segment detection parameters
    rms_frame_length: int
    rms_threshold: float
    min_segment_duration: float
    min_silence_duration: float

    @classmethod
    def from_dict(cls, data: Dict):
        base = PROJECT_ROOT
        def _resolve(p): return Path(p) if Path(p).is_absolute() else (base / Path(p))
        return cls(
            input_directory=_resolve(data["input_directory"]),
            output_directory=_resolve(data["output_directory"]),
            segment_directory=_resolve(data.get("segment_directory", "experimental/segments")),
            transform=data.get("transform", "mel"),
            sample_rate=int(data["sample_rate"]),
            n_fft=int(data["n_fft"]),
            hop_ratio=float(data.get("hop_ratio", 0.125)),
            hop_length=int(data.get("hop_length", int(int(data["n_fft"])*float(data.get("hop_ratio", 0.125))))),
            window=data.get("window", "hann"),
            use_log_frequency=bool(data.get("use_log_frequency", True)),
            fmin=float(data.get("fmin", 200)),
            fmax=float(data.get("fmax", 12000)),
            n_mels=int(data.get("n_mels", 512)),
            power=float(data.get("power", 2.0)),
            pcen_enabled=bool(data.get("pcen_enabled", False)),
            per_frequency_normalization=bool(data.get("per_frequency_normalization", False)),
            ref_power=float(data.get("ref_power", 1.0)),
            top_db=float(data.get("top_db", 45.0)) if data.get("top_db") else None,
            dynamic_range=float(data.get("dynamic_range", 80)),
            contrast_percentile=float(data.get("contrast_percentile", 99.5)) if data.get("contrast_percentile") else None,
            colormap=data.get("colormap", "gray_r"),
            fig_width=float(data.get("fig_width", 12)),
            fig_height=float(data.get("fig_height", 6)),
            dpi=int(data.get("dpi", 300)),
            max_duration_sec=float(data.get("max_duration_sec", 0)) if data.get("max_duration_sec") else None,
            title=data.get("title", "Experimental Spectrogram"),
            rms_frame_length=int(data.get("rms_frame_length", 1024)),
            rms_threshold=float(data.get("rms_threshold", 0.1)),
            min_segment_duration=float(data.get("min_segment_duration", 0.05)),
            min_silence_duration=float(data.get("min_silence_duration", 0.03)),
        )


def load_config(path=CONFIG_PATH):
    import json
    with path.open("r", encoding="utf-8") as f:
        return SpectrogramConfig.from_dict(json.load(f))


def _trim_audio(y: np.ndarray, sr: int, max_sec: Optional[float]) -> np.ndarray:
    if not max_sec:
        return y
    return y[:int(sr*max_sec)]


def detect_segments(y: np.ndarray, cfg: SpectrogramConfig):
    """
    Detect segments in audio using RMS energy:
    - rms_threshold scales the frame energy
    - min_segment_duration: minimum duration for a segment to be valid
    - min_silence_duration: minimum silence to split segments
    Returns list of tuples (start_sample, end_sample)
    """
    rms = librosa.feature.rms(y=y, frame_length=cfg.rms_frame_length, hop_length=int(cfg.n_fft*cfg.hop_ratio))[0]
    times = librosa.frames_to_samples(np.arange(len(rms)), hop_length=int(cfg.n_fft*cfg.hop_ratio))
    mask = rms > cfg.rms_threshold * np.max(rms)
    segments = []
    start = None
    for i, m in enumerate(mask):
        if m and start is None:
            start = times[i]
        elif not m and start is not None:
            end = times[i]
            if (end-start)/cfg.sample_rate >= cfg.min_segment_duration:
                segments.append((start, end))
            start = None
    if start is not None:
        segments.append((start, len(y)))
    return segments


def export_segments(y: np.ndarray, sr: int, segments: List[tuple], output_dir: Path, base_name: str):
    """Write each detected segment as a separate WAV file."""
    output_dir.mkdir(parents=True, exist_ok=True)
    paths = []
    for i, (start, end) in enumerate(segments):
        segment = y[start:end]
        path = output_dir / f"{base_name}_seg{i+1}.wav"
        sf.write(path, segment, sr)
        paths.append(path)
    return paths


def generate_spectrogram(wav_path: Path, cfg: SpectrogramConfig):
    """Generate spectrogram with segment overlay and export segments."""
    y, sr = librosa.load(wav_path, sr=cfg.sample_rate, mono=True)
    y = _trim_audio(y, sr, cfg.max_duration_sec)
    hop_length = int(cfg.n_fft * cfg.hop_ratio)

    # Transform
    if cfg.transform.lower() == "mel":
        S = librosa.feature.melspectrogram(
            y=y, sr=sr, n_fft=cfg.n_fft, hop_length=hop_length,
            window=cfg.window, n_mels=cfg.n_mels, fmin=cfg.fmin, fmax=cfg.fmax, power=cfg.power
        )
        if cfg.pcen_enabled:
            S = librosa.pcen(S + 1e-6, sr=sr, hop_length=hop_length)
        S_db = librosa.power_to_db(S, ref=cfg.ref_power, top_db=cfg.top_db)
        y_axis = "mel"
    else:
        S_db = librosa.amplitude_to_db(np.abs(librosa.stft(y, n_fft=cfg.n_fft, hop_length=hop_length, window=cfg.window)), ref=cfg.ref_power, top_db=cfg.top_db)
        y_axis = "log" if cfg.use_log_frequency else "linear"

    # Normalize per frequency
    if cfg.per_frequency_normalization:
        S_db = (S_db - S_db.mean(axis=1, keepdims=True)) / (S_db.std(axis=1, keepdims=True) + 1e-6)

    # Detect segments
    segments = detect_segments(y, cfg)
    export_segments(y, sr, segments, cfg.segment_directory, wav_path.stem)

    # Plot
    fig, ax = plt.subplots(figsize=(cfg.fig_width, cfg.fig_height), dpi=cfg.dpi)
    img = librosa.display.specshow(S_db, sr=sr, hop_length=hop_length, x_axis="time", y_axis=y_axis, fmin=cfg.fmin, fmax=cfg.fmax, cmap=cfg.colormap, ax=ax)
    
    # Overlay segments
    for start, end in segments:
        ax.add_patch(Rectangle((start/sr, cfg.fmin), (end-start)/sr, (cfg.fmax-cfg.fmin if cfg.fmax else S_db.shape[0]),
                               edgecolor="red", facecolor="none", linewidth=1.5))
    
    ax.set_title(cfg.title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    cbar = fig.colorbar(img, ax=ax, format="%+2.0f dB")
    cbar.set_label("Amplitude (dB)")
    fig.tight_layout()

    output_path = cfg.output_directory / f"{wav_path.stem}_spectrogram.png"
    cfg.output_directory.mkdir(parents=True, exist_ok=True)
    fig.savefig(output_path, dpi=cfg.dpi)
    plt.close(fig)
    return output_path
