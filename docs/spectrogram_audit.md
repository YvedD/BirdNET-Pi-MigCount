## BirdNET-Pi Spectrogram Rendering Audit

### 1) Backend generatie (production detections)
**Bestand/functie:** `scripts/utils/reporting.py::spectrogram`  
**Kernfragment:**
```python
S_base = librosa.feature.melspectrogram(
    y=y, sr=sr, n_fft=n_fft, hop_length=hop_length,
    window="hann", n_mels=1024, fmin=900, fmax=14000, power=1.0,
)
S_pcen = librosa.pcen(S_base + EPSILON, sr=sr, hop_length=hop_length, gain=0.7, bias=9.0, power=1.0)

fig = plt.figure(figsize=TARGET_FIGSIZE, dpi=TARGET_DPI)  # 944x472 px @ 1000 dpi
ax = fig.add_axes([0.09, 0.14, 0.84, 0.76], frame_on=True)
px_line = 72.0 / TARGET_DPI  # ~1px strokes
ax.tick_params(axis="both", labelsize=3, pad=0.8, length=1.2, width=px_line)
ax.xaxis.set_major_locator(mticker.MaxNLocator(8))
ax.yaxis.set_major_locator(mticker.MaxNLocator(8))
img_disp = librosa.display.specshow(
    S_pcen, sr=sr, hop_length=hop_length,
    x_axis="time", y_axis="mel", fmin=900, fmax=14000,
    cmap="plasma", ax=ax, shading="gouraud",
)
ax.set_xlabel("Time (s)", labelpad=1.0)
ax.set_ylabel("Frequency (Hz)", labelpad=1.0)
cbar = fig.colorbar(img_disp, ax=ax, format="%+2.0f")
```
**Gedrag:** PNG wordt 2:1 aspect (944×472). Zeer kleine labels (3–4 pt) en MaxNLocator(8) leveren weinig ticks → beperkte schaal-detail t.o.v. Streamlit.

### 2) Backoffice/batch experimenten
**Bestand/functie:** `experimental/spectrogram_generator.py::generate_spectrogram`  
**Kernfragment:**
```python
fig, ax = plt.subplots(figsize=(cfg.fig_width, cfg.fig_height), dpi=cfg.dpi)
cmap_obj = _resolve_colormap(cfg.colormap)
img = librosa.display.specshow(
    S_db, sr=sr, hop_length=hop_length, x_axis="time", y_axis=y_axis,
    fmin=effective_fmin, fmax=effective_fmax, cmap=cmap_obj,
    vmin=vmin, vmax=vmax, ax=ax, shading="gouraud",
)
ax.set_ylim(bottom=effective_fmin if effective_fmin > 0.0 else None, top=effective_fmax)
ax.set_aspect("auto")
ax.set_title(cfg.title)
ax.set_xlabel("Time (s)")
ax.set_ylabel("Frequency (Hz)")
cbar = fig.colorbar(img, ax=ax, format="%+2.0f dB")
```
**Gedrag:** Aspect/maat afkomstig uit `spectrogram_config.json` (default 10×5 inch @ 300 dpi). Ticks en fonts default matplotlib → meer detail dan reporting.py. Geen PNG-rescaling na generatie.

**Streamlit referentie:** `experimental/controls_panel.py` toont PNG’s via `st.image` zonder geforceerde hoogte/breedte → aspect blijft intact, schaal is proportioneel.

### 3) Frontend weergave (production UI)
**Bestanden:** `scripts/overview.php`, `scripts/spectrogram.php`  
**Kernfragment na laatste wijziging:**
```html
<img id="spectrogramimage"
     style="max-width:944px;width:100%;height:auto;display:block;margin:0 auto;background:#000;"
     src="/spectrogram.png?nocache=...">
```
**Gedrag:** Geen vaste hoogte meer; schaalt proportioneel over de beschikbare breedte met max-width 944 px. Aspect blijft gelijk aan PNG. Legacy canvaspad blijft bestaan voor niet-legacy weergave.

### 4) Waar detail/assen afwijken t.o.v. Streamlit
- Production `reporting.py` forceert extreem kleine fonts (3–4 pt) en MaxNLocator(8) → weinig ticks → “te weinig detail” op x/y.
- Production figuurrand (axes pad) blijft, maar Streamlit-config (generator) gebruikt standaard tick density en groter font → beter leesbaar.
- PNG-aspect is 2:1; Streamlit-config kan andere fig_width/height leveren (10×5 = 2:1, maar met hogere dpi 300 en grotere font defaults).

### 5) Concrete aanpassingsvoorstellen (code-level, geen DSP-wijziging)
Doel: layout/uitzicht gelijk maken aan Streamlit-UI terwijl aspect behouden blijft.

**In `scripts/utils/reporting.py::spectrogram`**
1. Vergroot leesbaarheid van assen (geen DSP impact):
   ```python
   # replace current tick setup
   ax.tick_params(axis="both", labelsize=7, pad=2, length=3, width=px_line)
   ax.xaxis.set_major_locator(mticker.MaxNLocator(12))
   ax.yaxis.set_major_locator(mticker.MaxNLocator(12))
   ax.xaxis.set_minor_locator(mticker.AutoMinorLocator())
   ax.yaxis.set_minor_locator(mticker.AutoMinorLocator())
   ax.xaxis.label.set_fontsize(8)
   ax.yaxis.label.set_fontsize(8)
   cbar.ax.tick_params(labelsize=7, width=px_line, length=3)
   cbar.set_label("PCEN", fontsize=8, labelpad=2)
   ```
   Effect: meer tick-stappen, beter leesbare labels, matching Streamlit-default sizes.

2. Optioneel: harmoniseer figuurmaat naar Streamlit-default (10×5 inch @ 300 dpi) om matching raster te krijgen:
   ```python
   TARGET_PNG_WIDTH = 900  # optional
   TARGET_PNG_HEIGHT = 450
   TARGET_DPI = 300
   TARGET_FIGSIZE = (TARGET_PNG_WIDTH / TARGET_DPI, TARGET_PNG_HEIGHT / TARGET_DPI)
   ```
   Effect: zelfde schaal/dpi-gevoel als experimental config; minder noodzaak tot extreme font verkleining.

3. Vast tick-set voor Y (Hz) binnen 0.9–14 kHz om meer referentiepunten te tonen:
   ```python
   yticks = [1000, 2000, 4000, 6000, 8000, 10000, 12000, 14000]
   ax.set_yticks(yticks)
   ax.set_ylim(900, 14000)
   ```
   Effect: expliciete schaal, meer detail, consistent met referentie.

**In frontend (PHP)**
- Huidige verandering (width:100%; height:auto; max-width:944px) reeds aspect-correct. Geen extra wijziging nodig behalve eventueel `background:#000` behouden of verwijderen voor Streamlit-match (die gebruikt geen zwarte balk).

### 6) Consistentie tussen UI’s
- Streamlit: geen vaste frame; PNG aspect gerespecteerd; ticks/fonts standaard → goed leesbaar.
- Production: met bovenstaande aanpassingen wordt dezelfde tick-density/font-size toegepast; geen container vervorming; raster vergelijkbaar.

### 7) Samenvatting oorzaak-gevolg
- Lage tick-density + 3 pt fonts in `reporting.py` ⇒ assen lijken leeg / weinig detail.
- (Voormalige) vaste 944×611 container ⇒ aspect mismatch; nu opgelost door responsive width/auto height.
- DSP en PNG-resolutie al correct; resterend verschil is styling (ticks/labels/layout).
