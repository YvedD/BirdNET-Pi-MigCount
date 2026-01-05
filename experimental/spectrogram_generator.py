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
from typing import Dict, Iterable, List, Optional

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
    sample_rate: int
    n_fft: int
    hop_length: int
    window: str
    use_log_frequency: bool
    fmin: Optional[float]
    fmax: Optional[float]
    ref_power: str | float
    top_db: float
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
            sample_rate=int(data["sample_rate"]),
            n_fft=int(data["n_fft"]),
            hop_length=int(data["hop_length"]),
            window=str(data["window"]),
            use_log_frequency=bool(data["use_log_frequency"]),
            fmin=None if data.get("fmin") in (None, "") else float(data["fmin"]),
            fmax=None if data.get("fmax") in (None, "") else float(data["fmax"]),
            ref_power=data.get("ref_power", "max"),
            top_db=float(data["top_db"]),
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
            "sample_rate": self.sample_rate,
            "n_fft": self.n_fft,
            "hop_length": self.hop_length,
            "window": self.window,
            "use_log_frequency": self.use_log_frequency,
            "fmin": self.fmin,
            "fmax": self.fmax,
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


def _get_ref_power(ref_power: str | float, magnitude: np.ndarray):
    if isinstance(ref_power, (int, float)):
        return float(ref_power)
    return np.max(magnitude)


def _trim_audio(y: np.ndarray, sr: int, max_duration_sec: Optional[float]) -> np.ndarray:
    if max_duration_sec is None:
        return y
    max_samples = int(max_duration_sec * sr)
    if max_samples <= 0:
        return y
    return y[:max_samples]


def generate_spectrogram(wav_path: Path, config: SpectrogramConfig, output_dir: Path) -> Path:
    """Render a single spectrogram PNG for wav_path into output_dir."""
    output_dir.mkdir(parents=True, exist_ok=True)
    y, sr = librosa.load(wav_path, sr=config.sample_rate, mono=True)
    y = _trim_audio(y, sr, config.max_duration_sec)

    stft = librosa.stft(
        y,
        n_fft=config.n_fft,
        hop_length=config.hop_length,
        window=config.window,
        center=True,
    )
    magnitude = np.abs(stft)
    ref = _get_ref_power(config.ref_power, magnitude)
    spectrogram_db = librosa.amplitude_to_db(magnitude, ref=ref, top_db=config.top_db)

    if config.contrast_percentile is not None:
        vmax = np.percentile(spectrogram_db, config.contrast_percentile)
        vmin = vmax - config.dynamic_range
    else:
        vmax = None
        vmin = spectrogram_db.max() - config.dynamic_range

    fig, ax = plt.subplots(
        figsize=(config.fig_width, config.fig_height), dpi=config.dpi
    )
    img = librosa.display.specshow(
        spectrogram_db,
        sr=sr,
        hop_length=config.hop_length,
        x_axis="time",
        y_axis="log" if config.use_log_frequency else "linear",
        fmin=config.fmin,
        fmax=config.fmax,
        cmap=config.colormap,
        vmin=vmin,
        vmax=vmax,
        ax=ax,
    )
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
