# Spectrogram PNG audit (BirdNET-Pi-MigCount)

Goal: map every place that generates or renders spectrogram PNGs, list the DSP/render parameters being used today, explain why exported images look smeared/low-contrast, and point to the exact code locations to change to get Raven/Chirpity-style output.

## Where spectrogram PNGs come from

1) **Per-detection exports (post-processing)**
- File: `scripts/utils/reporting.py`, function `spectrogram(...)` (lines 49–73).
- Called from `extract_detection(...)` inside `handle_reporting_queue` in `scripts/birdnet_analysis.py` after the model has already produced a detection (so *not* part of inference).
- Steps:
  - `extract_safe(...)` runs `sox ... trim` to cut the detection + context into a new audio file in `EXTRACTED/By_Date/...`.
  - `spectrogram(...)` calls **SoX**:  
    `sox -V1 <clip> -n remix 1 rate 24k spectrogram -t '' -c '' -o <tmp>.png` plus `-r` if `RAW_SPECTROGRAM=1`.  
    Then Pillow draws title/comment text and saves as `<clip>.png` beside the audio.

2) **Live/horizontal viewer PNG (`spectrogram.png`)**
- File: `scripts/spectrogram.sh` (lines ~1–38) run by `spectrogram_viewer.service`.
- Watches `$HOME/BirdSongs/StreamData/analyzing_now.txt` (written by `birdnet_analysis.py` before running inference) and regenerates `${EXTRACTED}/spectrogram.png` with the same SoX command as above (24 kHz mono, default SoX spectrogram).
- Displayed in `scripts/spectrogram.php` via `<img id="spectrogramimage">`, refreshed every `RECORDING_LENGTH` seconds (or drawn via canvas in non-legacy mode).

3) **Vertical live spectrogram (canvas, not PNG-based)**
- Files: `scripts/vertical_spectrogram.php` + `homepage/static/vertical-spectrogram.js`.
- Uses Web Audio API on the live audio element; parameters: `FFT_SIZE=4096`, `smoothingTimeConstant=0.0`, linear frequency axis, `getByteFrequencyData` (0–255 magnitudes), redraw every 100 ms, 1 pixel scroll per frame, no dB compression. Screenshots are optional: canvas → PNG uploaded to `Birdsongs - screenshots` via `save_screenshot` handler in `vertical_spectrogram.php`.

## Current DSP/render parameters (SoX-based PNGs)

- **Resampling / channel:** `remix 1` (mono, left channel), `rate 24k` → Nyquist 12 kHz; high-frequency content above 12 kHz is discarded.
- **FFT / window:** SoX defaults (from `sox --help-effect spectrogram`):
  - Window: Hann by default.
  - Y-size default → one-more-than-power-of-two ≈ 513 rows (DC plus 512 positive-frequency intervals); SoX chooses an FFT length to match that (≈2048-point FFT), so with `sr=24000` the bin spacing is ≈ (24 000 / 2) / 512 ≈ 23.44 Hz.
  - Overlap: SoX uses 4× overlap (~75%) internally; hop ≈ 256 samples → ~10.7 ms time step, window length ~42.7 ms (at 24 kHz).
- **Time axis / resolution:** `-X` default 100 px/s; `-x` default up to 800 px. For a 6 s extract this yields ~600 px wide image; SoX rescales the STFT grid to that width.
- **Amplitude scaling:** dB by default, dynamic range `-z 120 dB`, top `-Z 0 dBFS`, 249 colour quantisation steps.
- **Frequency axis:** Linear (0–12 kHz for 24 kHz audio); no log or mel option in current command.
- **Output size:** Default SoX canvas about 800 px wide × ~550 px tall (including axes); PNG is later rescaled by the browser to fit available width (HTML uses `width:100%`), so the raster is interpolated again on display.
- **Colour map:** SoX default palette (blue/green), no explicit contrast tweaking; optional `-r` removes axes/labels when `RAW_SPECTROGRAM=1`.
- **Post-processing:** Pillow draws two small text overlays (13 px and 11 px fonts) and re-saves the PNG.

