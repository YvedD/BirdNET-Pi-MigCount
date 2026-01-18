# Frame-Rate Control for Vertical Spectrogram

## Overview
This feature allows users to dynamically adjust the refresh rate (frame-rate) of the vertical spectrogram using a slider in the user interface.

## Key Files and Locations

### 1. `/homepage/static/vertical-spectrogram.js`
This is the **main file** where the frame-rate is controlled.

#### Frame-Rate Configuration Location
- **Line 21**: `REDRAW_INTERVAL_MS: 100,`
  - This configuration variable controls the refresh rate
  - Value in milliseconds (ms)
  - Default: 100ms = 10 frames per second (FPS)

#### New Function: `setRedrawInterval()`
- **Location**: Lines 855-866
- **Purpose**: Dynamically update the frame-rate without reloading the page
- **Parameters**: 
  - `intervalMs`: The new interval in milliseconds (10-1000ms)
- **Validation**:
  - Minimum: 10ms (100 FPS - very fast)
  - Maximum: 1000ms (1 FPS - very slow)
  - Invalid values are ignored with a warning

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

### 2. `/scripts/vertical_spectrogram.php`
This file contains the HTML interface and JavaScript logic for the user interface.

#### UI Control - Frame-Rate Slider
- **Location**: Lines 488-492
- **Section**: "Display Settings" control group
- **HTML Elements**:
  ```html
  <label>Frame-Rate:</label>
  <input type="range" id="framerate-slider" min="10" max="500" value="100" step="10" />
  <span class="value-display" id="framerate-value">100ms</span>
  ```
- **Slider Properties**:
  - Minimum: 10ms (fastest refresh)
  - Maximum: 500ms (slowest refresh)
  - Default: 100ms
  - Step size: 10ms

#### Event Handler
- **Location**: Lines 807-813
- **Function**: `setupControls()` contains the event listener
- **Operation**:
  1. Listens for `input` events on the slider
  2. Updates the displayed value (e.g., "150ms")
  3. Calls `VerticalSpectrogram.setRedrawInterval()`
  4. Saves the setting to localStorage

## How It Works

### Frame-Rate Logic
In `vertical-spectrogram.js`, line 299, the code checks if enough time has passed:

```javascript
if (now - lastRedrawTime >= CONFIG.REDRAW_INTERVAL_MS) {
  renderFrame();
  lastRedrawTime = now;
}
```

- Lower values = more frequent rendering = smoother but higher CPU usage
- Higher values = less frequent rendering = less smooth but more efficient

### Milliseconds to FPS Conversion
- **10ms** = ~100 FPS (frames per second)
- **50ms** = 20 FPS
- **100ms** = 10 FPS (default)
- **200ms** = 5 FPS
- **500ms** = 2 FPS

## Usage

### For Users
1. Open the vertical spectrogram interface
2. Look at the right sidebar "Spectrogram Controls"
3. Find the "Display Settings" section
4. Use the "Frame-Rate" slider to adjust the refresh rate:
   - Slide left for **faster** refresh (lower ms value)
   - Slide right for **slower** refresh (higher ms value)
5. Changes are **immediately visible** without page reload
6. Settings are **automatically saved** in the browser

### For Developers
To set the frame-rate programmatically:

```javascript
// Set fast frame-rate (20 FPS)
VerticalSpectrogram.setRedrawInterval(50);

// Set default frame-rate (10 FPS)
VerticalSpectrogram.setRedrawInterval(100);

// Set slow frame-rate for CPU savings (5 FPS)
VerticalSpectrogram.setRedrawInterval(200);
```

## Recommended Values

| Use Case | Recommended Value | Result |
|----------|------------------|---------|
| Raspberry Pi 3 or older | 150-200ms | Adequate smoothness, low CPU load |
| Raspberry Pi 4 | 100ms (default) | Good balance between smoothness and performance |
| Modern PC | 50ms | Very smooth display |
| Debugging/Analysis | 200-500ms | Slow refresh for detailed observation |
| Demo/Presentation | 50-75ms | Smooth, professional display |

## Summary

The frame-rate control feature provides users with full control over the vertical spectrogram's refresh rate:

1. **Configuration**: `REDRAW_INTERVAL_MS` in `vertical-spectrogram.js` (line 21)
2. **Function**: `setRedrawInterval()` in `vertical-spectrogram.js` (lines 855-866)
3. **UI Control**: Slider in `vertical_spectrogram.php` (lines 488-492)
4. **Event Handler**: In `setupControls()` function (lines 807-813)
5. **Persistence**: Via localStorage (save/load functions)

The implementation is simple, safe, and user-friendly, with immediate feedback and permanent storage of preferences.
