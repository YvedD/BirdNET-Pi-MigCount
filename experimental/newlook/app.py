import sys
import time
from dataclasses import replace
from pathlib import Path
from typing import Optional, Tuple

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import numpy as np
import streamlit as st

from experimental.newlook.audio_loader import (
    AudioLoadingError,
    SupportsUpload,
    audio_info,
    is_supported_file,
    load_audio,
    persist_uploaded_file,
)
from experimental.newlook.config import (
    DATASHADER_CMAPS,
    DATASHADER_SHADINGS,
    DEFAULT_CMAP,
    DEFAULT_DB_RANGE,
    DEFAULT_DPI,
    DEFAULT_FIGSIZE,
    DEFAULT_FMAX,
    DEFAULT_FMIN,
    DEFAULT_PER_FREQ_NORM,
    DEFAULT_RENDERER,
    MATPLOTLIB_CMAPS,
    NFFT_OPTIONS,
    PYQTGRAPH_CMAPS,
    RENDERER_CHOICES,
    SAMPLE_RATES,
    WINDOW_OPTIONS,
    DatashaderRenderParams,
    MatplotlibRenderParams,
    PyQtGraphRenderParams,
    SpectrogramDSP,
)
from experimental.newlook.renderer import (
    RendererBackend,
    render_datashader,
    render_matplotlib,
    render_pyqtgraph,
    save_png,
)
from experimental.newlook.spectrogram_engine import compute_spectrogram
from experimental.newlook.utils import clamp_frequency_range, format_seconds, hz_per_bin, ms_per_hop

st.set_page_config(page_title="Experimental Spectrogram Sandbox", layout="wide")


@st.cache_data(show_spinner=False)
def _cached_audio(path: str, target_sample_rate: Optional[int], resample: bool) -> Tuple[np.ndarray, int]:
    target = target_sample_rate if resample else None
    audio, sr = load_audio(path, target_sample_rate=target)
    return audio, sr


@st.cache_data(show_spinner=False)
def _cached_spectrogram(audio: np.ndarray, params: SpectrogramDSP) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    freqs, times, db = compute_spectrogram(
        audio,
        sample_rate=params.sample_rate,
        n_fft=params.n_fft,
        hop_length=params.hop_length,
        window=params.window,
        fmin=params.fmin,
        fmax=params.fmax,
        per_freq_norm=params.per_freq_norm,
        db_range=params.db_range,
    )
    return freqs, times, db


def _safe_index(options, value, default_index: int = 0) -> int:
    """Return index of value in options, or default_index if missing."""
    try:
        return options.index(value)
    except ValueError:
        return default_index


def _resolve_audio_source(uploaded_file: Optional[SupportsUpload], path_text: str) -> Optional[Path]:
    if uploaded_file:
        return persist_uploaded_file(uploaded_file)
    if path_text:
        candidate = Path(path_text).expanduser()
        if candidate.exists() and is_supported_file(candidate):
            return candidate
    return None


