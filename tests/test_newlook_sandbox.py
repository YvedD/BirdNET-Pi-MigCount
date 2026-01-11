import numpy as np
import soundfile as sf

from experimental.newlook.audio_loader import load_audio
from experimental.newlook.renderer import render_spectrogram, save_png
from experimental.newlook.spectrogram_engine import compute_spectrogram


def _sine_wave(freq: float, sr: int, duration: float) -> np.ndarray:
    t = np.linspace(0, duration, int(sr * duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t).astype(np.float32)


def test_compute_spectrogram_clamps_to_range():
    sr = 24000
    audio = _sine_wave(1000.0, sr, duration=1.0)
    freqs, times, db = compute_spectrogram(
        audio,
        sample_rate=sr,
        n_fft=2048,
        hop_length=512,
        window="hann",
        fmin=500.0,
        fmax=2000.0,
        per_freq_norm=True,
        db_range=50.0,
    )
    assert freqs[0] >= 500.0
    assert freqs[-1] <= 2000.0
    assert db.shape[0] == len(freqs)
    assert db.max() <= 0.0
    assert db.min() >= -50.1


def test_renderer_outputs_png(tmp_path):
    sr = 24000
    audio = _sine_wave(2000.0, sr, duration=0.5)
    freqs, times, db = compute_spectrogram(
        audio,
        sample_rate=sr,
        n_fft=1024,
        hop_length=256,
        window="hann",
        fmin=0.0,
        fmax=8000.0,
        per_freq_norm=False,
        db_range=60.0,
    )
    png = render_spectrogram(
        freqs,
        times,
        db,
        cmap="magma",
        figsize=(6.0, 3.0),
        dpi=120,
        vmin=-60.0,
        vmax=0.0,
        fmin=0.0,
        fmax=8000.0,
    )
    assert png.startswith(b"\x89PNG\r\n\x1a\n")
    output = tmp_path / "preview.png"
    save_png(png, output)
    assert output.exists()
    assert output.stat().st_size > 0


def test_audio_loader_resamples(tmp_path):
    original_sr = 16000
    audio = _sine_wave(800.0, original_sr, duration=0.25)
    wav_path = tmp_path / "tone.wav"
    sf.write(wav_path, audio, original_sr)
    resampled_audio, sr = load_audio(wav_path, target_sample_rate=24000)
    assert sr == 24000
    assert abs(len(resampled_audio) - int(len(audio) * 24000 / original_sr)) <= 2
