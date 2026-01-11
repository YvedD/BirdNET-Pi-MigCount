import io
import math
import tempfile
from pathlib import Path
from typing import Tuple, Union

import numpy as np
import soundfile as sf
from scipy import signal

SUPPORTED_EXTENSIONS = (".wav", ".mp3")


class AudioLoadingError(Exception):
    """Raised when an audio file cannot be loaded."""


def is_supported_file(path: Union[str, Path]) -> bool:
    return str(path).lower().endswith(SUPPORTED_EXTENSIONS)


def _resample(audio: np.ndarray, original_sr: int, target_sr: int) -> np.ndarray:
    if original_sr == target_sr:
        return audio
    gcd = math.gcd(int(original_sr), int(target_sr))
    up = target_sr // gcd
    down = original_sr // gcd
    return signal.resample_poly(audio, up, down)


def load_audio(
    source: Union[str, Path, io.BytesIO],
    target_sample_rate: int = None,
) -> Tuple[np.ndarray, int]:
    """
    Load an audio file using soundfile and optionally resample it.
    Returns mono audio as float32 and the effective sample rate.
    """
    try:
        data, sample_rate = sf.read(source, dtype="float32", always_2d=False)
    except Exception as exc:
        raise AudioLoadingError(str(exc)) from exc

    if data.ndim > 1:
        data = data.mean(axis=1)

    if target_sample_rate:
        data = _resample(data, sample_rate, target_sample_rate)
        sample_rate = target_sample_rate

    return data.astype(np.float32), int(sample_rate)


def load_uploaded_file(file_obj, target_sample_rate: int = None) -> Tuple[np.ndarray, int, Path]:
    """
    Persist an uploaded streamlit file to disk to enable caching and soundfile reading.
    Returns audio array, sample rate, and the temporary path used.
    """
    temp_path = persist_uploaded_file(file_obj)
    audio, sr = load_audio(temp_path, target_sample_rate=target_sample_rate)
    return audio, sr, temp_path


def persist_uploaded_file(file_obj) -> Path:
    suffix = Path(file_obj.name).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix="newlook_") as handle:
        handle.write(file_obj.getbuffer())
        return Path(handle.name)


def audio_info(path: Union[str, Path]) -> dict:
    meta = sf.info(path)
    duration = meta.frames / float(meta.samplerate) if meta.samplerate else 0.0
    return {
        "sample_rate": int(meta.samplerate),
        "frames": int(meta.frames),
        "channels": int(meta.channels),
        "duration": duration,
        "path": Path(path),
    }
