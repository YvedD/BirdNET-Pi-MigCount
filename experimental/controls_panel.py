"""
Experimental controls panel for spectrogram parameter tuning.

This Streamlit UI is sandboxed and only edits experimental/spectrogram_config.json.
It regenerates PNGs using tests/testdata WAV files and never touches BirdNET
inference or production spectrogram paths.
"""

from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experimental.spectrogram_generator import (  # type: ignore  # noqa: E402
    CONFIG_PATH,
    EXPERIMENT_ROOT,
    SpectrogramConfig,
    generate_for_directory,
    generate_spectrogram,
    load_config,
    save_config,
)


def render():
    st.title("Experimental Spectrogram Controls")
    st.caption(
        "Sandboxed renderer for Raven/Chirpity-style spectrograms. "
        "Does not affect BirdNET detection, models, or production outputs."
    )

    config = load_config(CONFIG_PATH)

    with st.form("spectrogram_params"):
        st.subheader("Signal & FFT")
        sample_rate = st.number_input(
            "Sample rate (Hz)", value=config.sample_rate, min_value=8000, max_value=192000
        )
        n_fft = st.number_input("FFT size", value=config.n_fft, min_value=256, step=256)
        hop_length = st.number_input(
            "Hop length", value=config.hop_length, min_value=64, step=64
        )
        window = st.text_input("Window", value=config.window)
        max_duration = st.number_input(
            "Max duration (seconds, blank for full file)",
            value=float(config.max_duration_sec) if config.max_duration_sec else 0.0,
            min_value=0.0,
        )

        st.subheader("Scale & Display")
        use_log_frequency = st.checkbox(
            "Logarithmic frequency axis", value=config.use_log_frequency
        )
        fmin = st.number_input(
            "Minimum frequency (Hz, 0 for auto)",
            value=float(config.fmin or 0.0),
            min_value=0.0,
            max_value=96000.0,
        )
        fmax = st.number_input(
            "Maximum frequency (Hz, 0 for auto)",
            value=float(config.fmax or 0.0),
            min_value=0.0,
            max_value=96000.0,
        )
        top_db = st.number_input("Top dB", value=float(config.top_db), min_value=10.0)
        dynamic_range = st.number_input(
            "Dynamic range (dB)", value=float(config.dynamic_range), min_value=10.0
        )
        contrast_percentile = st.number_input(
            "Contrast percentile (0-100, 0 disables percentile clipping)",
            value=float(config.contrast_percentile or 0.0),
            min_value=0.0,
            max_value=100.0,
        )
        colormap = st.text_input("Colormap", value=config.colormap)

        st.subheader("Output")
        fig_width = st.number_input("Figure width (inches)", value=float(config.fig_width))
        fig_height = st.number_input("Figure height (inches)", value=float(config.fig_height))
        dpi = st.number_input("DPI", value=int(config.dpi), min_value=72)
        title = st.text_input("Title", value=config.title)
        output_directory = st.text_input(
            "Output directory", value=str(config.output_directory)
        )

        submitted = st.form_submit_button("Save configuration")
        if submitted:
            updated = config.to_dict()
            updated.update(
                {
                    "sample_rate": int(sample_rate),
                    "n_fft": int(n_fft),
                    "hop_length": int(hop_length),
                    "window": window,
                    "max_duration_sec": None if max_duration <= 0 else float(max_duration),
                    "use_log_frequency": use_log_frequency,
                    "fmin": None if fmin <= 0 else float(fmin),
                    "fmax": None if fmax <= 0 else float(fmax),
                    "top_db": float(top_db),
                    "dynamic_range": float(dynamic_range),
                    "contrast_percentile": None if contrast_percentile <= 0 else float(contrast_percentile),
                    "colormap": colormap,
                    "fig_width": float(fig_width),
                    "fig_height": float(fig_height),
                    "dpi": int(dpi),
                    "title": title,
                    "output_directory": output_directory,
                }
            )
            save_config(SpectrogramConfig.from_dict(updated))
            st.success("Configuration saved to spectrogram_config.json")

    if st.button("Generate spectrogram PNGs", type="primary"):
        cfg = load_config(CONFIG_PATH)
        outputs = generate_for_directory(cfg.input_directory, cfg.output_directory, cfg)
        if outputs:
            st.success(f"Generated {len(outputs)} spectrogram file(s).")
            st.write("Latest file:")
            st.image(str(outputs[-1]))
        else:
            st.warning("No .wav files found to process.")

    st.subheader("Upload a WAV to generate a PNG")
    uploaded = st.file_uploader("Select a .wav file", type=["wav"])
    if uploaded is not None:
        cfg = load_config(CONFIG_PATH)
        output_dir = cfg.output_directory
        output_dir.mkdir(parents=True, exist_ok=True)
        wav_path = output_dir / f"user_{uploaded.name}"
        wav_path.write_bytes(uploaded.read())
        png_path = generate_spectrogram(wav_path, cfg, output_dir)
        st.success(f"Generated {png_path.name}")
        st.image(str(png_path))

    st.markdown(
        "This page is for visual experimentation only. "
        "Production BirdNET audio workflows remain unchanged."
    )


if __name__ == "__main__":
    render()
