"""
Standalone harness to generate experimental spectrogram PNGs.

Reads parameters from experimental/spectrogram_config.json, processes WAV files
under tests/testdata, and writes PNGs into experimental/output. No production
BirdNET code paths are touched.
"""

from pathlib import Path

from experimental.spectrogram_generator import CONFIG_PATH, run_harness


def main():
    results = run_harness(CONFIG_PATH)
    output_dir = Path(CONFIG_PATH.parent / "output").resolve()
    print(f"Generated {len(results)} spectrogram(s) into {output_dir}")


if __name__ == "__main__":
    main()
