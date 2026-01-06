from pathlib import Path
import sys
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from experimental.spectrogram_generator import (
    CONFIG_PATH,
    SpectrogramConfig,
    generate_for_directory,
    generate_spectrogram,
    load_config,
)

def render():
    st.title("Experimental Spectrogram Controls")

    cfg = load_config(CONFIG_PATH)

    with st.form("params"):
        transform = st.selectbox("Transform", ["mel", "stft", "cqt"], index=["mel","stft","cqt"].index(cfg.transform))
        sample_rate = st.selectbox("Sample rate", [24000, 48000], index=[24000,48000].index(cfg.sample_rate))
        n_fft = st.selectbox("FFT size", [2048,4096,8192], index=[2048,4096,8192].index(cfg.n_fft))
        hop_ratio = st.selectbox("Hop ratio", [0.0625,0.125], index=[0.0625,0.125].index(cfg.hop_ratio))
        window = st.selectbox("Window", ["hann","blackman","hamming","bartlett"], index=0)

        fmin = st.number_input("fmin (Hz)", value=float(cfg.fmin or 0))
        fmax = st.number_input("fmax (Hz)", value=float(cfg.fmax or 16000))
        n_mels = st.selectbox("Mel bins", [256,512,1024], index=[256,512,1024].index(cfg.n_mels))
        power = st.number_input("Power", value=cfg.power)
        pcen = st.checkbox("PCEN", value=cfg.pcen_enabled)

        submit = st.form_submit_button("Save")

    if submit:
        SpectrogramConfig.from_dict({
            **cfg.__dict__,
            "transform": transform,
            "sample_rate": sample_rate,
            "n_fft": n_fft,
            "hop_ratio": hop_ratio,
            "window": window,
            "fmin": fmin or None,
            "fmax": fmax or None,
            "n_mels": n_mels,
            "power": power,
            "pcen_enabled": pcen,
        })
        st.success("Saved")

    if st.button("Generate PNGs"):
        files = generate_for_directory(cfg.input_directory, cfg.output_directory, cfg)
        if files:
            st.image(str(files[-1]))

if __name__ == "__main__":
    render()
