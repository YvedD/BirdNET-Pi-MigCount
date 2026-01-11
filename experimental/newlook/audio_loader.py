import atexit
import io
import math
import tempfile
from pathlib import Path
from threading import Lock
from typing import Any, Optional, Protocol, Tuple, Union

import numpy as np
import soundfile as sf
from scipy import signal

SUPPORTED_EXTENSIONS = (".wav", ".mp3")
_TEMP_FILES = []
_TEMP_LOCK = Lock()


class SupportsUpload(Protocol):
    name: str

    def getbuffer(self) -> Any:
        ...


def _cleanup_temp_files():
    with _TEMP_LOCK:
        paths = list(_TEMP_FILES)
        _TEMP_FILES.clear()

    for path in paths:
        try:
            Path(path).unlink(missing_ok=True)
        except OSError:
            continue


atexit.register(_cleanup_temp_files)


class AudioLoadingError(Exception):
    """Raised when an audio file cannot be loaded."""


def is_supported_file(path: Union[str, Path]) -> bool:
    return str(path).lower().endswith(SUPPORTED_EXTENSIONS)


def _resample(audio: np.ndarray, original_sr: int, target_sr: int) -> np.ndarray:
    if original_sr == target_sr:
        return audio
    gcd = math.gcd(int(original_sr), int(target_sr))
    upsample_factor = target_sr // gcd
    downsample_factor = original_sr // gcd
    return signal.resample_poly(audio, upsample_factor, downsample_factor)


def load_audio(
    source: Union[str, Path, io.BytesIO],
    target_sample_rate: Optional[int] = None,
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


def load_uploaded_file(file_obj: SupportsUpload, target_sample_rate: Optional[int] = None) -> Tuple[np.ndarray, int, Path]:
    """
    Persist an uploaded streamlit file to disk to enable caching and soundfile reading.
    Returns audio array, sample rate, and the temporary path used.
    """
    temp_path = persist_uploaded_file(file_obj)
    audio, sr = load_audio(temp_path, target_sample_rate=target_sample_rate)
    return audio, sr, temp_path


def persist_uploaded_file(file_obj: SupportsUpload) -> Path:
    suffix = Path(file_obj.name).suffix or ".wav"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix="newlook_") as handle:
        handle.write(file_obj.getbuffer())
        path = Path(handle.name)
    with _TEMP_LOCK:
        _TEMP_FILES.append(path)
    return path


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
