# Frame-Rate Instelling voor Verticaal Spectrogram

## Overzicht
Deze functionaliteit stelt gebruikers in staat om de verversingssnelheid (frame-rate) van het verticale spectrogram dynamisch aan te passen via een slider in de gebruikersinterface.

## Belangrijkste Bestanden

### 1. `/homepage/static/vertical-spectrogram.js`
Dit is het **hoofdbestand** waar de frame-rate wordt gecontroleerd.

#### Locatie van Frame-Rate Configuratie
- **Regel 21**: `REDRAW_INTERVAL_MS: 100,`
  - Dit is de configuratievariabele die de verversingssnelheid bepaalt
  - Waarde in milliseconden (ms)
  - Standaardwaarde: 100ms = 10 frames per seconde (FPS)

#### Nieuwe Functie: `setRedrawInterval()`
- **Locatie**: Regels 855-866
- **Doel**: Dynamisch bijwerken van de frame-rate zonder de pagina te herladen
- **Parameters**: 
  - `intervalMs`: Het nieuwe interval in milliseconden (10-1000ms)
- **Validatie**:
  - Minimum: 10ms (100 FPS - zeer snel)
  - Maximum: 1000ms (1 FPS - zeer langzaam)
  - Ongeldige waarden worden genegeerd met een waarschuwing

```javascript
function setRedrawInterval(intervalMs) {
  if (!Number.isFinite(intervalMs) || intervalMs < 10 || intervalMs > 1000) {
    console.warn('Invalid redraw interval value:', intervalMs);
    return;
  }
  CONFIG.REDRAW_INTERVAL_MS = intervalMs;
  console.log('Redraw interval set to:', intervalMs, 'ms');
}
```

#### Public API Update
- **Locatie**: Regels 870-882
- De functie `setRedrawInterval` is toegevoegd aan de publieke API
- Dit maakt het mogelijk om de functie aan te roepen vanaf buiten de module

### 2. `/scripts/vertical_spectrogram.php`
Dit bestand bevat de HTML-interface en JavaScript-logica voor de gebruikersinterface.

#### UI Control - Frame-Rate Slider
- **Locatie**: Regels 488-492
- **Sectie**: "Display Settings" control groep
- **HTML Elementen**:
  ```html
  <label>Frame-Rate:</label>
  <input type="range" id="framerate-slider" min="10" max="500" value="100" step="10" />
  <span class="value-display" id="framerate-value">100ms</span>
  ```
- **Slider Eigenschappen**:
  - Minimum waarde: 10ms (snelste refresh)
  - Maximum waarde: 500ms (langzaamste refresh)
  - Standaard waarde: 100ms
  - Stap grootte: 10ms

#### Event Handler
- **Locatie**: Regels 824-830
- **Functie**: `setupControls()` bevat de event listener
- **Werking**:
  1. Luistert naar `input` events op de slider
  2. Update de weergegeven waarde (bijv. "150ms")
  3. Roept `VerticalSpectrogram.setRedrawInterval()` aan
  4. Slaat de instelling op in localStorage

```javascript
const framerateSlider = document.getElementById('framerate-slider');
const framerateValue = document.getElementById('framerate-value');
framerateSlider.addEventListener('input', function() {
  const value = parseInt(this.value);
  framerateValue.textContent = value + 'ms';
  VerticalSpectrogram.setRedrawInterval(value);
  saveSettings();
});
```

#### Persistence (Opslaan van Instellingen)
- **Save Function** (Regels 677-690):
  - Voegt `redrawInterval` toe aan opgeslagen instellingen
  - Gebruikt localStorage voor permanente opslag
  
```javascript
function saveSettings() {
  const settings = {
    colorScheme: document.getElementById('color-scheme-select')?.value,
    minConfidence: document.getElementById('confidence-slider')?.value,
    lowCutEnabled: document.getElementById('lowcut-checkbox')?.checked,
    lowCutFrequency: document.getElementById('lowcut-slider')?.value,
    labelRotation: labelRotation,
    redrawInterval: document.getElementById('framerate-slider')?.value
  };
  localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
}
```

- **Load Function** (Regels 746-755):
  - Laadt opgeslagen frame-rate instelling bij het opstarten
  - Past de slider en weergave aan
  - Roept `setRedrawInterval()` aan met de opgeslagen waarde

```javascript
if (settings.redrawInterval !== undefined) {
  const framerateSlider = document.getElementById('framerate-slider');
  const framerateValue = document.getElementById('framerate-value');
  if (framerateSlider && framerateValue) {
    framerateSlider.value = settings.redrawInterval;
    framerateValue.textContent = settings.redrawInterval + 'ms';
    VerticalSpectrogram.setRedrawInterval(parseInt(settings.redrawInterval));
  }
}
```

## Hoe Het Werkt

### Frame-Rate Logica
In het bestand `vertical-spectrogram.js`, regel 299, wordt gecontroleerd of er genoeg tijd is verstreken:

```javascript
if (now - lastRedrawTime >= CONFIG.REDRAW_INTERVAL_MS) {
  renderFrame();
  lastRedrawTime = now;
}
```

- Dit zorgt ervoor dat nieuwe frames alleen worden getekend als het interval is verstreken
- Lagere waarden = vaker tekenen = vloeiender maar meer CPU-gebruik
- Hogere waarden = minder vaak tekenen = minder vloeiend maar zuiniger

