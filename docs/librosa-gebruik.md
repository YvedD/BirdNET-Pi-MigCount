# Librosa-gebruik in BirdNET-Pi-MigCount (NL)

## Waar wordt Librosa gebruikt?
- De enige directe Librosa-aanroep staat in `scripts/utils/analysis.py`. Daar wordt `librosa.load(...)` gebruikt om audiobestanden te openen, te resamplen en mono te maken voordat het model de chunks analyseert.

## Wat biedt Librosa volgens de documentatie?
- Librosa zelf richt zich op feature-extractie en spectrale analyse (STFT/Mel/MFCC) met configureerbare parameters zoals `n_fft`, `hop_length`, `win_length` en raamfuncties.
- Voor high‑pass filtering verwijst de documentatie naar het combineren met SciPy (bijv. een Butterworth-filter) of een pre-emphasis stap vóór de feature-extractie.

## Verbeteringen die nu beschikbaar zijn
1. **High-pass filter vóór de analyse**  
   - Nieuw: optionele instelling `HIGHPASS_HZ` (in `/etc/birdnet/birdnet.conf`).  
   - Werking: een 4e‑orde Butterworth high-pass filter (SciPy) wordt toegepast op het geladen signaal vóór het in chunks wordt gesplitst.  
   - Standaard: uitgeschakeld (waarde `0` of niet ingesteld). Zet bijv. `HIGHPASS_HZ="200"` om wind/laagfrequente brom te dempen.

2. **Gedetailleerdere spectrogrammen**  
   - Live verticaal spectrogram (`homepage/static/vertical-spectrogram.js`): verhoog desgewenst `FFT_SIZE` (standaard 2048) naar 4096 voor fijnere frequentieresolutie en pas `ANALYSER_SMOOTHING` aan voor minder vervaging. Dit kost meer CPU maar toont syllabes duidelijker.  
   - Low-cut in de viewer: zet `LOW_CUT_ENABLED` op `true` en kies een passende `LOW_CUT_FREQUENCY` (bv. 200 Hz) om lage ruis te onderdrukken.  
   - Offline/static spectrogrammen (SoX in `scripts/spectrogram.sh`): verhoog de spectrogram-resolutie door de SoX-parameters te verfijnen (bijv. meer pixels per seconde/FFT-resolutie) als je nog gedetailleerdere beelden wilt genereren.

## Haalbaarheid in BirdNET-Pi-MigCount
- Het high-pass filter is direct geïntegreerd en kan zonder codewijzigingen worden geactiveerd via `HIGHPASS_HZ`.  
- Extra spectrogramdetail is reeds ondersteund via de bestaande verticale viewerconfiguratie; aanpassingen zijn beperkt tot het bijstellen van de configuratiewaarden in het JS-bestand of SoX-parameters indien gewenst.
