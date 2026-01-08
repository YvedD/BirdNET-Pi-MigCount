from __future__ import annotations
APP_DESCRIPTION = """
Streamlit UI for experimenting with spectrogram parameters.

Features:
- Adjust mel or STFT transforms
- Tune windowing, FFT size, hop ratio (overlap)
- Control frequency bounds, mel bins, scaling, and power
- Enable PCEN with optional dB shaping
- Optional preprocessing: lightweight noise reduction and HPF
- Visualize results directly in the UI
- Upload single WAVs for testing
- Save configuration for reproducible experiments
- Export a human-readable snapshot of the current settings

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
    generate_spectrogram,
    load_config,
    save_config,
)

PRESET_SIZES = [256, 512, 1024, 2048, 4096, 8192]
MEL_OPTIONS = [128, 512, 1024, 2048, 4096]
WINDOW_OPTIONS = ["hann", "hamming", "blackman"]
TRANSFORM_OPTIONS = ["mel", "stft"]
HOP_MIN = 0.03125
HOP_MAX = 0.5
FMIN_RANGE = (500.0, 3000.0)
FMAX_RANGE = (8000.0, 16000.0)
COLORMAP_OPTIONS = [
    "soft_gray",
    "hot",
    "viridis",
    "plasma",
    "magma",
    "inferno",
    "cividis",
    "gray_r",
]
COMPACT_STYLE = """
<style>
    div.block-container{padding-top:0.15rem;padding-bottom:0.2rem;max-width:1400px;}
    section[data-testid="stSidebar"]{font-size:0.8rem;}
    div[data-testid="stMarkdown"] p, label, .stSelectbox label, .stSlider label,
    .stNumberInput label, .stTextInput label, .stCheckbox label{font-size:0.8rem;margin-bottom:0.08rem;}
    .stSelectbox, .stNumberInput, .stSlider, .stTextInput, .stCheckbox{padding-top:0.02rem;padding-bottom:0.02rem;}
    h1, h2, h3, h4{font-size:1rem;margin-bottom:0.25rem;}
    .stButton>button{padding:0.28rem 0.33rem;font-size:0.86rem;}
    [data-testid="stHorizontalBlock"]{row-gap:0.08rem;}
    .stSlider [data-baseweb="slider"]{height:22px;}
    .section-title{font-size:13pt;font-weight:700;margin:0.15rem 0 0.05rem;}
