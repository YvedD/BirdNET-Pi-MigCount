from __future__ import annotations

"""
Streamlit UI for experimenting with spectrogram parameters and syllable segmentation.

Features:
- Adjust spectrogram transforms (mel, STFT, CQT)
- Tune windowing, FFT size, hop ratio
- Control frequency bounds and scaling
- Enable PCEN and per-frequency normalization
- Generate segmented WAVs for syllables
- Visualize results directly in the UI

All changes are saved to experimental/spectrogram_config.json
and isolated from BirdNET production pipeline.
"""

import sys
from pathlib import Path
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experimental.spectrogram_generator import (
    CONFIG_PATH,
    SpectrogramConfig,
    generate_spectrogram,
    detect_segments,
    export_segments,
    load_config,
    save_config,
)

def render():
    st.title("Experimental Spectrogram Controls")
    st.caption(
        "This UI allows you to tweak every parameter and see its effect immediately.\n"
        "You can also generate WAV segments for each detected syllable."
    )

    # Load current config
    cfg = load_config(CONFIG_PATH)

    with st.form("params_form"):
        st.subheader("Audio & Transform")
        transform = st.selectbox("Transform type", ["mel", "stft", "cqt"], index=["mel", "stft", "cqt"].index(cfg.transform))
        sample_rate = st.selectbox("Sample rate (Hz)", [24000, 48000], index=[24000, 48000].index(cfg.sample_rate))
        n_fft_options = [2048, 4096, 8192] if sample_rate == 48000 else [2048, 4096]
        n_fft = st.selectbox("FFT size", n_fft_options, index=n_fft_options.index(cfg.n_fft if cfg.n_fft in n_fft_options else n_fft_options[0]))
        hop_ratio = st.slider("Hop ratio (fraction of FFT size)", 0.05, 0.25, float(cfg.hop_ratio), step=0.01)
        window = st.selectbox("Window function", ["hann", "hamming", "blackman", "bartlett"], index=["hann", "hamming", "blackman", "bartlett"].index(cfg.window))

        st.subheader("Frequency & Scaling")
        use_log_frequency = st.checkbox("Logarithmic frequency axis", value=cfg.use_log_frequency)
        fmin = st.number_input("Min frequency (Hz)", min_value=0.0, max_value=96000.0, value=float(cfg.fmin or 200.0))
        fmax = st.number_input("Max frequency (Hz)", min_value=0.0, max_value=96000.0, value=float(cfg.fmax or 12000.0))
        n_mels = st.number_input("Number of Mel bins", value=int(cfg.n_mels), min_value=16, max_value=2048)
        power = st.number_input("Power (spectrogram)", value=float(cfg.power), min_value=1.0, max_value=4.0)
        pcen_enabled = st.checkbox("Enable PCEN", value=cfg.pcen_enabled)
        per_freq_norm = st.checkbox("Per-frequency normalization", value=cfg.per_frequency_normalization)
        ref_power = st.number_input("Reference power (dB)", value=float(cfg.ref_power), min_value=0.0001)
        top_db = st.number_input("Top dB (clipping)", value=float(cfg.top_db or 45.0), min_value=1.0, max_value=120.0)
        dynamic_range = st.number_input("Dynamic range (dB)", value=float(cfg.dynamic_range), min_value=10.0)

        st.subheader("Segmentation (syllables)")
        rms_frame_length = st.number_input("RMS frame length (samples)", value=int(cfg.rms_frame_length))
        rms_threshold = st.slider("RMS threshold (0-1)", 0.0, 1.0, float(cfg.rms_threshold), step=0.01)
        min_segment_duration = st.number_input("Min segment duration (s)", value=float(cfg.min_segment_duration), min_value=0.01, max_value=10.0)
        min_silence_duration = st.number_input("Min silence to separate (s)", value=float(cfg.min_silence_duration), min_value=0.01, max_value=10.0)

        st.subheader("Visualization & Output")
        colormap = st.selectbox("Colormap", ["gray_r", "magma", "inferno", "plasma"], index=["gray_r", "magma", "inferno", "plasma"].index(cfg.colormap))
        fig_width = st.number_input("Figure width (inches)", value=float(cfg.fig_width))
        fig_height = st.number_input("Figure height (inches)", value=float(cfg.fig_height))
        dpi = st.number_input("DPI", value=int(cfg.dpi), min_value=72)
        title = st.text_input("Title", value=cfg.title)
        output_dir = st.text_input("Output directory", value=str(cfg.output_directory))
        segment_dir = st.text_input("Segment directory (WAVs)", value=str(cfg.segment_directory))

        submitted = st.form_submit_button("Save config")
        if submitted:
            updated = cfg.to_dict()
            updated.update({
                "transform": transform,
                "sample_rate": sample_rate,
                "n_fft": n_fft,
                "hop_ratio": hop_ratio,
                "window": window,
                "use_log_frequency": use_log_frequency,
                "fmin": fmin,
                "fmax": fmax,
                "n_mels": n_mels,
                "power": power,
                "pcen_enabled": pcen_enabled,
                "per_frequency_normalization": per_freq_norm,
                "ref_power": ref_power,
                "top_db": top_db,
                "dynamic_range": dynamic_range,
                "rms_frame_length": rms_frame_length,
                "rms_threshold": rms_threshold,
                "min_segment_duration": min_segment_duration,
                "min_silence_duration": min_silence_duration,
                "colormap": colormap,
                "fig_width": fig_width,
                "fig_height": fig_height,
                "dpi": dpi,
                "title": title,
                "output_directory": output_dir,
                "segment_directory": segment_dir
            })
            save_config(SpectrogramConfig.from_dict(updated))
            st.success("Configuration saved!")

    st.subheader("Generate PNG / Segments")
    if st.button("Process all WAVs in input directory"):
        cfg = load_config(CONFIG_PATH)
        for wav in cfg.input_directory.glob("*.wav"):
            generate_spectrogram(wav, cfg)
        st.success("Processing complete! Segments exported to WAVs in segment directory.")

if __name__ == "__main__":
    render()
