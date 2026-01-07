from __future__ import annotations
APP_DESCRIPTION = """
Streamlit UI for experimenting with spectrogram parameters and syllable segmentation.

Features:
- Adjust spectrogram transforms (mel, STFT, CQT)
- Tune windowing, FFT size, hop ratio (overlap)
- Control frequency bounds, scaling, and power
- Enable PCEN and per-frequency normalization
- Detect segments (syllables/notes) and visualize them on the spectrogram
- Sigmoid soft-threshold for smoothing segment edges
- Optional overlay of segments on the spectrogram image
- Visualize results directly in the UI
- Upload single WAVs for testing
- Save configuration for reproducible experiments

All changes are saved to experimental/spectrogram_config.json
and isolated from BirdNET production pipeline.
"""
__doc__ = APP_DESCRIPTION

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
    generate_spectrogram,
    load_config,
    save_config,
)

PRESET_SIZES = [256, 512, 1024, 2048, 4096, 8192]
MEL_OPTIONS = PRESET_SIZES
COLORMAP_OPTIONS = ["soft_gray", "viridis", "plasma", "magma", "inferno", "cividis", "gray_r"]
COMPACT_STYLE = """
<style>
    :root {
        --primary-color:#5c7cfa;
        --text-color:#1f2937;
    }
    body, .stApp {
        background-color:#f7f9fc;
        color:var(--text-color);
    }
    div.block-container{padding-top:0.35rem;padding-bottom:0.6rem;max-width:1600px;}
    section[data-testid="stSidebar"]{font-size:0.85rem;}
    div[data-testid="stMarkdown"] p, label, .stSelectbox label, .stSlider label,
    .stNumberInput label, .stTextInput label, .stCheckbox label{font-size:0.85rem;margin-bottom:0.2rem;}
    .stSelectbox, .stNumberInput, .stSlider, .stTextInput, .stCheckbox{padding-top:0.1rem;padding-bottom:0.1rem;}
    h1, h2, h3, h4{font-size:1.05rem;margin-bottom:0.4rem;}
    .stButton>button{padding:0.35rem 0.4rem;font-size:0.9rem;}
    [data-testid="stHorizontalBlock"]{row-gap:0.2rem;}
    .stTabs [data-baseweb="tab-list"]{gap:0.25rem;}
</style>
"""

HARD_DEFAULTS = {
    "input_directory": "experimental/input",
    "output_directory": "experimental/output",
    "transform": "stft",
    "sample_rate": 48000,
    "n_fft": 4096,
    "hop_ratio": 0.125,
    "hop_length": 512,
    "window": "hann",
    "use_log_frequency": True,
    "fmin": 1000.0,
    "fmax": 12000.0,
    "n_mels": 512,
    "power": 2.0,
    "pcen_enabled": False,
    "pcen_bias": 2.0,
    "pcen_gain": 0.98,
    "per_frequency_normalization": False,
    "ref_power": 1.0,
    "top_db": 80,
    "dynamic_range": 80,
    "contrast_percentile": None,
    "noise_reduction": False,
    "high_pass_filter": False,
    "high_pass_cutoff": 300.0,
    "colormap": "soft_gray",
    "fig_width": 12.0,
    "fig_height": 6.0,
    "dpi": 300,
    "max_duration_sec": None,
    "title": "Experimental Spectrogram",
    "rms_frame_length": 1024,
    "rms_threshold": 0.2,
    "min_segment_duration": 0.05,
    "min_silence_duration": 0.05,
    "segment_directory": "experimental/segments",
    "sigmoid_k": 20.0,
    "overlay_segments": True,
}


def _prefer_light_colormap(name: str) -> str:
    return "soft_gray" if name == "gray_r" else name


def _init_state(cfg: SpectrogramConfig) -> None:
    hard_defaults = SpectrogramConfig.from_dict(HARD_DEFAULTS).to_dict()
    base_config = cfg.to_dict()
    base_config["colormap"] = _prefer_light_colormap(base_config.get("colormap", hard_defaults["colormap"]))
    if "hard_defaults" not in st.session_state:
        st.session_state.hard_defaults = hard_defaults
    if "base_config" not in st.session_state:
        st.session_state.base_config = {**hard_defaults, **base_config}
    st.session_state.setdefault("working_config", st.session_state.base_config.copy())
    st.session_state["working_config"].setdefault("colormap", base_config["colormap"])
    st.session_state.setdefault("last_preview_config", {})
    st.session_state.setdefault("force_refresh", True)


