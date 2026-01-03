# Waar de spectrogram-knop wordt geladen

Deze repo toont het (verticale) spectrogram via de navigatiebalk in `homepage/views.php`:

- De taakbalkknoppen staan in `homepage/views.php` regels 61‑75. De knoppen sturen een `view`-parameter (`Spectrogram` of `Vertical Spectrogram`) via een `<form>` submit.
- In hetzelfde bestand staat de router (regels 143‑159): bij `$_GET['view'] == "Spectrogram"` wordt `spectrogram.php` ingeladen; bij `$_GET['view'] == "Vertical Spectrogram"` wordt `scripts/vertical_spectrogram.php` ingeladen.
- `scripts/spectrogram.php` rendert het klassieke horizontale spectrogram met `<img id="spectrogramimage">` en JavaScript dat periodiek `spectrogram.png` en `spectrogram.php?ajax_csv=true` ophaalt.
- `scripts/vertical_spectrogram.php` bouwt de verticale variant en laadt `../static/vertical-spectrogram.js` dat het canvas tekent en de data ophaalt.
- `homepage/index.php` laadt `views.php` in een iframe, dus een klik op de taakbalkknoppen ververst enkel die iframe en toont het juiste spectrogram.
