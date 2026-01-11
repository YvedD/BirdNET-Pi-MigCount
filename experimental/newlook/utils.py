from typing import Iterable, Tuple


def hz_per_bin(sample_rate: int, n_fft: int) -> float:
    return float(sample_rate) / float(n_fft)


def ms_per_hop(hop_length: int, sample_rate: int) -> float:
    return 1000.0 * float(hop_length) / float(sample_rate)


def clamp_frequency_range(fmin: float, fmax: float, sample_rate: int) -> Tuple[float, float]:
    nyquist = float(sample_rate) / 2.0
    low = max(0.0, float(fmin))
    high = nyquist if fmax is None else min(float(fmax), nyquist)
    if low >= high:
        raise ValueError("fmin must be lower than fmax and Nyquist")
    return low, high


def format_seconds(seconds: float) -> str:
    if seconds >= 60:
        minutes = int(seconds // 60)
        remainder = seconds % 60
        return f"{minutes:d}m {remainder:.1f}s"
    return f"{seconds:.2f}s"


def validate_window_name(name: str, allowed: Iterable[str]) -> str:
    lower = name.lower()
    if lower not in {w.lower() for w in allowed}:
        raise ValueError(f"Unsupported window '{name}'")
    return lower