def render():
    st.set_page_config(layout="wide")
    st.markdown(COMPACT_STYLE, unsafe_allow_html=True)
    st.title("Experimental Spectrogram Controls")
    st.caption(
        "Tweak parameters and visualize effect immediately. "
        "Detected syllables are shown as overlays for quick inspection."
    )

    cfg = load_config(CONFIG_PATH)
    _init_state(cfg)

    def reset_defaults() -> None:
        defaults = st.session_state.get("hard_defaults", st.session_state.base_config)
        st.session_state.base_config = defaults.copy()
        st.session_state.working_config = defaults.copy()
        for key, value in defaults.items():
            st.session_state[key] = value
        st.session_state.force_refresh = True
        st.session_state.last_preview_config = {}

    working_cfg = st.session_state["working_config"]
    def current_value(key: str, default):
        return st.session_state.get(key, working_cfg.get(key, default))

    controls_col, preview_col = st.columns([1.05, 0.95])

    with controls_col:
        action_cols = st.columns(3)
        with action_cols[0]:
            st.button("Reset Defaults", on_click=reset_defaults, use_container_width=True)
        with action_cols[1]:
            save_clicked = st.button("Save configuration", use_container_width=True)
        with action_cols[2]:
            generate_all = st.button("Genereer PNGs", use_container_width=True)

        st.subheader("Audio & Transform")
        transform_default = current_value("transform", working_cfg.get("transform", "stft"))
        sample_rate_default = int(current_value("sample_rate", working_cfg.get("sample_rate", 48000)))
        transform_cols = st.columns(2)
        with transform_cols[0]:
            transform = st.selectbox(
                "Transform",
                ["mel", "stft", "cqt"],
                index=["mel", "stft", "cqt"].index(str(transform_default)),
                key="transform",
                help="Select type of spectrogram. 'mel' emphasizes perceptual frequencies, 'cqt' is logarithmic per octave, 'stft' is linear."
            )
        with transform_cols[1]:
            sample_rate = st.selectbox(
                "Sample rate (Hz)",
                [24000, 48000],
                index=[24000, 48000].index(sample_rate_default),
                key="sample_rate",
                help="Audio sampling rate. Higher = better frequency resolution at high frequencies, but larger files."
            )

        fft_cols = st.columns(3)
        n_fft_default = int(current_value("n_fft", working_cfg.get("n_fft", PRESET_SIZES[3])))
        if n_fft_default not in PRESET_SIZES:
            n_fft_default = PRESET_SIZES[3]
            st.session_state.n_fft = n_fft_default
        with fft_cols[0]:
            n_fft = st.selectbox(
                "FFT size",
                PRESET_SIZES,
                index=PRESET_SIZES.index(int(n_fft_default)),
                key="n_fft",
                help="Number of FFT points. Larger = better frequency resolution, lower temporal resolution."
            )
        hop_ratio_default = float(current_value("hop_ratio", working_cfg.get("hop_ratio", 0.125)))
        with fft_cols[1]:
            hop_ratio = st.slider(
                "Hop ratio",
                0.05,
                0.25,
                hop_ratio_default,
                step=0.01,
                key="hop_ratio",
                help="Fraction of FFT size used as hop (controls overlap)."
            )
        window_default = str(current_value("window", working_cfg.get("window", "hann")))
        with fft_cols[2]:
            window = st.selectbox(
                "Window",
                ["hann", "hamming", "blackman", "bartlett"],
                index=["hann", "hamming", "blackman", "bartlett"].index(window_default),
                key="window",
                help="Windowing function for FFT. Affects spectral leakage and sharpness of frequency peaks."
            )

        st.subheader("Frequency & Scaling")
        log_cols = st.columns(2)
        with log_cols[0]:
            use_log_frequency_default = bool(current_value("use_log_frequency", working_cfg.get("use_log_frequency", True)))
            use_log_frequency = st.checkbox(
                "Log frequency axis",
                value=use_log_frequency_default,
                key="use_log_frequency",
                help="Display y-axis on logarithmic scale. Useful for bird sounds with wide frequency range."
            )
        with log_cols[1]:
            pcen_enabled = st.checkbox(
                "Enable PCEN",
                value=bool(current_value("pcen_enabled", working_cfg.get("pcen_enabled", False))),
                key="pcen_enabled",
                help="Enhances weak signals and suppresses constant background noise."
            )
        pcen_cols = st.columns(2)
        with pcen_cols[0]:
            pcen_bias = st.slider(
                "PCEN bias",
                0.5,
                10.0,
                float(current_value("pcen_bias", working_cfg.get("pcen_bias", 2.0))),
                step=0.1,
                key="pcen_bias",
                disabled=not pcen_enabled,
                help="Bias term added before compression. Higher values reduce gain on quiet regions."
            )
        with pcen_cols[1]:
            pcen_gain = st.slider(
                "PCEN gain (alpha)",
                0.1,
                1.0,
                float(current_value("pcen_gain", working_cfg.get("pcen_gain", 0.98))),
                step=0.01,
                key="pcen_gain",
                disabled=not pcen_enabled,
                help="Controls strength of PCEN automatic gain. Lower values increase compression."
            )
        filter_cols = st.columns(2)
        with filter_cols[0]:
            noise_reduction = st.checkbox(
                "Noise reduction",
                value=bool(current_value("noise_reduction", working_cfg.get("noise_reduction", False))),
                key="noise_reduction",
                help="Apply lightweight spectral noise gating before spectrogram generation."
            )
        with filter_cols[1]:
            high_pass_filter = st.checkbox(
                "High-pass filter",
                value=bool(current_value("high_pass_filter", working_cfg.get("high_pass_filter", False))),
                key="high_pass_filter",
                help="Software HPF to reduce low-frequency rumble before analysis."
            )
            hp_min = 20.0
            hp_max = max(hp_min + 10.0, float(sample_rate / 2.0 - 200.0))
            current_cutoff = float(current_value("high_pass_cutoff", working_cfg.get("high_pass_cutoff", 300.0)))
            if current_cutoff > hp_max:
                current_cutoff = hp_max
                st.session_state.high_pass_cutoff = hp_max
            high_pass_cutoff = st.slider(
                "HPF cutoff (Hz)",
                hp_min,
                hp_max,
                current_cutoff,
                step=10.0,
                key="high_pass_cutoff",
                disabled=not high_pass_filter,
                help="Cutoff frequency for the HPF (applied before spectrogram generation)."
            )

        freq_cols = st.columns(2)
        with freq_cols[0]:
            fmin = st.number_input(
                "Min frequency (Hz)",
                min_value=0.0,
                max_value=96000.0,
                value=float(current_value("fmin", working_cfg.get("fmin") or 1000.0)),
                key="fmin",
                help="Lowest frequency to display. Frequencies below this are ignored."
            )
            n_mels_default = current_value("n_mels", working_cfg.get("n_mels", MEL_OPTIONS[0]))
            if int(n_mels_default) not in MEL_OPTIONS:
                n_mels_default = MEL_OPTIONS[0]
                st.session_state.n_mels = n_mels_default
            n_mels = st.selectbox(
                "Mel bins",
                MEL_OPTIONS,
                index=MEL_OPTIONS.index(int(n_mels_default)),
                key="n_mels",
                help="Number of frequency bins for Mel-spectrogram. More bins = finer frequency resolution."
            )
        with freq_cols[1]:
            fmax = st.number_input(
                "Max frequency (Hz)",
                min_value=0.0,
                max_value=96000.0,
                value=float(current_value("fmax", working_cfg.get("fmax") or 12000.0)),
                key="fmax",
                help="Highest frequency to display (capped at 16kHz)."
            )
            power = st.slider(
                "Spectrogram power",
                0.25,
                2.5,
                float(current_value("power", working_cfg.get("power", 2.0))),
                step=0.25,
                key="power",
                help="Exponent applied to magnitude. Lower values brighten faint details."
            )

        norm_cols = st.columns(2)
        with norm_cols[0]:
            per_freq_norm = st.checkbox(
                "Per-frequency normalization",
                value=bool(current_value("per_frequency_normalization", working_cfg.get("per_frequency_normalization", False))),
                key="per_frequency_normalization",
                help="Normalize each frequency band independently. Makes spectrogram contrast more uniform."
            )
            ref_power = st.number_input(
                "Reference power (dB)",
                value=float(current_value("ref_power", working_cfg.get("ref_power", 1.0))),
                min_value=0.0001,
                key="ref_power",
                help="Reference value for amplitude-to-dB conversion."
            )
        with norm_cols[1]:
            top_db = st.number_input(
                "Top dB (clipping)",
                value=float(current_value("top_db", working_cfg.get("top_db") or 45.0)),
                min_value=1.0,
                max_value=120.0,
                key="top_db",
                help="Clips the dynamic range of the spectrogram for visualization."
            )
            dynamic_range = st.number_input(
                "Dynamic range (dB)",
                value=float(current_value("dynamic_range", working_cfg.get("dynamic_range", 80.0))),
                min_value=10.0,
                key="dynamic_range",
                help="Contrast between max and min dB displayed in image."
            )

        st.subheader("Segmentation (syllables)")
        rms_cols = st.columns(2)
        rms_default = int(current_value("rms_frame_length", working_cfg.get("rms_frame_length", 1024)))
        if rms_default not in PRESET_SIZES:
            rms_default = PRESET_SIZES[2]
            st.session_state.rms_frame_length = rms_default
        with rms_cols[0]:
            rms_frame_length = st.selectbox(
                "RMS frame (samples)",
                PRESET_SIZES,
                index=PRESET_SIZES.index(rms_default),
                key="rms_frame_length",
                help="Number of samples per RMS calculation. Larger = smoother energy envelope."
            )
            min_segment_duration = st.number_input(
                "Min segment (s)",
                value=float(current_value("min_segment_duration", working_cfg.get("min_segment_duration", 0.05))),
                min_value=0.01,
                max_value=10.0,
                key="min_segment_duration",
                help="Segments shorter than this are ignored."
            )
        with rms_cols[1]:
            rms_threshold = st.slider(
                "RMS threshold",
                0.0,
                1.0,
                float(current_value("rms_threshold", working_cfg.get("rms_threshold", 0.2))),
                step=0.01,
                key="rms_threshold",
                help="Minimum normalized RMS to consider a segment. Lower = more segments."
            )
            min_silence_duration = st.number_input(
                "Min silence (s)",
                value=float(current_value("min_silence_duration", working_cfg.get("min_silence_duration", 0.05))),
                min_value=0.01,
                max_value=10.0,
                key="min_silence_duration",
                help="Minimum silent interval to split two segments."
            )
        sigmoid_cols = st.columns(2)
        with sigmoid_cols[0]:
            sigmoid_k = st.slider(
                "Sigmoid k",
                1.0,
                50.0,
                float(current_value("sigmoid_k", working_cfg.get("sigmoid_k", 20.0))),
                step=1.0,
                key="sigmoid_k",
                help="Softens edges of RMS threshold using sigmoid. Higher = sharper cut, lower = smoother detection."
            )
        with sigmoid_cols[1]:
            overlay_segments = st.checkbox(
                "Overlay segments",
                value=bool(current_value("overlay_segments", working_cfg.get("overlay_segments", False))),
                key="overlay_segments",
                help="Draw detected segment boundaries directly on the spectrogram for visual inspection."
            )

        st.subheader("Visualization & Output")
        current_colormap_value = _prefer_light_colormap(st.session_state.get("colormap", working_cfg.get("colormap", COLORMAP_OPTIONS[0])))
        if current_colormap_value not in COLORMAP_OPTIONS:
            current_colormap_value = COLORMAP_OPTIONS[0]
            st.session_state.colormap = current_colormap_value
        colormap_row = st.columns(2)
        with colormap_row[0]:
            colormap = st.selectbox(
                "Colormap",
                COLORMAP_OPTIONS,
                index=COLORMAP_OPTIONS.index(current_colormap_value),
                key="colormap",
            )
            dpi = st.number_input("DPI", value=int(current_value("dpi", working_cfg.get("dpi", 300))), min_value=72, key="dpi")
        with colormap_row[1]:
            title = st.text_input("Title", value=str(current_value("title", working_cfg.get("title", ""))), key="title")
        size_cols = st.columns(2)
        with size_cols[0]:
            fig_width = st.number_input("Figure width (inches)", value=float(current_value("fig_width", working_cfg.get("fig_width", 12.0))), key="fig_width")
        with size_cols[1]:
            fig_height = st.number_input("Figure height (inches)", value=float(current_value("fig_height", working_cfg.get("fig_height", 6.0))), key="fig_height")
        path_cols = st.columns(2)
        with path_cols[0]:
            output_dir = st.text_input("Output directory", value=str(current_value("output_directory", working_cfg.get("output_directory", ""))), key="output_directory")
        with path_cols[1]:
            segment_dir = st.text_input(
                "Segment directory",
                value=str(current_value("segment_directory", working_cfg.get("segment_directory", ""))),
                key="segment_directory",
                help="Detected segments are only overlayed; WAV export is disabled."
            )

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
            "pcen_bias": pcen_bias,
            "pcen_gain": pcen_gain,
            "per_frequency_normalization": per_freq_norm,
            "ref_power": ref_power,
            "top_db": top_db,
            "dynamic_range": dynamic_range,
            "noise_reduction": noise_reduction,
            "high_pass_filter": high_pass_filter,
            "high_pass_cutoff": high_pass_cutoff,
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
                    export_segments_flag=False
                )
            st.success(f"Processing complete! PNGs saved in {current_cfg.output_directory}")

    available_wavs: List[Path] = sorted(current_cfg.input_directory.glob("*.wav"))
    fallback_wavs = sorted(PROJECT_ROOT.glob("*.wav"))
    wav_pool = available_wavs if available_wavs else fallback_wavs
    if wav_pool and not st.session_state.get("preview_wav"):
        st.session_state.preview_wav = str(wav_pool[0])

    with preview_col:
        st.subheader("Live preview")
        current_cfg.output_directory.mkdir(parents=True, exist_ok=True)
        Path(current_cfg.segment_directory).mkdir(parents=True, exist_ok=True)

        uploaded_path = None
        uploaded = st.file_uploader("Upload a WAV to generate a fresh PNG", type=["wav"])
        if uploaded is not None:
            wav_path = current_cfg.output_directory / f"user_{uploaded.name}"
            wav_path.write_bytes(uploaded.read())
            uploaded_path = wav_path
            st.session_state.preview_wav = str(wav_path)
            st.session_state.force_refresh = True
            png_path = generate_spectrogram(
                wav_path,
                current_cfg,
                overlay_segments=overlay_segments,
                export_segments_flag=False
            )
            st.session_state.preview_path = png_path
            st.session_state.last_preview_config = updated
            st.session_state.last_preview_wav = wav_path
            st.success(f"Generated {png_path.name}")
            st.image(str(png_path))

        preview_options = [str(p) for p in wav_pool]
        if uploaded_path:
            preview_options.append(str(uploaded_path))
        if st.session_state.get("preview_wav"):
            preview_options.append(st.session_state.preview_wav)
        preview_options_list = list(dict.fromkeys(preview_options))

        def preview_label(p: str) -> str:
            return Path(p).name

        selected_index = 0
        if preview_options_list and st.session_state.get("preview_wav") in preview_options_list:
            selected_index = preview_options_list.index(st.session_state.preview_wav)
        selected_wav = st.selectbox(
            "Preview WAV",
            options=preview_options_list,
            index=selected_index,
            format_func=preview_label,
            key="preview_wav",
        ) if preview_options_list else None

        if uploaded is None:
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
                st.image(str(cached_preview), caption=f"Preview: {Path(cached_preview).name}", use_container_width=True)
            else:
                st.info("Plaats een WAV in de input map of upload er een om een live preview te zien.")


if __name__ == "__main__":
    render()