def main():
    st.title("Experimental Spectrogram Sandbox (new look)")
    st.caption(
        "Shared STFT DSP core with switchable renderers (Matplotlib, PyQtGraph, Datashader) for high-speed comparisons on Raspberry Pi 4B."
    )

    if "render_times" not in st.session_state:
        st.session_state["render_times"] = {}

    with st.sidebar:
        st.subheader("Audio")
        uploaded = st.file_uploader("Upload WAV/MP3", type=["wav", "mp3"])
        path_text = st.text_input("Or provide a local path", value="")
        target_sample_rate = st.selectbox("Target sample rate", SAMPLE_RATES, index=len(SAMPLE_RATES) - 1)
        resample = st.checkbox("Resample to target sample rate", value=True)

        st.subheader("Renderer")
        renderer_choice = st.radio("Backend", RENDERER_CHOICES, index=RENDERER_CHOICES.index(DEFAULT_RENDERER))

        st.subheader("Spectrogram DSP")
        n_fft = st.selectbox("FFT size", NFFT_OPTIONS, index=1)
        hop_length = st.slider("Hop length (samples)", min_value=128, max_value=n_fft, value=n_fft // 4, step=32)
        window = st.selectbox("Window function", WINDOW_OPTIONS, index=0)
        fmin = st.number_input("Min frequency (Hz)", min_value=0.0, value=DEFAULT_FMIN, step=10.0)
        fmax_default = min(DEFAULT_FMAX, target_sample_rate / 2)
        fmax = st.number_input(
            "Max frequency (Hz)", min_value=10.0, max_value=float(target_sample_rate / 2), value=fmax_default, step=10.0
        )
        per_freq_norm = st.checkbox("Per-frequency normalization", value=DEFAULT_PER_FREQ_NORM)
        db_range = st.slider("dB dynamic range", min_value=20, max_value=120, value=int(DEFAULT_DB_RANGE), step=5)

        st.subheader("Renderer controls")
        if renderer_choice == RENDERER_CHOICES[0]:
            cmap = st.selectbox("Colormap", MATPLOTLIB_CMAPS, index=_safe_index(MATPLOTLIB_CMAPS, DEFAULT_CMAP))
            dpi = st.slider("DPI", min_value=72, max_value=300, value=DEFAULT_DPI, step=4)
            width = st.slider("Figure width", min_value=4.0, max_value=14.0, value=DEFAULT_FIGSIZE[0], step=0.5)
            height = st.slider("Figure height", min_value=2.0, max_value=8.0, value=DEFAULT_FIGSIZE[1], step=0.5)
            render_params = MatplotlibRenderParams(cmap=cmap, dpi=dpi, figsize=(width, height))
            active_backend = RendererBackend.MATPLOTLIB
        elif renderer_choice == RENDERER_CHOICES[1]:
            cmap = st.selectbox("Colormap", PYQTGRAPH_CMAPS, index=_safe_index(PYQTGRAPH_CMAPS, DEFAULT_CMAP))
            gamma = st.slider("Contrast gamma", min_value=0.5, max_value=2.0, value=1.0, step=0.1)
            interpolate = st.checkbox("Interpolation", value=True)
            downsample = st.slider("Downsample (stride)", min_value=1, max_value=4, value=1, step=1)
            width_px = st.slider("Render width (px)", min_value=400, max_value=1600, value=900, step=50)
            height_px = st.slider("Render height (px)", min_value=200, max_value=900, value=420, step=20)
            render_params = PyQtGraphRenderParams(
                cmap=cmap, gamma=gamma, interpolate=interpolate, downsample=downsample, width=width_px, height=height_px
            )
            active_backend = RendererBackend.PYQTGRAPH
        else:
            cmap = st.selectbox("Colormap", DATASHADER_CMAPS, index=_safe_index(DATASHADER_CMAPS, DEFAULT_CMAP))
            shading = st.selectbox("Shading / aggregation", DATASHADER_SHADINGS, index=0)
            width_px = st.slider("Output width (px)", min_value=400, max_value=1600, value=900, step=50)
            height_px = st.slider("Output height (px)", min_value=200, max_value=900, value=420, step=20)
            render_params = DatashaderRenderParams(cmap=cmap, shading=shading, width=width_px, height=height_px)
            active_backend = RendererBackend.DATASHADER

    dsp_params = SpectrogramDSP(
        sample_rate=target_sample_rate,
        n_fft=n_fft,
        hop_length=hop_length,
        window=window,
        fmin=fmin,
        fmax=fmax,
        per_freq_norm=per_freq_norm,
        db_range=db_range,
    )

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
    except AudioLoadingError as exc:
        st.error(f"Failed to load audio: {exc}")
        return
    except OSError as exc:
        st.error(f"Filesystem error while loading audio: {exc}")
        return

    try:
        fmin_clamped, fmax_clamped = clamp_frequency_range(fmin, fmax, effective_sr)
    except ValueError as exc:
        st.error(str(exc))
        return

    runtime_params = replace(
        dsp_params,
        sample_rate=effective_sr,
        fmin=fmin_clamped,
        fmax=fmax_clamped,
    )

    duration = len(audio) / float(runtime_params.sample_rate)
    freq_res = hz_per_bin(runtime_params.sample_rate, runtime_params.n_fft)
    time_res = ms_per_hop(runtime_params.hop_length, runtime_params.sample_rate)

    vmin = -float(runtime_params.db_range)
    vmax = 0.0

    try:
        freqs, times, db_values = _cached_spectrogram(audio, runtime_params)
    except (ValueError, RuntimeError) as exc:
        st.error(f"Spectrogram failed: {exc}")
        return

    render_time_ms: Optional[float] = None

    if active_backend == RendererBackend.MATPLOTLIB:
        start = time.perf_counter()
        png_bytes = render_matplotlib(
            freqs,
            times,
            db_values,
            params=render_params,
            vmin=vmin,
            vmax=vmax,
            fmin=runtime_params.fmin,
            fmax=runtime_params.fmax,
        )
        render_time_ms = (time.perf_counter() - start) * 1000.0
    elif active_backend == RendererBackend.PYQTGRAPH:
        start = time.perf_counter()
        png_bytes = render_pyqtgraph(freqs, times, db_values, params=render_params, vmin=vmin, vmax=vmax)
        render_time_ms = (time.perf_counter() - start) * 1000.0
    else:
        start = time.perf_counter()
        png_bytes = render_datashader(
            freqs,
            times,
            db_values,
            params=render_params,
            vmin=vmin,
            vmax=vmax,
            fmin=runtime_params.fmin,
            fmax=runtime_params.fmax,
        )
        render_time_ms = (time.perf_counter() - start) * 1000.0

    st.session_state.render_times[active_backend] = render_time_ms

    status_cols = st.columns(4)
    status_cols[0].metric("Audio length", format_seconds(duration))
    status_cols[1].metric("FFT resolution", f"{freq_res:.2f} Hz/bin")
    status_cols[2].metric("Time resolution", f"{time_res:.2f} ms/frame")
    status_cols[3].metric(f"{renderer_choice} render", f"{render_time_ms:.1f} ms")
    st.write(
        f"Input sample rate: {info['sample_rate']} Hz  •  Effective sample rate: {effective_sr} Hz  •  Channels: {info['channels']}"
    )

    if st.session_state.render_times:
        times_text = "  |  ".join(f"{name}: {ms:.1f} ms" for name, ms in st.session_state.render_times.items())
        st.caption(f"Render times (last run): {times_text}")

    col_preview, col_actions = st.columns([3, 1])
    display_width: Optional[int]
    if isinstance(render_params, MatplotlibRenderParams):
        display_width = int(render_params.figsize[0] * render_params.dpi)
    elif isinstance(render_params, (PyQtGraphRenderParams, DatashaderRenderParams)):
        display_width = render_params.width
    else:
        display_width = None
    col_preview.image(
        png_bytes, caption=f"Live spectrogram preview — {renderer_choice}", width=display_width
    )

    suggested_name = audio_path.with_name(audio_path.stem + "_newlook.png").name
    col_actions.download_button("Download PNG", data=png_bytes, file_name=suggested_name, mime="image/png")

    if audio_path.exists():
        if col_actions.button("Save PNG next to audio"):
            output_path = audio_path.with_name(audio_path.stem + "_newlook.png")
            save_png(png_bytes, output_path)
            col_actions.success(f"Saved to {output_path}")


if __name__ == "__main__":  # pragma: no cover
    main()
