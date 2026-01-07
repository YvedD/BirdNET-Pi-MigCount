"""
Enhanced spectrogram generator with RMS-based segment detection and sigmoid soft-thresholding.

This module generates spectrogram PNGs from WAV files with additional features:
- Detection of audio segments (vocalizations, syllables, bird notes)
- Overlay of detected segments on the spectrogram
- Sigmoid-based soft-thresholding to reduce vertical streak artifacts

This module is sandboxed: it only consumes WAVs from input_directory and writes PNGs to output_directory.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import librosa
import librosa.display  # type: ignore
import matplotlib
import matplotlib.pyplot as plt
from matplotlib import colors as mcolors
import numpy as np
from scipy import signal
from matplotlib.patches import Rectangle
from PIL import Image, UnidentifiedImageError

EXPERIMENT_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = EXPERIMENT_ROOT.parent
CONFIG_PATH = EXPERIMENT_ROOT / "spectrogram_config.json"
NOISE_PROFILE_PERCENTILE = 25


def _calculate_hop_length(n_fft: int, hop_ratio: float, provided: Optional[int] = None) -> int:
    hop_from_ratio = int(n_fft * hop_ratio)
    return provided if provided and provided > 0 else hop_from_ratio


def _lighten_colormap(name: str, floor: float = 0.2) -> mcolors.Colormap:
    base = plt.get_cmap(name)
    samples = np.linspace(floor, 1.0, base.N)
    light_cmap = mcolors.LinearSegmentedColormap.from_list(f"{name}_soft", base(samples))
    try:
        matplotlib.colormaps.register(light_cmap)
    except ValueError:
        pass
    return light_cmap


def _resolve_colormap(name: str):
    if name in plt.colormaps():
        return plt.get_cmap(name)
    if name == "soft_gray":
        return _lighten_colormap("gray_r", 0.25)
    if name.endswith("_light") and name[:-6] in plt.colormaps():
        return _lighten_colormap(name[:-6], 0.25)
    return plt.get_cmap("viridis")


def _save_png(fig_obj: plt.Figure, path: Path, dpi: int) -> None:
    fig_obj.savefig(path, dpi=dpi, bbox_inches="tight", format="png")


def _cleanup_paths(*paths: Path) -> None:
    for path in paths:
        path.unlink(missing_ok=True)


@dataclass
class SpectrogramConfig:
    """
    Container for JSON-driven spectrogram parameters.

    Defaults are tuned for bird song / syllable visualization:
    - good time resolution
    - sharp spectral contrast
    - PCEN-compatible
    - lightweight enough for Raspberry Pi
    """

    # I/O
    input_directory: Path
    output_directory: Path

    # Transform
    transform: str = "mel"  # 'mel', 'stft', or 'cqt'
    sample_rate: int = 48000

    # FFT / time-frequency resolution
    n_fft: int = 4096
    hop_ratio: float = 0.125  # hop_length = n_fft * hop_ratio
    hop_length: int = 512  # explicit, kept in sync with hop_ratio
    window: str = "hann"

    # Frequency axis
    use_log_frequency: bool = False  # mel already provides perceptual scaling
    fmin: Optional[float] = 2000.0
    fmax: Optional[float] = 9500.0

    # Mel configuration
    n_mels: int = 256
    power: float = 1.0  # IMPORTANT: PCEN expects ~1.0, not 2.0

    # PCEN
    pcen_enabled: bool = False
    pcen_bias: float = 3.0        # lighter background
    pcen_gain: float = 0.7        # less aggressive normalization

    # Linear / dB pipeline (ignored when PCEN is enabled)
    per_frequency_normalization: bool = False
    ref_power: float = 1.0
    top_db: Optional[float] = 60.0
    dynamic_range: float = 45.0
    contrast_percentile: Optional[float] = None

    # Visualization
    colormap: str = "gray"
    fig_width: float = 10.0
    fig_height: float = 4.5
    dpi: int = 150
    title: str = "Experimental Spectrogram"

    # Processing limits
    max_duration_sec: Optional[float] = None

    # Optional preprocessing
    noise_reduction: bool = False  # lightweight spectral gating
    high_pass_filter: bool = False
    high_pass_cutoff: float = 300.0

    # Segment / syllable detection (RMS-based)
    rms_frame_length: int = 2048
    rms_threshold: float = 0.10
    min_segment_duration: float = 0.05
    min_silence_duration: float = 0.05
    segment_directory: str = "experimental/segments"  # legacy placeholder

    # Soft thresholding & overlays
    sigmoid_k: float = 0.15
    overlay_segments: bool = False

    @classmethod
    def from_dict(cls, data: Dict) -> "SpectrogramConfig":
        base = PROJECT_ROOT

        def _resolve(path_value: str) -> Path:
            path_obj = Path(path_value)
            return path_obj if path_obj.is_absolute() else (base / path_obj)

        return cls(
            input_directory=_resolve(data["input_directory"]),
            output_directory=_resolve(data["output_directory"]),
            transform=str(data.get("transform", "stft")),
            sample_rate=int(data["sample_rate"]),
            n_fft=int(data["n_fft"]),
            hop_ratio=float(data.get("hop_ratio", 0.125)),
            hop_length=int(
                data.get("hop_length", int(int(data["n_fft"]) * float(data.get("hop_ratio", 0.125))))
            ),
            window=str(data["window"]),
            use_log_frequency=bool(data.get("use_log_frequency", True)),
            fmin=None if data.get("fmin") in (None, "") else float(data["fmin"]),
            fmax=None if data.get("fmax") in (None, "") else float(data["fmax"]),
            n_mels=int(data.get("n_mels", 512)),
            power=float(data.get("power", 2.0)),
            pcen_enabled=bool(data.get("pcen_enabled", False)),
            per_frequency_normalization=bool(data.get("per_frequency_normalization", False)),
            ref_power=float(data.get("ref_power", 1.0)),
            top_db=None if data.get("top_db") in (None, "") else float(data["top_db"]),
            dynamic_range=float(data.get("dynamic_range", 80)),
            contrast_percentile=None
            if data.get("contrast_percentile") in (None, "")
            else float(data["contrast_percentile"]),
            colormap=str(data.get("colormap", "gray_r")),
            fig_width=float(data.get("fig_width", 12.0)),
            fig_height=float(data.get("fig_height", 6.0)),
            dpi=int(data.get("dpi", 300)),
            max_duration_sec=None
            if data.get("max_duration_sec") in (None, "")
             else float(data["max_duration_sec"]),
             title=str(data.get("title", "Experimental Spectrogram")),
             pcen_bias=float(data.get("pcen_bias", 2.0)),
             pcen_gain=float(data.get("pcen_gain", 0.98)),
             noise_reduction=bool(data.get("noise_reduction", False)),
             high_pass_filter=bool(data.get("high_pass_filter", False)),
             high_pass_cutoff=float(data.get("high_pass_cutoff", 300.0)),
             rms_frame_length=int(data.get("rms_frame_length", 1024)),
             rms_threshold=float(data.get("rms_threshold", 0.2)),
             min_segment_duration=float(data.get("min_segment_duration", 0.05)),
             min_silence_duration=float(data.get("min_silence_duration", 0.05)),
             segment_directory=str(data.get("segment_directory", "experimental/segments")),
            sigmoid_k=float(data.get("sigmoid_k", 20.0)),
            overlay_segments=bool(data.get("overlay_segments", False)),
        )

    def to_dict(self) -> Dict:
        def _relativize(path: Path) -> str:
            try:
                return str(path.relative_to(PROJECT_ROOT))
            except ValueError:
                return str(path)

        return {
            "input_directory": _relativize(self.input_directory),
            "output_directory": _relativize(self.output_directory),
            "transform": self.transform,
            "sample_rate": self.sample_rate,
            "n_fft": self.n_fft,
            "hop_ratio": self.hop_ratio,
            "hop_length": self.hop_length,
            "window": self.window,
            "use_log_frequency": self.use_log_frequency,
            "fmin": self.fmin,
            "fmax": self.fmax,
            "n_mels": self.n_mels,
            "power": self.power,
            "pcen_enabled": self.pcen_enabled,
            "per_frequency_normalization": self.per_frequency_normalization,
            "ref_power": self.ref_power,
            "top_db": self.top_db,
            "dynamic_range": self.dynamic_range,
            "contrast_percentile": self.contrast_percentile,
            "colormap": self.colormap,
            "fig_width": self.fig_width,
            "fig_height": self.fig_height,
            "dpi": self.dpi,
            "max_duration_sec": self.max_duration_sec,
            "title": self.title,
            "pcen_bias": self.pcen_bias,
            "pcen_gain": self.pcen_gain,
            "noise_reduction": self.noise_reduction,
            "high_pass_filter": self.high_pass_filter,
            "high_pass_cutoff": self.high_pass_cutoff,
            "rms_frame_length": self.rms_frame_length,
            "rms_threshold": self.rms_threshold,
            "min_segment_duration": self.min_segment_duration,
            "min_silence_duration": self.min_silence_duration,
            "segment_directory": self.segment_directory,
            "sigmoid_k": self.sigmoid_k,
            "overlay_segments": self.overlay_segments,
        }


def load_config(config_path: Path = CONFIG_PATH) -> SpectrogramConfig:
    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    cfg = SpectrogramConfig.from_dict(raw)
    cfg.input_directory.mkdir(parents=True, exist_ok=True)
    cfg.output_directory.mkdir(parents=True, exist_ok=True)
    return cfg


def save_config(config: SpectrogramConfig, config_path: Path = CONFIG_PATH) -> None:
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)


def _trim_audio(y: np.ndarray, sr: int, max_duration_sec: Optional[float]) -> np.ndarray:
    """Trim audio to maximum duration in seconds."""
    if max_duration_sec is None:
        return y
    max_samples = int(max_duration_sec * sr)
    return y[:max_samples]


def _sigmoid(x: np.ndarray, k: float = 20.0) -> np.ndarray:
    """Sigmoid function for soft-thresholding (reduces vertical streak artifacts)."""
    return 1 / (1 + np.exp(-k * (x - 0.5)))  # assumes x normalized [0,1]


def _apply_high_pass_filter(y: np.ndarray, sr: int, cutoff_hz: float) -> np.ndarray:
    """Lightweight HPF using a 4th-order Butterworth filter."""
    if cutoff_hz <= 0.0 or cutoff_hz >= sr / 2:
        return y
    sos = signal.butter(4, cutoff_hz, btype="highpass", fs=sr, output="sos")
    return signal.sosfilt(sos, y)


def _apply_noise_reduction(y: np.ndarray, n_fft: int, hop_length: int) -> np.ndarray:
    """Simple spectral gating based on median noise profile."""
    if y.size == 0:
        return y
    D = librosa.stft(y, n_fft=n_fft, hop_length=hop_length)
    magnitude = np.abs(D)
    noise_profile = np.percentile(magnitude, NOISE_PROFILE_PERCENTILE, axis=1, keepdims=True)
    reduced_mag = np.maximum(magnitude - noise_profile, 0.0)
    phased = reduced_mag * np.exp(1j * np.angle(D))
    return librosa.istft(phased, hop_length=hop_length, length=len(y))


def detect_segments(y: np.ndarray, sr: int, cfg: SpectrogramConfig) -> List[Tuple[int, int]]:
    """
    Detect segments in audio based on RMS with sigmoid soft-thresholding.
    Returns list of (start_sample, end_sample) tuples.
    """

    # Compute RMS per frame
    hop_length = _calculate_hop_length(cfg.n_fft, cfg.hop_ratio, getattr(cfg, "hop_length", None))
    rms = librosa.feature.rms(y=y, frame_length=cfg.rms_frame_length, hop_length=hop_length)[0]

    # Normalize RMS to [0,1]
    rms_norm = rms / np.max(rms + 1e-6)

    # Apply sigmoid soft-thresholding
    rms_sigmoid = _sigmoid(rms_norm, k=cfg.sigmoid_k)

    # Threshold to boolean mask
    mask = rms_sigmoid > cfg.rms_threshold

    # Convert frame indices to sample indices
    frames = np.arange(len(mask)) * hop_length
    segments: List[Tuple[int, int]] = []
    in_segment = False
    seg_start = 0
    min_samples = int(cfg.min_segment_duration * sr)
    min_silence = int(cfg.min_silence_duration * sr)

    for i, m in enumerate(mask):
        sample_idx = i * hop_length
        if m and not in_segment:
            in_segment = True
            seg_start = sample_idx
        elif not m and in_segment:
            seg_end = sample_idx
            if seg_end - seg_start >= min_samples:
                if segments and seg_start - segments[-1][1] < min_silence:
                    # Merge close segments
                    segments[-1] = (segments[-1][0], seg_end)
                else:
                    segments.append((seg_start, seg_end))
            in_segment = False

    # Handle case where audio ends in a segment
    if in_segment:
        seg_end = len(y)
        if seg_end - seg_start >= min_samples:
            if segments and seg_start - segments[-1][1] < min_silence:
                segments[-1] = (segments[-1][0], seg_end)
            else:
                segments.append((seg_start, seg_end))

    return segments


def export_segments(y: np.ndarray, sr: int, segments: List[Tuple[int, int]], cfg: SpectrogramConfig, base_name: str) -> None:
    """Segment export intentionally disabled; kept for API compatibility."""
    return None


def generate_spectrogram(
    wav_path: Path,
    cfg: SpectrogramConfig,
    overlay_segments: bool = False,
    export_segments_flag: bool = False,
    output_dir: Optional[Path] = None,
) -> Path:
    """Generate a single spectrogram with optional segment overlay (no WAV export)."""
    output_dir = output_dir or cfg.output_directory
    output_dir.mkdir(parents=True, exist_ok=True)
    y, sr = librosa.load(wav_path, sr=cfg.sample_rate, mono=True)
    y = _trim_audio(y, sr, cfg.max_duration_sec)
    hop_length = _calculate_hop_length(cfg.n_fft, cfg.hop_ratio, getattr(cfg, "hop_length", None))

    if cfg.high_pass_filter:
        y = _apply_high_pass_filter(y, sr, cfg.high_pass_cutoff)
    if cfg.noise_reduction:
        y = _apply_noise_reduction(y, cfg.n_fft, hop_length)

    # Determine frequency bounds
    nyquist = sr / 2.0
    freq_cap = min(16000.0, nyquist - 1.0)
    effective_fmin = cfg.fmin or 0.0
    effective_fmax = min(cfg.fmax or freq_cap, freq_cap)
    if effective_fmax <= effective_fmin:
        effective_fmin = max(0.0, effective_fmax * 0.5)

    # Generate spectrogram
    pcen_kwargs = {
        "sr": sr,
        "hop_length": hop_length,
        "gain": cfg.pcen_gain,
        "bias": cfg.pcen_bias,
    }
    if cfg.transform.lower() == "mel":
        S_base = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_fft=cfg.n_fft,
            hop_length=hop_length,
            window=cfg.window,
            n_mels=cfg.n_mels,
            fmin=effective_fmin,
            fmax=effective_fmax,
            power=cfg.power,
        )
        if cfg.pcen_enabled:
            S_db = librosa.pcen(S_base + 1e-6, **pcen_kwargs)
        else:
            S_db = librosa.power_to_db(S_base, ref=cfg.ref_power, top_db=cfg.top_db)
        y_axis = "mel"
    elif cfg.transform.lower() == "cqt":
        bins_per_octave = 48
        n_bins = int(np.ceil(np.log2(effective_fmax / (effective_fmin or 200.0)) * bins_per_octave))
        C = np.abs(librosa.cqt(y, sr=sr, hop_length=hop_length, fmin=effective_fmin or 200.0, n_bins=n_bins, bins_per_octave=bins_per_octave, window=cfg.window))
        if cfg.pcen_enabled:
            S_db = librosa.pcen((C ** 2) + 1e-6, **pcen_kwargs)
        else:
            S_db = librosa.amplitude_to_db(C, ref=cfg.ref_power, top_db=cfg.top_db)
        y_axis = "cqt_hz"
    else:
        STFT = librosa.stft(y, n_fft=cfg.n_fft, hop_length=hop_length, window=cfg.window, center=True)
        if cfg.pcen_enabled:
            magnitude = np.abs(STFT) ** 2
            S_db = librosa.pcen(magnitude + 1e-6, **pcen_kwargs)
        else:
            S_db = librosa.amplitude_to_db(np.abs(STFT), ref=cfg.ref_power, top_db=cfg.top_db)
        y_axis = "log" if cfg.use_log_frequency else "linear"

    # Per-frequency normalization
    if cfg.per_frequency_normalization:
        mean = S_db.mean(axis=1, keepdims=True)
        std = S_db.std(axis=1, keepdims=True) + 1e-6
        S_db = (S_db - mean) / std

    # Contrast clipping
    if cfg.pcen_enabled:
        if cfg.contrast_percentile is not None:
            vmax = np.percentile(S_db, cfg.contrast_percentile)
        else:
            vmax = np.max(S_db)
        vmin = np.min(S_db)
    else:
        if cfg.contrast_percentile is not None:
            vmax = np.percentile(S_db, cfg.contrast_percentile)
            vmin = vmax - cfg.dynamic_range
        else:
            vmax = np.max(S_db)
            vmin = vmax - cfg.dynamic_range
    S_db = np.clip(S_db, vmin, None)

    # Detect segments
    segments = detect_segments(y, sr, cfg)

    # Segment export disabled; overlay remains available

    # Plot spectrogram with optional overlay
    fig, ax = plt.subplots(figsize=(cfg.fig_width, cfg.fig_height), dpi=cfg.dpi)
    cmap_obj = _resolve_colormap(cfg.colormap)
    img = librosa.display.specshow(S_db, sr=sr, hop_length=hop_length, x_axis="time", y_axis=y_axis, fmin=effective_fmin, fmax=effective_fmax, cmap=cmap_obj, vmin=vmin, vmax=vmax, ax=ax)
    if hasattr(img, "set_interpolation"):
        img.set_interpolation("nearest")
    ax.set_ylim(
        bottom=effective_fmin if effective_fmin > 0.0 else None,
        top=effective_fmax,
    )
    ax.set_aspect("auto")
    ax.set_title(cfg.title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    cbar = fig.colorbar(img, ax=ax, format="%+2.0f dB")
    cbar.set_label("Amplitude (dB)")

    if overlay_segments:
        for start, end in segments:
            ax.add_patch(Rectangle((start / sr, effective_fmin), (end - start) / sr, effective_fmax - effective_fmin, edgecolor="red", facecolor="none", linewidth=1.2))

    fig.tight_layout()
    output_path = output_dir / f"{wav_path.stem}_spectrogram.png"
    _save_png(fig, output_path, cfg.dpi)

    if not output_path.exists():
        raise RuntimeError(f"No PNG written to {output_path}")
    if output_path.stat().st_size == 0:
        raise RuntimeError(f"Empty PNG written to {output_path}")

    # Validate PNG to avoid truncated/corrupted files
    try:
        with Image.open(output_path) as png_check:
            png_check.verify()
    except Image.DecompressionBombError:
        _cleanup_paths(output_path)
        raise
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        tmp_path = output_path.with_suffix(".tmp.png")
        try:
            _save_png(fig, tmp_path, cfg.dpi)
            with Image.open(tmp_path) as png_check:
                png_check.verify()
        except Image.DecompressionBombError:
            _cleanup_paths(tmp_path, output_path)
            raise
        except (UnidentifiedImageError, OSError, SyntaxError) as retry_exc:
            raise RuntimeError(
                f"Failed to create valid PNG at {output_path}; initial error: {exc}; retry error: {retry_exc}"
            ) from retry_exc
        else:
            try:
                # Use replace to atomically swap the temporary file into place where supported;
                # any platform limitations surface as an OSError handled below.
                tmp_path.replace(output_path)
            except OSError as replace_exc:
                raise RuntimeError(f"Failed to move temporary PNG to {output_path}") from replace_exc
        finally:
            if tmp_path.exists():
                tmp_path.unlink()

    plt.close(fig)
    return output_path


def generate_for_directory(input_dir: Path, output_dir: Path, cfg: SpectrogramConfig) -> List[Path]:
    """Generate spectrograms for all WAVs in a directory."""
    wav_files = sorted(input_dir.glob("*.wav"))
    results = []
    for wav_path in wav_files:
        results.append(generate_spectrogram(wav_path, cfg, overlay_segments=cfg.overlay_segments, output_dir=output_dir))
    return results


def run_harness(config_path: Path = CONFIG_PATH) -> List[Path]:
    """Load JSON config and generate spectrograms for all test WAVs."""
    cfg = load_config(config_path)
    return generate_for_directory(cfg.input_directory, cfg.output_directory, cfg)


if __name__ == "__main__":
    results = run_harness()
    print(f"Generated {len(results)} spectrogram(s) into {CONFIG_PATH.parent / 'output'}")
