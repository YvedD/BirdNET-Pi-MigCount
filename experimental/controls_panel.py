from __future__ import annotations
"""
Streamlit UI for experimenting with spectrogram parameters and syllable segmentation.

Features:
- Adjust spectrogram transforms (mel, STFT, CQT)
- Tune windowing, FFT size, hop ratio (overlap)
- Control frequency bounds, scaling, and power
- Enable PCEN and per-frequency normalization
- Detect and export segments as separate WAVs (syllables/notes)
- Sigmoid soft-threshold for smoothing segment edges
- Optional overlay of segments on the spectrogram image
- Visualize results directly in the UI
- Upload single WAVs for testing
- Save configuration for reproducible experiments

All changes are saved to experimental/spectrogram_config.json
and isolated from BirdNET production pipeline.
"""

import sys
from pathlib import Path
from typing import Dict, List
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experimental.spectrogram_generator import (
    CONFIG_PATH,
    SpectrogramConfig,
    detect_segments,
    export_segments,
    generate_spectrogram,
    load_config,
    save_config,
)

MEL_OPTIONS = [512, 1024, 2048, 4096, 8192]
COLORMAP_OPTIONS = ["soft_gray", "viridis", "plasma", "magma", "inferno", "cividis", "gray_r"]
COMPACT_STYLE = """
<style>
    div.block-container{padding-top:0.6rem;padding-bottom:1rem;}
    section[data-testid="stSidebar"]{font-size:0.9rem;}
    div[data-testid="stMarkdown"] p, label, .stSelectbox label, .stSlider label,
    .stNumberInput label, .stTextInput label, .stCheckbox label{font-size:0.9rem;}
    h1, h2, h3, h4{font-size:1.2rem;}
</style>
"""


def _prefer_light_colormap(name: str) -> str:
    return "soft_gray" if name == "gray_r" else name


def _init_state(cfg: SpectrogramConfig) -> None:
    base_config = cfg.to_dict()
    base_config["colormap"] = _prefer_light_colormap(base_config.get("colormap", "soft_gray"))
    if "base_config" not in st.session_state:
        st.session_state.base_config = base_config
    st.session_state.setdefault("working_config", st.session_state.base_config.copy())
    st.session_state["working_config"].setdefault("colormap", base_config["colormap"])
    for key, value in st.session_state["working_config"].items():
        st.session_state.setdefault(key, value)
    st.session_state.setdefault("last_preview_config", {})
    st.session_state.setdefault("force_refresh", True)


