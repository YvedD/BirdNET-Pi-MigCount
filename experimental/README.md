# Experimental Spectrogram Sandbox

This folder is isolated from the BirdNET production pipeline. It only reads
`.wav` files from `tests/testdata` and writes PNG spectrograms into
`experimental/output`. No detection, inference, or scoring code is imported.

## Components

- `spectrogram_config.json` – JSON file containing every tunable DSP/display
  parameter (sample rate, FFT size, hop length, window, log frequency, dynamic
  range, colormap, figure size/DPI, etc.).
- `spectrogram_generator.py` – Python library that renders high-resolution PNGs
  using librosa + matplotlib and the JSON config.
- `generate_spectrograms.py` – CLI harness that processes all `tests/testdata/*.wav`
  files using the current config.
- `controls_panel.py` – Streamlit UI labeled as experimental that edits the JSON
  config and triggers regeneration.

## Usage

```bash
python experimental/generate_spectrograms.py
# or interactive controls
streamlit run experimental/controls_panel.py --server.headless true
```

Generated files land in `experimental/output/`, which is ignored from version
control. Remove this directory to reset the sandbox.
