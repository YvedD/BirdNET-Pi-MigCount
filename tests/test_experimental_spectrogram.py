from pathlib import Path

from experimental.spectrogram_generator import (
    load_config,
    generate_spectrogram,
)


def test_config_paths_are_isolated():
    config = load_config()
    assert "experimental" in str(config.output_directory)
    assert config.input_directory.is_dir()
    assert config.output_directory.is_absolute()


def test_generate_spectrogram_creates_png(tmp_path):
    config = load_config()
    # keep runtime short for tests while using real test data
    config.max_duration_sec = 1.0
    wav_path = Path(__file__).parent / "testdata" / "Pica pica_30s.wav"
    output = generate_spectrogram(wav_path, config, tmp_path)
    assert output.exists()
    assert output.suffix == ".png"
