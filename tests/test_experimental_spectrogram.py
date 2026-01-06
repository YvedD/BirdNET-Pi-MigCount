from pathlib import Path
from numbers import Real

import experimental.spectrogram_generator as spectrogram_generator
from experimental.spectrogram_generator import (
    load_config,
    generate_spectrogram,
)
from PIL import Image
import matplotlib.axes


def test_config_paths_are_isolated():
    config = load_config()
    assert "experimental" in str(config.output_directory)
    assert config.input_directory.is_dir()
    assert config.output_directory.is_absolute()
    assert abs(config.hop_length - int(config.n_fft * config.hop_ratio)) <= 1


def test_generate_spectrogram_creates_png(tmp_path):
    config = load_config()
    config.transform = "mel"
    config.hop_ratio = 0.0625
    config.n_fft = 2048
    # keep runtime short for tests while using real test data
    config.max_duration_sec = 1.0
    wav_path = Path(__file__).parent / "testdata" / "Pica pica_30s.wav"
    output = generate_spectrogram(wav_path, config, overlay_segments=False, output_dir=tmp_path)
    assert output.exists()
    assert output.suffix == ".png"


def test_generate_spectrogram_recovers_from_corrupt_png(monkeypatch, tmp_path):
    config = load_config()
    config.max_duration_sec = 0.2
    wav_path = Path(__file__).parent / "testdata" / "Pica pica_30s.wav"

    real_open = Image.open
    open_call_count = 0

    def flaky_open(path, *args, **kwargs):
        nonlocal open_call_count
        # Fail the first verification pass to trigger the retry logic
        if open_call_count == 0:
            open_call_count += 1

            class FakeImage:
                def verify(self):
                    raise SyntaxError("broken PNG file")

                def __enter__(self):
                    return self

                def __exit__(self, exc_type, exc_val, exc_tb):
                    return False

            return FakeImage()
        return real_open(path, *args, **kwargs)

    monkeypatch.setattr(spectrogram_generator.Image, "open", flaky_open)

    output = generate_spectrogram(wav_path, config, overlay_segments=False, output_dir=tmp_path)

    assert open_call_count == 1
    assert output.exists()
    with Image.open(output) as img:
        img.verify()


def test_log_spectrogram_clamps_low_frequency(monkeypatch, tmp_path):
    config = load_config()
    config.transform = "stft"
    config.use_log_frequency = True
    config.fmin = 1000.0
    config.fmax = 8000.0
    config.max_duration_sec = 0.2
    wav_path = Path(__file__).parent / "testdata" / "Pica pica_30s.wav"

    ylim_calls = []
    real_set_ylim = matplotlib.axes.Axes.set_ylim

    def tracking_set_ylim(self, bottom=None, top=None, *args, **kwargs):
        ylim_calls.append((bottom, top))
        return real_set_ylim(self, bottom=bottom, top=top, *args, **kwargs)

    monkeypatch.setattr(matplotlib.axes.Axes, "set_ylim", tracking_set_ylim)

    generate_spectrogram(wav_path, config, overlay_segments=False, output_dir=tmp_path)

    assert any(isinstance(bottom, Real) and bottom >= config.fmin for bottom, _ in ylim_calls)
    assert any(isinstance(top, Real) and top <= config.fmax for _, top in ylim_calls)
