from pathlib import Path
from typing import Optional

import numpy as np
import streamlit as st

from .audio_loader import audio_info, is_supported_file, load_audio, persist_uploaded_file
from .config import (
    COLOR_MAPS,
    DEFAULT_CMAP,
    DEFAULT_DB_RANGE,
    DEFAULT_FIGSIZE,
    DEFAULT_FMAX,
    DEFAULT_FMIN,
    DEFAULT_PER_FREQ_NORM,
    DEFAULT_DPI,
    NFFT_OPTIONS,
    SAMPLE_RATES,
    WINDOW_OPTIONS,
)
from .renderer import render_spectrogram, save_png
from .spectrogram_engine import compute_spectrogram
from .utils import clamp_frequency_range, format_seconds, hz_per_bin, ms_per_hop

st.set_page_config(page_title="Experimental Spectrogram Sandbox", layout="wide")


@st.cache_data(show_spinner=False)
def _cached_audio(path: str, target_sample_rate: Optional[int], resample: bool):
    target = target_sample_rate if resample else None
    audio, sr = load_audio(path, target_sample_rate=target)
    return audio, sr


@st.cache_data(show_spinner=False)
def _cached_spectrogram(audio: np.ndarray, sr: int, n_fft: int, hop_length: int, window: str, fmin: float, fmax: float, per_freq_norm: bool, db_range: float):
    freqs, times, db = compute_spectrogram(
        audio,
        sample_rate=sr,
        n_fft=n_fft,
        hop_length=hop_length,
        window=window,
        fmin=fmin,
        fmax=fmax,
        per_freq_norm=per_freq_norm,
        db_range=db_range,
    )
    return freqs, times, db


def _resolve_audio_source(uploaded_file, path_text: str) -> Optional[Path]:
    if uploaded_file:
        return persist_uploaded_file(uploaded_file)
    if path_text:
        candidate = Path(path_text).expanduser()
        if candidate.exists() and is_supported_file(candidate):
            return candidate
    return None


def main():
    st.title("Experimental Spectrogram Sandbox (new look)")
    st.caption("Offline, high-resolution STFT spectrograms for BirdNET-Pi recordings. Uses numpy + scipy.signal + soundfile + matplotlib.")

    with st.sidebar:
        st.subheader("Audio")
        uploaded = st.file_uploader("Upload WAV/MP3", type=["wav", "mp3"])
        path_text = st.text_input("Or provide a local path", value="")
        target_sample_rate = st.selectbox("Target sample rate", SAMPLE_RATES, index=len(SAMPLE_RATES) - 1)
        resample = st.checkbox("Resample to target sample rate", value=True)

        st.subheader("Spectrogram parameters")
        n_fft = st.selectbox("FFT size", NFFT_OPTIONS, index=1)
        hop_length = st.slider("Hop length (samples)", min_value=128, max_value=n_fft, value=n_fft // 4, step=32)
        window = st.selectbox("Window function", WINDOW_OPTIONS, index=0)
        fmin = st.number_input("Min frequency (Hz)", min_value=0.0, value=DEFAULT_FMIN, step=10.0)
        fmax_default = min(DEFAULT_FMAX, target_sample_rate / 2)
        fmax = st.number_input("Max frequency (Hz)", min_value=10.0, max_value=float(target_sample_rate / 2), value=fmax_default, step=10.0)
        per_freq_norm = st.checkbox("Per-frequency normalization", value=DEFAULT_PER_FREQ_NORM)
        db_range = st.slider("dB dynamic range", min_value=20, max_value=120, value=int(DEFAULT_DB_RANGE), step=5)

        st.subheader("Rendering")
        cmap = st.selectbox("Colormap", COLOR_MAPS, index=COLOR_MAPS.index(DEFAULT_CMAP))
        dpi = st.slider("DPI", min_value=72, max_value=300, value=DEFAULT_DPI, step=4)
        width = st.slider("Figure width", min_value=4.0, max_value=14.0, value=DEFAULT_FIGSIZE[0], step=0.5)
        height = st.slider("Figure height", min_value=2.0, max_value=8.0, value=DEFAULT_FIGSIZE[1], step=0.5)

    audio_path = _resolve_audio_source(uploaded, path_text)

    if not audio_path:
        st.info("Select or provide a local WAV/MP3 file to begin.")
        return

    try:
        info = audio_info(audio_path)
    except Exception as exc:  # pragma: no cover - defensive
        st.error(f"Unable to inspect audio: {exc}")
        return

    try:
        audio, effective_sr = _cached_audio(str(audio_path), target_sample_rate, resample=resample)
    except Exception as exc:
        st.error(f"Failed to load audio: {exc}")
        return

    try:
        fmin_clamped, fmax_clamped = clamp_frequency_range(fmin, fmax, effective_sr)
    except ValueError as exc:
        st.error(str(exc))
        return

    duration = len(audio) / float(effective_sr)
    freq_res = hz_per_bin(effective_sr, n_fft)
    time_res = ms_per_hop(hop_length, effective_sr)

    status_cols = st.columns(3)
    status_cols[0].metric("Audio length", format_seconds(duration))
    status_cols[1].metric("FFT resolution", f"{freq_res:.2f} Hz/bin")
    status_cols[2].metric("Time resolution", f"{time_res:.2f} ms/frame")
    st.write(f"Input sample rate: {info['sample_rate']} Hz  •  Effective sample rate: {effective_sr} Hz  •  Channels: {info['channels']}")

    vmin = -float(db_range)
    vmax = 0.0

    try:
        freqs, times, db_values = _cached_spectrogram(
            audio,
            effective_sr,
            n_fft=n_fft,
            hop_length=hop_length,
            window=window,
            fmin=fmin_clamped,
            fmax=fmax_clamped,
            per_freq_norm=per_freq_norm,
            db_range=db_range,
        )
    except Exception as exc:
        st.error(f"Spectrogram failed: {exc}")
        return

    png_bytes = render_spectrogram(
        freqs,
        times,
        db_values,
        cmap=cmap,
        figsize=(width, height),
        dpi=dpi,
        vmin=vmin,
        vmax=vmax,
        fmin=fmin_clamped,
        fmax=fmax_clamped,
    )

    col_preview, col_actions = st.columns([3, 1])
    col_preview.image(png_bytes, caption="Live spectrogram preview", use_column_width=True)

    suggested_name = audio_path.with_name(audio_path.stem + "_newlook.png").name
    col_actions.download_button("Download PNG", data=png_bytes, file_name=suggested_name, mime="image/png")

    if audio_path.exists():
        if col_actions.button("Save PNG next to audio"):
            output_path = audio_path.with_name(audio_path.stem + "_newlook.png")
            save_png(png_bytes, output_path)
            col_actions.success(f"Saved to {output_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