</style>
"""

HARD_DEFAULTS = {
    "input_directory": "experimental/input",
    "output_directory": "experimental/output",
    "transform": "mel",
    "sample_rate": 48000,
    "n_fft": 2048,
    "hop_ratio": 0.0625,
    "hop_length": 128,
    "window": "hann",
    "use_log_frequency": True,
    "fmin": 1200.0,
    "fmax": 12000.0,
    "n_mels": 1024,
    "power": 1.0,
    "pcen_enabled": False,
    "pcen_bias": 2.0,
    "pcen_gain": 0.85,
    "pcen_apply_top_db": False,
    "pcen_apply_dynamic_range": False,
    "pcen_apply_ref_power": False,
    "per_frequency_normalization": False,
    "ref_power": 1.0,
    "top_db": 80,
    "dynamic_range": 60,
    "contrast_percentile": None,
    "noise_reduction": False,
    "high_pass_filter": False,
    "high_pass_cutoff": 800.0,
    "colormap": "soft_gray",
    "fig_width": 10.0,
    "fig_height": 5.0,
    "dpi": 300,
    "max_duration_sec": None,
    "title": "Experimental Spectrogram",
    "rms_frame_length": 1024,
    "rms_threshold": 0.2,
}


def _prefer_light_colormap(name: str) -> str:
    if name in ("gray_r", "lightgray", "lichtgrijs"):
        return "soft_gray"
    return name


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
        "Visualize adjustments instantly for quick comparisons."
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

    def _export_settings(cfg: SpectrogramConfig) -> Path:
        desktop = Path.home() / "Desktop"
        desktop.mkdir(parents=True, exist_ok=True)
        out_path = desktop / "BirdNET-Pi-MigCount-settings.txt"
        lines = [
            "BirdNET-Pi-MigCount spectrogram settings",
            f"Transform: {cfg.transform}",
            f"Sample rate: {cfg.sample_rate} Hz",
            f"Window: {cfg.window}",
            f"FFT size: {cfg.n_fft}",
            f"Hop ratio: {cfg.hop_ratio:.5f}",
            f"Hop length: {cfg.hop_length} samples",
            f"Frequency range: {cfg.fmin} Hz – {cfg.fmax} Hz",
            f"Mel bins: {cfg.n_mels}",
            f"Power: {cfg.power}",
            f"PCEN enabled: {cfg.pcen_enabled}",
            f"PCEN bias: {cfg.pcen_bias}",
            f"PCEN gain/alpha: {cfg.pcen_gain}",
            f"PCEN apply top_dB: {cfg.pcen_apply_top_db}",
            f"PCEN apply dynamic range: {cfg.pcen_apply_dynamic_range}",
            f"PCEN apply ref power: {cfg.pcen_apply_ref_power}",
            f"Top dB (classic dB): {cfg.top_db}",
            f"Dynamic range (classic dB): {cfg.dynamic_range}",
            f"Reference power: {cfg.ref_power}",
            f"Noise reduction enabled: {cfg.noise_reduction}",
            f"High-pass filter enabled: {cfg.high_pass_filter}",
            f"HPF cutoff: {cfg.high_pass_cutoff} Hz",
            f"Output directory: {cfg.output_directory}",
            f"Colormap: {cfg.colormap}",
        ]
        out_path.write_text("\n".join(lines), encoding="utf-8")
        return out_path

    with controls_col:
        action_cols = st.columns(4)
        with action_cols[0]:
            st.button("Reset Defaults", on_click=reset_defaults, use_container_width=True)
        with action_cols[1]:
            save_clicked = st.button("Save configuration", use_container_width=True)
        with action_cols[2]:
            keep_settings = st.button("Keep these settings", use_container_width=True)
        with action_cols[3]:
            generate_all = st.button("Genereer PNGs", use_container_width=True)

        st.markdown('<div class="section-title">Spectrogram core</div>', unsafe_allow_html=True)
        transform_default = current_value("transform", working_cfg.get("transform", "mel"))
        if str(transform_default) not in TRANSFORM_OPTIONS:
            transform_default = TRANSFORM_OPTIONS[0]
            st.session_state.transform = transform_default
        sample_rate_default = int(current_value("sample_rate", working_cfg.get("sample_rate", 48000)))
        if sample_rate_default not in (24000, 48000):
            sample_rate_default = 48000
            st.session_state.sample_rate = sample_rate_default
        window_default = str(current_value("window", working_cfg.get("window", "hann")))
        core_cols = st.columns(3)
        with core_cols[0]:
            transform = st.selectbox(
                "Transform",
                TRANSFORM_OPTIONS,
                index=TRANSFORM_OPTIONS.index(str(transform_default)),
                key="transform",
                help="Choose mel or linear STFT representation."
            )
        with core_cols[1]:
            sample_rate = st.selectbox(
                "Sample rate (Hz)",
                [24000, 48000],
                index=[24000, 48000].index(sample_rate_default),
                key="sample_rate",
                help="Higher sample rate keeps more high-frequency detail."
            )
        with core_cols[2]:
            window = st.selectbox(
                "Window",
                WINDOW_OPTIONS,
                index=WINDOW_OPTIONS.index(window_default if window_default in WINDOW_OPTIONS else WINDOW_OPTIONS[0]),
                key="window",
                help="Windowing function for FFT."
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
                help="Number of FFT points. Larger = sharper frequency resolution."
            )
        hop_ratio_default = float(current_value("hop_ratio", working_cfg.get("hop_ratio", 0.0625)))
        with fft_cols[1]:
            hop_ratio = st.slider(
                "Hop ratio",
                HOP_MIN,
                HOP_MAX,
                min(max(hop_ratio_default, HOP_MIN), HOP_MAX),
                step=0.001,
                format="%.5f",
                key="hop_ratio",
                help="Fraction of FFT size used as hop (controls overlap and temporal detail)."
            )
        hop_length_calc = int(n_fft * hop_ratio)
        with fft_cols[2]:
            st.metric("Hop length (samples)", hop_length_calc)
            frame_ms = (hop_length_calc / sample_rate) * 1000.0
            st.caption(f"Frame duur: {frame_ms:.2f} ms")

        st.markdown('<div class="section-title">Frequency & resolution</div>', unsafe_allow_html=True)
        fmin_default = float(current_value("fmin", working_cfg.get("fmin") or FMIN_RANGE[0]))
        fmax_default = float(current_value("fmax", working_cfg.get("fmax") or FMAX_RANGE[1]))
        freq_cols = st.columns(3)
        with freq_cols[0]:
            fmin = st.slider(
                "Minimum frequency (Hz)",
                FMIN_RANGE[0],
                FMIN_RANGE[1],
                min(max(fmin_default, FMIN_RANGE[0]), FMIN_RANGE[1]),
                step=50.0,
                key="fmin",
            )
        with freq_cols[1]:
            fmax = st.slider(
                "Maximum frequency (Hz)",
                FMAX_RANGE[0],
                FMAX_RANGE[1],
                min(max(fmax_default, FMAX_RANGE[0]), FMAX_RANGE[1]),
                step=250.0,
                key="fmax",
            )
            if fmax <= fmin:
                fmax = min(FMAX_RANGE[1], fmin + 500.0)
                st.session_state.fmax = fmax
        n_mels_default = current_value("n_mels", working_cfg.get("n_mels", MEL_OPTIONS[2]))
        if int(n_mels_default) not in MEL_OPTIONS:
            n_mels_default = MEL_OPTIONS[2]
            st.session_state.n_mels = n_mels_default
        with freq_cols[2]:
            n_mels = st.selectbox(
                "Mel bins",
                MEL_OPTIONS,
                index=MEL_OPTIONS.index(int(n_mels_default)),
                key="n_mels",
                help="Higher values reduce blocky low-frequency artefacts."
            )

        st.markdown('<div class="section-title">Scaling</div>', unsafe_allow_html=True)
        scaling_cols = st.columns(2)
        with scaling_cols[0]:
            power = st.slider(
                "Spectrogram power",
                0.25,
                2.0,
                float(current_value("power", working_cfg.get("power", 1.0))),
                step=0.05,
                key="power",
                help="Exponent applied to magnitude before scaling."
            )
        with scaling_cols[1]:
            use_log_frequency = transform == "stft"
            st.caption("Log frequency is auto-enabled for STFT.")

        st.markdown('<div class="section-title">Appearance</div>', unsafe_allow_html=True)
        appearance_cols = st.columns(2)
        colormap_default = _prefer_light_colormap(str(current_value("colormap", working_cfg.get("colormap", COLORMAP_OPTIONS[0]))))
        if colormap_default not in COLORMAP_OPTIONS:
            colormap_default = COLORMAP_OPTIONS[0]
        with appearance_cols[0]:
            colormap = st.selectbox(
                "Colormap",
                COLORMAP_OPTIONS,
                index=COLORMAP_OPTIONS.index(colormap_default),
                key="colormap",
                format_func=lambda name: "Lichtgrijs" if name in ("soft_gray", "lichtgrijs") else name,
            )
        with appearance_cols[1]:
            st.caption("Kies een kleurschema, inclusief lichtgrijs of hot.")

        st.markdown('<div class="section-title">PCEN</div>', unsafe_allow_html=True)
        pcen_enabled = st.checkbox(
            "Enable PCEN",
            value=bool(current_value("pcen_enabled", working_cfg.get("pcen_enabled", False))),
            key="pcen_enabled",
            help="Adaptive gain control to lift weak syllables without crushing peaks."
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
            )
        with pcen_cols[1]:
            pcen_gain = st.slider(
                "PCEN gain (alpha)",
                0.1,
                1.0,
                float(current_value("pcen_gain", working_cfg.get("pcen_gain", 0.85))),
                step=0.01,
                key="pcen_gain",
                disabled=not pcen_enabled,
            )
        opt_cols = st.columns(3)
        with opt_cols[0]:
            pcen_apply_top_db = st.checkbox(
                "Apply top dB after PCEN",
                value=bool(current_value("pcen_apply_top_db", working_cfg.get("pcen_apply_top_db", False))),
                key="pcen_apply_top_db",
                disabled=not pcen_enabled,
            )
        with opt_cols[1]:
            pcen_apply_dynamic_range = st.checkbox(
                "Apply dynamic range after PCEN",
                value=bool(current_value("pcen_apply_dynamic_range", working_cfg.get("pcen_apply_dynamic_range", False))),
                key="pcen_apply_dynamic_range",
                disabled=not pcen_enabled,
            )
        with opt_cols[2]:
            pcen_apply_ref_power = st.checkbox(
                "Apply ref power after PCEN",
                value=bool(current_value("pcen_apply_ref_power", working_cfg.get("pcen_apply_ref_power", False))),
                key="pcen_apply_ref_power",
                disabled=not pcen_enabled,
            )

        st.markdown('<div class="section-title">Classic dB scaling (when PCEN is off)</div>', unsafe_allow_html=True)
        db_cols = st.columns(3)
        with db_cols[0]:
            top_db = st.number_input(
                "Top dB",
                min_value=40.0,
                max_value=100.0,
                value=float(current_value("top_db", working_cfg.get("top_db", 80.0))),
                key="top_db",
                disabled=pcen_enabled,
            )
        with db_cols[1]:
            dynamic_range = st.number_input(
                "Dynamic range (dB)",
                min_value=30.0,
                max_value=80.0,
                value=float(current_value("dynamic_range", working_cfg.get("dynamic_range", 60.0))),
                key="dynamic_range",
                disabled=pcen_enabled,
            )
        with db_cols[2]:
            ref_power = st.number_input(
                "Reference power",
                min_value=0.1,
                max_value=2.0,
                value=float(current_value("ref_power", working_cfg.get("ref_power", 1.0))),
                key="ref_power",
                disabled=pcen_enabled,
            )

        st.markdown('<div class="section-title">Preprocessing</div>', unsafe_allow_html=True)
        pre_cols = st.columns(3)
        with pre_cols[0]:
            noise_reduction = st.checkbox(
                "Noise reduction",
                value=bool(current_value("noise_reduction", working_cfg.get("noise_reduction", False))),
                key="noise_reduction",
                help="Lightweight spectral gating."
            )
        with pre_cols[1]:
            high_pass_filter = st.checkbox(
                "High-pass filter",
                value=bool(current_value("high_pass_filter", working_cfg.get("high_pass_filter", False))),
                key="high_pass_filter",
                help="Suppress rumble below the band of interest."
            )
        with pre_cols[2]:
            hp_max = min(2000.0, float(sample_rate / 2.0 - 100.0))
            hpf_default = float(current_value("high_pass_cutoff", working_cfg.get("high_pass_cutoff", 800.0)))
            if hpf_default > hp_max:
                hpf_default = hp_max
                st.session_state.high_pass_cutoff = hp_max
            high_pass_cutoff = st.slider(
                "HPF cutoff (Hz)",
                500.0,
                hp_max,
                hpf_default,
                step=25.0,
                key="high_pass_cutoff",
                disabled=not high_pass_filter,
            )

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
            "pcen_apply_top_db": pcen_apply_top_db,
            "pcen_apply_dynamic_range": pcen_apply_dynamic_range,
            "pcen_apply_ref_power": pcen_apply_ref_power,
            "per_frequency_normalization": bool(current_value("per_frequency_normalization", working_cfg.get("per_frequency_normalization", False))),
            "ref_power": ref_power,
            "top_db": top_db,
            "dynamic_range": dynamic_range,
            "noise_reduction": noise_reduction,
            "high_pass_filter": high_pass_filter,
            "high_pass_cutoff": high_pass_cutoff,
            "colormap": _prefer_light_colormap(colormap),
        })
        st.session_state["working_config"] = updated
        current_cfg = SpectrogramConfig.from_dict(updated)
        st.session_state.force_refresh = st.session_state.force_refresh or (st.session_state.last_preview_config != updated)

        if save_clicked:
            save_config(current_cfg)
            st.session_state.base_config = current_cfg.to_dict()
            st.success("Configuration saved!")

        if keep_settings:
            settings_path = _export_settings(current_cfg)
            st.success(f"Settings saved to {settings_path}")

        if generate_all:
            current_cfg.input_directory.mkdir(parents=True, exist_ok=True)
            current_cfg.output_directory.mkdir(parents=True, exist_ok=True)
            for wav in current_cfg.input_directory.glob("*.wav"):
                generate_spectrogram(
                    wav,
                    current_cfg,
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
                overlay_segments=False,
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
                    overlay_segments=False,
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