## Why the exported PNGs look smeared / low-contrast

- **Linear frequency axis** compresses the higher bands where many short migration calls live; Raven/Chirpity typically show a quasi-log scale that spreads 3–10 kHz more visually.
- **Long-ish analysis window (≈42 ms) vs. short calls (5–20 ms)** spreads transients across several frames; combined with auto-resampling to an ~800 px width, this produces horizontal blur.
- **Only ~600–800 px time axis per clip** (auto `-X`/`-x`) forces SoX to interpolate the STFT grid; any subsequent browser scaling magnifies that blur.
- **Wide dynamic range (120 dB) with the default palette** leaves most energy in mid-tones → low perceived contrast compared to Raven/Chirpity, which usually gate to ~60–80 dB and push the noise floor down.
- **12 kHz ceiling (24 kHz resample)** removes ultrasonic content and halves vertical pixel economy; for high-pitched calls this further bunches structure near the top of the plot.
- **No dB floor / noise clipping** means background noise stays visible, softening edges.

## What to change (precise hooks)

1) **Per-detection PNG generator**  
   - Hook: `scripts/utils/reporting.py::spectrogram` (SoX args).  
   - Suggested Raven/Chirpity-style parameters (example to drop in place of the current defaults):  
     `sox <clip> -n remix 1 rate 48k spectrogram -x 2000 -Y 1025 -X 300 -z 80 -Z -20 -o <tmp>.png`  
     Rationale: 48 kHz keeps up to 24 kHz, requesting `-Y 1025` asks SoX for ~1025 vertical bins (it snaps to power-of-two+1, i.e., ~2048-point FFT internally). With ~3.33 ms column spacing at `-X 300`, the hop is ~160 samples, giving ~92.2% overlap against a ~42.67 ms window. The higher DPI (2000x1025) and tighter 80 dB dynamic range with a lifted floor (-20 dBFS top) improve contrast. If log frequency is required, SoX cannot provide it—see Python path below.

2) **Live `/spectrogram.png` service**  
   - Hook: `scripts/spectrogram.sh` SoX call (same flags as above) to keep live viewer consistent with stored detections.

3) **If you need a true log-frequency Raven-style plot** (SoX lacks this)  
   - Replace the SoX call in `reporting.py::spectrogram` with a small matplotlib/librosa renderer:  
     - Load clip (already mono) at 48 kHz.  
     - `n_fft=2048 or 4096`, `hop_length=256` (87.5% overlap for 2048) or `hop_length=384` ((2048-384)/2048 = 81.25% overlap), `window='hann'`.  
     - `S = librosa.stft(y, n_fft=n_fft, hop_length=hop_length, window='hann')`; `S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max, top_db=80)`.  
     - `librosa.display.specshow(..., y_axis='log', sr=48000, cmap='magma')`, figure size e.g. 8x6 inches at 300 dpi (≈2400x1800 px).  
     - Save PNG directly to `<clip>.png`; keep the title/comment overlay if desired.  
   - The same renderer can be wired into `spectrogram.sh` if a log-frequency live PNG is wanted.

4) **Optional multi-mode switch**  
   - Add a config flag (e.g., `SPECTROGRAM_MODE=linear|raven`) checked in `reporting.py::spectrogram` and `spectrogram.sh` to select between legacy SoX defaults and a high-res/log version.

## Quick reference

- PNG generation is entirely *post-detection*; changing it will not affect the ML inference path (`scripts/utils/analysis.py` only uses librosa for loading audio into the model).
- Main touch-points to adjust:  
  - `scripts/utils/reporting.py::spectrogram` (per-detection PNGs)  
  - `scripts/spectrogram.sh` (live `spectrogram.png`)  
  - Display scaling lives in `scripts/spectrogram.php`/CSS; increasing SoX output resolution reduces reliance on browser scaling.
- Vertical spectrogram (canvas) already supports higher FFT sizes (default 4096, adjustable in `homepage/static/vertical-spectrogram.js`), but it is linear-frequency and uses raw magnitudes; for Raven-like contrast you would need a dB conversion and log-frequency remap there as well.