def render():
    st.set_page_config(layout="wide")
    st.markdown(COMPACT_STYLE, unsafe_allow_html=True)
    st.title("Experimental Spectrogram Controls")
    st.caption(
        "Tweak parameters and visualize effect immediately. "
        "Segmented WAVs for detected syllables can be exported."
    )

    cfg = load_config(CONFIG_PATH)
    _init_state(cfg)

    def reset_defaults() -> None:
        base = st.session_state.base_config
        st.session_state.working_config = base.copy()
        for key, value in base.items():
            st.session_state[key] = value
        st.session_state.force_refresh = True
        st.session_state.last_preview_config = {}

    working_cfg = st.session_state["working_config"]

    controls_col, preview_col = st.columns([1.05, 0.95])

    with controls_col:
        action_cols = st.columns(3)
        with action_cols[0]:
            st.button("Reset Defaults", on_click=reset_defaults, use_container_width=True)
        with action_cols[1]:
            save_clicked = st.button("Save configuration", use_container_width=True)
        with action_cols[2]:
            generate_all = st.button("Genereer PNGs", use_container_width=True)

        settings_left, settings_right = st.columns(2)

        with settings_left:
            st.subheader("Audio & Transform")
            transform = st.selectbox(
                "Transform type",
                ["mel", "stft", "cqt"],
                index=["mel", "stft", "cqt"].index(str(st.session_state.transform)),
                key="transform",
                help="Select type of spectrogram. 'mel' emphasizes perceptual frequencies, 'cqt' is logarithmic per octave, 'stft' is linear."
            )
            sample_rate = st.selectbox(
                "Sample rate (Hz)",
                [24000, 48000],
                index=[24000, 48000].index(int(st.session_state.sample_rate)),
                key="sample_rate",
                help="Audio sampling rate. Higher = better frequency resolution at high frequencies, but larger files."
            )
            n_fft_options = [2048, 4096, 8192] if sample_rate == 48000 else [2048, 4096]
            if int(st.session_state.n_fft) not in n_fft_options:
                st.session_state.n_fft = n_fft_options[0]
            n_fft = st.selectbox(
                "FFT size",
                n_fft_options,
                index=n_fft_options.index(int(st.session_state.n_fft)),
                key="n_fft",
                help="Number of FFT points. Larger = better frequency resolution, lower temporal resolution."
            )
            hop_ratio = st.slider(
                "Hop ratio (fraction of FFT size)",
                0.05,
                0.25,
                float(st.session_state.hop_ratio),
                step=0.01,
                key="hop_ratio",
                help="Overlap between consecutive FFT windows. Smaller = smoother spectrogram over time."
            )
            window = st.selectbox(
                "Window function",
                ["hann", "hamming", "blackman", "bartlett"],
                index=["hann", "hamming", "blackman", "bartlett"].index(str(st.session_state.window)),
                key="window",
                help="Windowing function for FFT. Affects spectral leakage and sharpness of frequency peaks."
            )

            st.subheader("Frequency & Scaling")
            use_log_frequency = st.checkbox(
                "Logarithmic frequency axis",
                value=bool(st.session_state.use_log_frequency),
                key="use_log_frequency",
                help="Display y-axis on logarithmic scale. Useful for bird sounds with wide frequency range."
            )
            fmin = st.number_input(
                "Min frequency (Hz)",
                min_value=0.0,
                max_value=96000.0,
                value=float(st.session_state.get("fmin") or 200.0),
                key="fmin",
                help="Lowest frequency to display. Frequencies below this are ignored."
            )
            fmax = st.number_input(
                "Max frequency (Hz)",
                min_value=0.0,
                max_value=96000.0,
                value=float(st.session_state.get("fmax") or 12000.0),
                key="fmax",
                help="Highest frequency to display."
            )
            mel_default = st.session_state.get("n_mels", working_cfg.get("n_mels", MEL_OPTIONS[0]))
            if int(mel_default) not in MEL_OPTIONS:
                mel_default = MEL_OPTIONS[0]
                st.session_state.n_mels = mel_default
            n_mels = st.selectbox(
                "Number of Mel bins",
                MEL_OPTIONS,
                index=MEL_OPTIONS.index(int(mel_default)),
                key="n_mels",
                help="Number of frequency bins for Mel-spectrogram. More bins = finer frequency resolution."
            )
            power = st.number_input(
                "Spectrogram power",
                value=float(st.session_state.power),
                min_value=1.0,
                max_value=4.0,
                key="power",
                help="Exponent applied to magnitude. Usually 2.0 = power spectrogram."
            )
            pcen_enabled = st.checkbox(
                "Enable PCEN (per-channel energy normalization)",
                value=bool(st.session_state.pcen_enabled),
                key="pcen_enabled",
                help="Enhances weak signals and suppresses constant background noise."
            )
            per_freq_norm = st.checkbox(
                "Per-frequency normalization",
                value=bool(st.session_state.per_frequency_normalization),
                key="per_frequency_normalization",
                help="Normalize each frequency band independently. Makes spectrogram contrast more uniform."
            )
            ref_power = st.number_input(
                "Reference power (dB)",
                value=float(st.session_state.ref_power),
                min_value=0.0001,
                key="ref_power",
                help="Reference value for amplitude-to-dB conversion."
            )
            top_db = st.number_input(
                "Top dB (clipping)",
                value=float(st.session_state.get("top_db") or 45.0),
                min_value=1.0,
                max_value=120.0,
                key="top_db",
                help="Clips the dynamic range of the spectrogram for visualization."
            )
            dynamic_range = st.number_input(
                "Dynamic range (dB)",
                value=float(st.session_state.dynamic_range),
                min_value=10.0,
                key="dynamic_range",
                help="Contrast between max and min dB displayed in image."
            )

        with settings_right:
            st.subheader("Segmentation (syllables)")
            rms_frame_length = st.number_input(
                "RMS frame length (samples)",
                value=int(st.session_state.rms_frame_length),
                key="rms_frame_length",
                help="Number of samples per RMS calculation. Larger = smoother energy envelope."
            )
            rms_threshold = st.slider(
                "RMS threshold (0-1)",
                0.0,
                1.0,
                float(st.session_state.rms_threshold),
                step=0.01,
                key="rms_threshold",
                help="Minimum normalized RMS to consider a segment. Lower = more segments."
            )
            min_segment_duration = st.number_input(
                "Min segment duration (s)",
                value=float(st.session_state.min_segment_duration),
                min_value=0.01,
                max_value=10.0,
                key="min_segment_duration",
                help="Segments shorter than this are ignored."
            )
            min_silence_duration = st.number_input(
                "Min silence to separate (s)",
                value=float(st.session_state.min_silence_duration),
                min_value=0.01,
                max_value=10.0,
                key="min_silence_duration",
                help="Minimum silent interval to split two segments."
            )
            sigmoid_k = st.slider(
                "Sigmoid steepness (soft-threshold)",
                1.0,
                50.0,
                float(st.session_state.sigmoid_k),
                step=1.0,
                key="sigmoid_k",
                help="Softens edges of RMS threshold using sigmoid. Higher = sharper cut, lower = smoother detection."
            )
            overlay_segments = st.checkbox(
                "Overlay segments on spectrogram",
                value=bool(st.session_state.overlay_segments),
                key="overlay_segments",
                help="Draw detected segment boundaries directly on the spectrogram for visual inspection."
            )

            st.subheader("Visualization & Output")
            current_colormap_value = _prefer_light_colormap(st.session_state.get("colormap", working_cfg.get("colormap", COLORMAP_OPTIONS[0])))
            if current_colormap_value not in COLORMAP_OPTIONS:
                current_colormap_value = COLORMAP_OPTIONS[0]
                st.session_state.colormap = current_colormap_value
            colormap = st.selectbox(
                "Colormap",
                COLORMAP_OPTIONS,
                index=COLORMAP_OPTIONS.index(current_colormap_value),
                key="colormap",
            )
            fig_width = st.number_input("Figure width (inches)", value=float(st.session_state.fig_width), key="fig_width")
            fig_height = st.number_input("Figure height (inches)", value=float(st.session_state.fig_height), key="fig_height")
            dpi = st.number_input("DPI", value=int(st.session_state.dpi), min_value=72, key="dpi")
            title = st.text_input("Title", value=str(st.session_state.title), key="title")
            output_dir = st.text_input("Output directory", value=str(st.session_state.output_directory), key="output_directory")
            segment_dir = st.text_input("Segment directory (WAVs)", value=str(st.session_state.segment_directory), key="segment_directory")

        hop_length_calc = int(n_fft * hop_ratio)
        st.session_state.hop_length = hop_length_calc
        updated = st.session_state["working_config"].copy()
        updated.update({
            "transform": transform,
            "sample_rate": sample_rate,
            "n_fft": n_fft,
            "hop_ratio": hop_ratio,
            "hop_length": hop_length_calc,
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
            "sigmoid_k": sigmoid_k,
            "overlay_segments": overlay_segments,
            "colormap": colormap,
            "fig_width": fig_width,
            "fig_height": fig_height,
            "dpi": dpi,
            "title": title,
            "output_directory": output_dir,
            "segment_directory": segment_dir
        })
        st.session_state["working_config"] = updated
        current_cfg = SpectrogramConfig.from_dict(updated)
        st.session_state.force_refresh = st.session_state.force_refresh or (st.session_state.last_preview_config != updated)

        if save_clicked:
            save_config(current_cfg)
            st.session_state.base_config = current_cfg.to_dict()
            st.success("Configuration saved!")

        if generate_all:
            current_cfg.input_directory.mkdir(parents=True, exist_ok=True)
            current_cfg.output_directory.mkdir(parents=True, exist_ok=True)
            for wav in current_cfg.input_directory.glob("*.wav"):
                generate_spectrogram(
                    wav,
                    current_cfg,
                    overlay_segments=overlay_segments,
                    export_segments_flag=True
                )
            st.success(f"Processing complete! Segments exported to WAVs in {current_cfg.segment_directory}")

    available_wavs: List[Path] = sorted(current_cfg.input_directory.glob("*.wav"))
    fallback_wavs = sorted(PROJECT_ROOT.glob("*.wav"))
    wav_pool = available_wavs if available_wavs else fallback_wavs
    if wav_pool and not st.session_state.get("preview_wav"):
        st.session_state.preview_wav = str(wav_pool[0])

    with preview_col:
        st.subheader("Live preview")
        preview_options = [str(p) for p in wav_pool]
        preview_label = lambda p: Path(p).name  # noqa: E731
        selected_index = preview_options.index(st.session_state.preview_wav) if preview_options and st.session_state.get("preview_wav") in preview_options else 0 if preview_options else 0
        selected_wav = st.selectbox(
            "Preview WAV",
            options=preview_options,
            index=selected_index if preview_options else 0,
            format_func=preview_label,
            key="preview_wav",
        ) if preview_options else None

        current_cfg.output_directory.mkdir(parents=True, exist_ok=True)
        Path(current_cfg.segment_directory).mkdir(parents=True, exist_ok=True)

        uploaded = st.file_uploader("Upload a WAV to generate PNG & segments", type=["wav"])
        if uploaded is not None:
            wav_path = current_cfg.output_directory / f"user_{uploaded.name}"
            wav_path.write_bytes(uploaded.read())
            st.session_state.preview_wav = str(wav_path)
            st.session_state.force_refresh = True
            png_path = generate_spectrogram(
                wav_path,
                current_cfg,
                overlay_segments=overlay_segments,
                export_segments_flag=True
            )
            st.session_state.preview_path = png_path
            st.session_state.last_preview_config = updated
            st.session_state.last_preview_wav = wav_path
            st.success(f"Generated {png_path.name}")
            st.image(str(png_path))
        else:
            preview_cfg_state: Dict = st.session_state["working_config"]
            cached_preview = st.session_state.get("preview_path")
            last_preview_wav = st.session_state.get("last_preview_wav")
            chosen_wav = Path(selected_wav) if selected_wav else None
            should_refresh = st.session_state.force_refresh or preview_cfg_state != st.session_state.get("last_preview_config") or chosen_wav != last_preview_wav

            if chosen_wav and chosen_wav.exists() and should_refresh:
                preview_path = generate_spectrogram(
                    chosen_wav,
                    current_cfg,
                    overlay_segments=overlay_segments,
                    export_segments_flag=False
                )
                st.session_state.preview_path = preview_path
                st.session_state.last_preview_config = preview_cfg_state.copy()
                st.session_state.last_preview_wav = chosen_wav
                st.session_state.force_refresh = False
                cached_preview = preview_path

            if cached_preview and Path(cached_preview).exists():
                st.image(str(cached_preview), caption=f"Preview: {Path(cached_preview).name}", use_column_width=True)
            else:
                st.info("Plaats een WAV in de input map of upload er een om een live preview te zien.")


if __name__ == "__main__":
    render()
