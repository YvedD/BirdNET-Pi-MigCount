"""
Standalone harness to generate experimental spectrograms and WAV segments.

This script:
- loads the JSON config
- processes all WAVs in input_directory
- saves spectrogram PNGs to output_directory
- saves syllable-level WAVs to segment_directory

Useful for batch processing without Streamlit.
"""

from pathlib import Path
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

    print(f"Done. Spectrograms in {cfg.output_directory}, segments in {cfg.segment_directory}")

if __name__ == "__main__":
    main()
