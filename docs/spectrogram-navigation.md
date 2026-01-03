# Where the spectrogram buttons are loaded

The navigation bar that opens the spectrogram views is defined in `homepage/views.php`:

- The top-nav buttons live in `homepage/views.php` lines 61-75 and submit a `view` parameter (`Spectrogram` or `Vertical Spectrogram`) via a `<form>`.
- The same file routes the request (lines 143-159): when `$_GET['view'] == "Spectrogram"` it includes `spectrogram.php` (the `scripts/spectrogram.php` file referenced without a prefix); when `$_GET['view'] == "Vertical Spectrogram"` it includes `scripts/vertical_spectrogram.php`.
- `spectrogram.php` (in the scripts root) renders the classic horizontal spectrogram with `<img id="spectrogramimage">` and JavaScript that polls `spectrogram.png` and `spectrogram.php?ajax_csv=true`.
- `scripts/vertical_spectrogram.php` builds the vertical variant and loads `../static/vertical-spectrogram.js` (served from `homepage/static/vertical-spectrogram.js`) to draw the canvas and fetch detections.
- `homepage/index.php` embeds `views.php` in an iframe, so clicking the toolbar buttons just reloads that iframe to show the requested spectrogram.
