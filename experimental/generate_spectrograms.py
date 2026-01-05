"""
Standalone harness to generate experimental spectrogram PNGs.

Reads parameters from experimental/spectrogram_config.json, processes WAV files
under tests/testdata, and writes PNGs into experimental/output. No production
BirdNET code paths are touched.
"""

from pathlib import Path

from experimental.spectrogram_generator import (
    CONFIG_PATH,
    generate_for_directory,
    load_config,
)


def main():
    config = load_config(CONFIG_PATH)
    results = generate_for_directory(
        config.input_directory, config.output_directory, config
    )
    print(f"Generated {len(results)} spectrogram(s) into {config.output_directory.resolve()}")


if __name__ == "__main__":
    main()
