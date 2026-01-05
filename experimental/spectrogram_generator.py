"""
Experimental spectrogram generator using librosa + matplotlib.

This module is a sandbox for rendering Raven/Chirpity-style spectrograms.
It is deliberately isolated: it only consumes .wav files from the tests/
folder and writes PNGs into experimental/output. No BirdNET inference,
models, or scoring code are imported or modified.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Union

import librosa
import librosa.display  # type: ignore
import matplotlib.pyplot as plt
import numpy as np

EXPERIMENT_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = EXPERIMENT_ROOT.parent
CONFIG_PATH = EXPERIMENT_ROOT / "spectrogram_config.json"


@dataclass
class SpectrogramConfig:
    """Container for JSON-driven spectrogram parameters."""

    input_directory: Path
    output_directory: Path
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
            use_log_frequency=bool(data["use_log_frequency"]),
            fmin=None if data.get("fmin") in (None, "") else float(data["fmin"]),
            fmax=None if data.get("fmax") in (None, "") else float(data["fmax"]),
            n_mels=int(data.get("n_mels", 256)),
            power=float(data.get("power", 2.0)),
            pcen_enabled=bool(data.get("pcen_enabled", False)),
            per_frequency_normalization=bool(data.get("per_frequency_normalization", False)),
            ref_power=float(data.get("ref_power", 1.0)),
            top_db=None if data.get("top_db") in (None, "") else float(data["top_db"]),
            dynamic_range=float(data["dynamic_range"]),
            contrast_percentile=None
            if data.get("contrast_percentile") in (None, "")
            else float(data["contrast_percentile"]),
            colormap=str(data["colormap"]),
            fig_width=float(data["fig_width"]),
            fig_height=float(data["fig_height"]),
            dpi=int(data["dpi"]),
            max_duration_sec=None
            if data.get("max_duration_sec") in (None, "")
            else float(data["max_duration_sec"]),
            title=str(data.get("title", "Experimental Spectrogram")),
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
        }


def load_config(config_path: Path = CONFIG_PATH) -> SpectrogramConfig:
    with config_path.open("r", encoding="utf-8") as f:
        raw = json.load(f)
    return SpectrogramConfig.from_dict(raw)


def save_config(config: SpectrogramConfig, config_path: Path = CONFIG_PATH) -> None:
    with config_path.open("w", encoding="utf-8") as f:
        json.dump(config.to_dict(), f, indent=2)


def _trim_audio(y: np.ndarray, sr: int, max_duration_sec: Optional[float]) -> np.ndarray:
    if max_duration_sec is None:
        return y
    max_samples = int(max_duration_sec * sr)
    if max_samples <= 0:
        return y[:0]
    return y[:max_samples]


def generate_spectrogram(wav_path: Path, config: SpectrogramConfig, output_dir: Path) -> Path:
    """Render a single spectrogram PNG for wav_path into output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    y, sr = librosa.load(wav_path, sr=config.sample_rate, mono=True)
    y = _trim_audio(y, sr, config.max_duration_sec)

    if config.use_log_frequency and (config.fmin is None or config.fmin <= 0):
        config.fmin = 200.0

    nyquist = sr / 2.0
    effective_fmax = min(config.fmax or nyquist, nyquist - 1.0)
    effective_fmin = config.fmin or 0.0
    if effective_fmax <= effective_fmin:
        effective_fmin = max(0.0, effective_fmax * 0.5)

    hop_length = int(config.n_fft * config.hop_ratio)
    config.hop_length = hop_length

    transform = config.transform.lower()
    if transform == "mel":
        mel_spec = librosa.feature.melspectrogram(
            y=y,
            sr=sr,
            n_fft=config.n_fft,
            hop_length=hop_length,
            window=config.window,
            n_mels=config.n_mels,
            fmin=effective_fmin,
            fmax=effective_fmax,
            power=config.power,
            center=True,
        )
        if config.pcen_enabled:
            mel_spec = librosa.pcen(mel_spec + 1e-6, sr=sr, hop_length=hop_length)
        spectrogram_db = librosa.power_to_db(
            mel_spec, ref=config.ref_power, top_db=config.top_db
        )
        y_axis = "mel"
    elif transform == "cqt":
        fmin = effective_fmin or 200.0
        fmax = effective_fmax
        bins_per_octave = 48
        n_bins = int(np.ceil(np.log2(fmax / fmin) * bins_per_octave))
        cqt = np.abs(
            librosa.cqt(
                y=y,
                sr=sr,
                hop_length=hop_length,
                fmin=fmin,
                n_bins=n_bins,
                bins_per_octave=bins_per_octave,
                window=config.window,
            )
        )
        if config.pcen_enabled:
            cqt = librosa.pcen(cqt + 1e-6, sr=sr, hop_length=hop_length)
        spectrogram_db = librosa.amplitude_to_db(
            cqt, ref=config.ref_power, top_db=config.top_db
        )
        y_axis = "cqt_hz"
    else:
        stft = librosa.stft(
            y,
            n_fft=config.n_fft,
            hop_length=hop_length,
            window=config.window,
            center=True,
        )
        magnitude = np.abs(stft)
        spectrogram_db = librosa.amplitude_to_db(
            magnitude, ref=config.ref_power, top_db=config.top_db
        )
        y_axis = "log" if config.use_log_frequency else "linear"

    if config.per_frequency_normalization:
        mean = spectrogram_db.mean(axis=1, keepdims=True)
        std = spectrogram_db.std(axis=1, keepdims=True) + 1e-6
        spectrogram_db = (spectrogram_db - mean) / std

    if config.contrast_percentile is not None:
        vmax = np.percentile(spectrogram_db, config.contrast_percentile)
        vmin = vmax - config.dynamic_range
    else:
        vmax = np.max(spectrogram_db)
        vmin = vmax - config.dynamic_range

    spectrogram_db = np.clip(spectrogram_db, vmin, None)

    fig, ax = plt.subplots(
        figsize=(config.fig_width, config.fig_height), dpi=config.dpi
    )
    img = librosa.display.specshow(
        spectrogram_db,
        sr=sr,
        hop_length=hop_length,
        x_axis="time",
        y_axis=y_axis,
        fmin=effective_fmin,
        fmax=effective_fmax,
        cmap=config.colormap,
        vmin=vmin,
        vmax=vmax,
        ax=ax,
    )
    if hasattr(img, "set_interpolation"):
        img.set_interpolation("nearest")
    ax.set_aspect("auto")
    ax.set_ylim(bottom=config.fmin or 0, top=config.fmax or None)
    ax.set_xlim(left=0)
    ax.set_ylim(ax.get_ylim()[0], ax.get_ylim()[1])
    ax.set_ylim(ax.get_ylim())  # ensure origin lower default
    ax.set_title(config.title)
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Frequency (Hz)")
    cbar = fig.colorbar(img, ax=ax, format="%+2.0f dB")
    cbar.set_label("Amplitude (dB)")
    fig.tight_layout()

    output_path = output_dir / f"{wav_path.stem}_spectrogram.png"
    fig.savefig(output_path, dpi=config.dpi, bbox_inches="tight")
    plt.close(fig)
    return output_path


def generate_for_directory(
    input_dir: Path, output_dir: Path, config: SpectrogramConfig
) -> List[Path]:
    wav_files: Iterable[Path] = sorted(input_dir.glob("*.wav"))
    generated: List[Path] = []
    for wav_path in wav_files:
        generated.append(generate_spectrogram(wav_path, config, output_dir))
    return generated


def run_harness(config_path: Path = CONFIG_PATH) -> List[Path]:
    """Load JSON config and generate spectrograms for tests/testdata wavs."""
    config = load_config(config_path)
    return generate_for_directory(config.input_directory, config.output_directory, config)


if __name__ == "__main__":
    results = run_harness()
    print(f"Generated {len(results)} spectrogram(s) into {CONFIG_PATH.parent/'output'}")
