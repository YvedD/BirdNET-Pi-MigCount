# Experimental Spectrogram Sandbox (new look)

This sandbox provides a fast, linear-STFT spectrogram workflow for BirdNET-Pi recordings on Raspberry Pi 4B hardware. It is intentionally isolated from the main pipeline and uses only `numpy`, `scipy.signal`, `soundfile`, `matplotlib` (Agg) and `streamlit`.

## Goals
- Offline, high-resolution spectrogram generation for BirdNET-Pi audio clips.
- Adjustable FFT, hop, window, frequency range, dB dynamic range and color map.
- Headless-friendly Streamlit GUI with live preview and PNG export next to the audio file.
- Deterministic output suitable for future integration with BirdNET-Pi detections.

## Run (headless)
```bash
python -m streamlit run experimental/newlook/app.py --server.headless true
```

After launch, open `http://localhost:8501` in your browser, choose a WAV/MP3 clip, tweak parameters on the left, and preview/save the resulting spectrogram on the right.

## Integration notes
- The engine uses pure STFT (no mel) for maximum syllable detail.
- PNGs are stored alongside the source clip when a filesystem path is provided, making it straightforward to reference them from detection outputs or reports.
- Caching is scoped per run to avoid global state while keeping interactions responsive on constrained devices.