### Relatie tussen Milliseconden en FPS
- **10ms** = ~100 FPS (frames per seconde)
- **50ms** = 20 FPS
- **100ms** = 10 FPS (standaard)
- **200ms** = 5 FPS
- **500ms** = 2 FPS

## Gebruik

### Voor Gebruikers
1. Open het verticale spectrogram via de interface
2. Kijk naar de rechterzijbalk met "Spectrogram Controls"
3. Vind de sectie "Display Settings"
4. Gebruik de "Frame-Rate" slider om de verversingssnelheid aan te passen:
   - Schuif naar links voor **snellere** refresh (lagere waarde in ms)
   - Schuif naar rechts voor **langzamere** refresh (hogere waarde in ms)
5. De wijziging is **direct zichtbaar** zonder pagina te herladen
6. De instelling wordt **automatisch opgeslagen** in de browser

### Voor Ontwikkelaars
Om de frame-rate programmatisch in te stellen:

```javascript
// Stel een snelle frame-rate in (20 FPS)
VerticalSpectrogram.setRedrawInterval(50);

// Stel de standaard frame-rate in (10 FPS)
VerticalSpectrogram.setRedrawInterval(100);

// Stel een langzame frame-rate in voor CPU-besparing (5 FPS)
VerticalSpectrogram.setRedrawInterval(200);
```

## Voordelen

### Gebruikersvoordelen
- **Flexibiliteit**: Pas de vloeiendheid aan naar persoonlijke voorkeur
- **Prestaties**: Verminder CPU-gebruik op oudere hardware
- **Zichtbaarheid**: Hogere frame-rate voor betere detectie van snelle vogelvlucht
- **Batterijtijd**: Lagere frame-rate bespaart batterij op mobiele apparaten

### Technische Voordelen
- **Geen herlaadpagina nodig**: Wijzigingen zijn direct van kracht
- **Persistent**: Instellingen blijven bewaard tussen sessies
- **Veilig**: Input validatie voorkomt ongeldige waarden
- **Eenvoudig**: Intuïtieve slider interface

## Aanbevolen Waarden

| Gebruik Case | Aanbevolen Waarde | Resultaat |
|--------------|------------------|-----------|
| Raspberry Pi 3 of ouder | 150-200ms | Voldoende vloeiend, lage CPU-belasting |
| Raspberry Pi 4 | 100ms (standaard) | Goede balans tussen vloeiendheid en prestaties |
| Moderne PC | 50ms | Zeer vloeiende weergave |
| Debuggen/Analyse | 200-500ms | Langzame refresh voor gedetailleerde observatie |
| Demo/Presentatie | 50-75ms | Vloeiende, professionele weergave |

## Technische Details

### Veiligheidslimieten
- **Minimum**: 10ms om te voorkomen dat de browser overbelast wordt
- **Maximum**: 1000ms om te voorkomen dat het spectrogram "bevriest"
- **Default**: 100ms voor goede balans tussen prestaties en vloeiendheid

### Browser Compatibiliteit
- Werkt in alle moderne browsers (Chrome, Firefox, Safari, Edge)
- Gebruikt standaard HTML5 range input en JavaScript
- Geen externe dependencies vereist

### Prestatie Impact
De impact op systeemprestaties is direct gerelateerd aan de gekozen waarde:
- **Lage waarde (10-50ms)**: Hogere CPU-gebruik, vloeiender animatie
- **Medium waarde (100-150ms)**: Gebalanceerd, geschikt voor meeste systemen
- **Hoge waarde (200-500ms)**: Laag CPU-gebruik, minder vloeiend

## Veelgestelde Vragen

**Q: Wat is de beste instelling voor mijn systeem?**
A: Begin met 100ms (standaard). Als het spectrogram hapering vertoont, verhoog de waarde. Voor vloeiere weergave, verlaag de waarde.

**Q: Waarom zie ik geen verschil bij hele lage waarden?**
A: Bij waarden onder 50ms kan de browser/hardware de limiet bereiken. Het scherm refresh meestal op 60Hz (16.7ms), dus waarden veel lager dan 17ms hebben weinig extra effect.

**Q: Hoe reset ik naar standaard?**
A: Stel de slider in op 100ms, of wis de browser localStorage voor deze site.

**Q: Beïnvloedt dit de audio kwaliteit?**
A: Nee, alleen de visuele refresh rate wordt beïnvloed. De audio blijft ongewijzigd.

## Samenvatting

De frame-rate controle functie biedt gebruikers volledige controle over de verversingssnelheid van het verticale spectrogram:

1. **Configuratie**: `REDRAW_INTERVAL_MS` in `vertical-spectrogram.js` (regel 21)
2. **Functie**: `setRedrawInterval()` in `vertical-spectrogram.js` (regels 855-866)
3. **UI Control**: Slider in `vertical_spectrogram.php` (regels 488-492)
4. **Event Handler**: In `setupControls()` functie (regels 824-830)
5. **Persistence**: Via localStorage (save/load functions)

De implementatie is eenvoudig, veilig, en gebruiksvriendelijk, met directe feedback en permanente opslag van voorkeuren.
