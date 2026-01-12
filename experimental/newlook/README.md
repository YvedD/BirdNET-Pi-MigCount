# Experimental Spectrogram Sandbox (new look)

An isolated Streamlit GUI to compare high-performance spectrogram renderers on Raspberry Pi 4B with HDMI. The sandbox lives entirely in `experimental/newlook/` and shares nothing with production BirdNET-Pi code.

## Architecture
- **Audio loading**: WAV/MP3 via `soundfile`, optional resampling to 24 kHz or 48 kHz.
- **DSP**: Shared linear STFT (no mel), configurable FFT size, hop, window, per-frequency normalization, and dB dynamic range.
- **Renderers** (switchable live):
  - **Matplotlib (reference)**: Full axis control, DPI, colormap; PNG output.
  - **PyQtGraph (fast)**: Qt-backed image pipeline with gamma/contrast control, interpolation toggle, and downsampling for speed.
  - **Datashader + Holoviews (dense)**: Correct aggregation for large matrices, shading modes, and resolution controls for scientific inspection.
- **GUI**: Streamlit split-view with parameters on the left, live preview on the right, and render-time metrics per backend. Switching renderers reuses the cached DSP output.

## Running the sandbox
Use `experimental/newlook/run_experimental.txt` for a copy/paste bootstrap:
1. Create/activate a venv.
2. Upgrade/install the required dependencies (numpy, scipy, soundfile, matplotlib, streamlit, pillow, pyqtgraph, PyQt6, datashader, holoviews).
3. Run `python -m streamlit run experimental/newlook/app.py`.
4. Open `http://localhost:8501` in your browser (HDMI on the Pi).

## Renderer intents
- **Matplotlib**: Reference-quality PNGs with stable color scaling for later comparisons.
- **PyQtGraph**: Lowest-latency preview when tweaking parameters; direct rendering of the spectrogram matrix.
- **Datashader + Holoviews**: Handles very dense matrices with correct aggregation and shading for scientific review.

## Integration ideas
- Generated PNGs can be saved next to each audio file; detection code can point to these assets without coupling to the sandbox.
- The shared DSP layer aligns with BirdNET-Pi detections (linear Hz, no mel), so timestamps and frequency bins match downstream analysis.
- Render-time metrics help select the best backend before integrating visuals into reports or dashboards.
