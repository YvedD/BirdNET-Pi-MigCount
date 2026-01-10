
"""
Standalone harness to generate experimental spectrograms.

This script:
- loads the JSON config
- processes all WAVs in input_directory
- saves spectrogram PNGs to output_directory

Useful for batch processing without Streamlit.
"""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from experimental.spectrogram_generator import CONFIG_PATH, load_config, generate_spectrogram

def main():
    cfg = load_config(CONFIG_PATH)

    # Process each WAV file
    wav_files = list(cfg.input_directory.glob("*.wav"))
    if not wav_files:
        print(f"No WAV files found in {cfg.input_directory}")
        return

    for wav in wav_files:
        print(f"Processing {wav.name}...")
        generate_spectrogram(wav, cfg)

    print(f"Done. Spectrograms in {cfg.output_directory}")

if __name__ == "__main__":
    main()
