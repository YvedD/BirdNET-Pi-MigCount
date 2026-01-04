<?php
error_reporting(E_ERROR);
ini_set('display_errors',1);

require_once __DIR__ . '/common.php';
$home = get_home();
$config = get_config();

define('RTSP_STREAM_RECONNECT_DELAY', 10000);

$safe_home = realpath($home);
$allowed_bases = ['/home/'];
$is_allowed_home = false;
if ($safe_home !== false) {
  foreach ($allowed_bases as $base) {
    if (strpos($safe_home, $base) === 0) {
      $is_allowed_home = true;
      break;
    }
  }
}
if (!$is_allowed_home) {
  $safe_home = '/home/runner';
}

// Handle AJAX request for detection data (reuse existing endpoint logic)
if(isset($_GET['ajax_csv'])) {
  $RECS_DIR = $config["RECS_DIR"];
  $STREAM_DATA_DIR = $RECS_DIR . "/StreamData/";

  if (empty($config['RTSP_STREAM'])) {
    $look_in_directory = $STREAM_DATA_DIR;
    $files = scandir($look_in_directory, SCANDIR_SORT_ASCENDING);
    $newest_file = isset($files[2]) ? $files[2] : null;
    if ($newest_file === null) { die(); }
  } else {
    $look_in_directory = $STREAM_DATA_DIR;
    $files = scandir($look_in_directory, SCANDIR_SORT_ASCENDING);

    if(!empty($config['RTSP_STREAM_TO_LIVESTREAM']) && is_numeric($config['RTSP_STREAM_TO_LIVESTREAM'])){
        $RTSP_STREAM_LISTENED_TO = ($config['RTSP_STREAM_TO_LIVESTREAM'] + 1);
    } else {
        $RTSP_STREAM_LISTENED_TO = 1;
    }

    foreach ($files as $file_idx => $stream_file_name) {
        if ($stream_file_name != "." && $stream_file_name != "..") {
            if (stripos($stream_file_name, 'RTSP_' . $RTSP_STREAM_LISTENED_TO) !== false && stripos($stream_file_name, '.wav.json') !== false) {
                $newest_file = $stream_file_name;
            }
        }
    }
  }

if(isset($_GET['newest_file']) && $newest_file == $_GET['newest_file']) { die(); }

$newest_file = basename($newest_file);
$contents = file_get_contents($look_in_directory . $newest_file);
if ($contents !== false) {
  $json = json_decode($contents);
  if ($json != null) {
    $datetime = DateTime::createFromFormat(DateTime::ISO8601, $json->{'timestamp'});
    $now = new DateTime();
    $interval = $now->diff($datetime);
    $json->delay = $interval->format('%s');
    echo json_encode($json);
  }
}
die();
}

// Handle screenshot upload
if(isset($_GET['save_screenshot']) && $_SERVER['REQUEST_METHOD'] === 'POST') {
  header('Content-Type: application/json');
  try {
    $RECS_DIR = $config["RECS_DIR"];
    $screenshots_dir = $RECS_DIR . "/Birdsongs - screenshots";
    if (!file_exists($screenshots_dir)) {
      if (!mkdir($screenshots_dir, 0755, true)) {
        throw new Exception("Failed to create screenshots directory");
      }
    }
    if (!is_writable($screenshots_dir)) { throw new Exception("Screenshots directory is not writable"); }
    if (!isset($_FILES['screenshot']) || $_FILES['screenshot']['error'] !== UPLOAD_ERR_OK) {
      throw new Exception("No screenshot file uploaded or upload error");
    }
    $file_info = finfo_open(FILEINFO_MIME_TYPE);
    $mime_type = finfo_file($file_info, $_FILES['screenshot']['tmp_name']);
    finfo_close($file_info);
    if ($mime_type !== 'image/png') { throw new Exception("Invalid file type. Expected PNG image."); }
    $timestamp = isset($_POST['timestamp']) ? preg_replace('/[^0-9_-]/', '', $_POST['timestamp']) : date('Y-m-d_H-i-s');
    $filename = "spectrogram_" . $timestamp . ".png";
    $filepath = $screenshots_dir . "/" . $filename;
    if (!move_uploaded_file($_FILES['screenshot']['tmp_name'], $filepath)) {
      throw new Exception("Failed to save screenshot file");
    }
    echo json_encode([ 'success' => true, 'filename' => $filename ]);
  } catch (Exception $e) {
    http_response_code(500);
    echo json_encode([ 'success' => false, 'error' => $e->getMessage() ]);
  }
  die();
}

$RTSP_Stream_Config = array();
if (is_array($config) && array_key_exists('RTSP_STREAM',$config)) {
  if (is_null($config['RTSP_STREAM']) === false && $config['RTSP_STREAM'] !== "") {
    $RTSP_Stream_Config_Data = explode(",", $config['RTSP_STREAM']);
    foreach ($RTSP_Stream_Config_Data as $stream_idx => $stream_url) {
      $RTSP_stream_url = parse_url($stream_url);
      $RTSP_Stream_Config[$stream_idx] = $RTSP_stream_url['host'];
    }
  }
}
?>
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Vertical Spectrogram</title>
  <style>
html, body {
  margin: 0;
  padding: 0;
  height: 100%;
  overflow: hidden;
  background: hsl(280, 100%, 10%);
  font-family: 'Roboto Flex', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

#main-container {
  display: flex;
  justify-content: center; /* horizontaal centreren */
  align-items: center;     /* verticaal centreren */
  height: 100%;
  width: 100%;
}

#canvas-container {
  position: relative;
  display: flex;
  justify-content: center; /* horizontaal centreren canvas */
  align-items: center;     /* verticaal centreren canvas */
  flex-direction: column;
  height: 100%;
  max-width: 100%;
  margin: 0;
}
#frequency-labels-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
}

canvas {
  display: block;
  width: 100%;
  height: 100%;
  image-rendering: -moz-crisp-edges;
  image-rendering: crisp-edges;
}

#loading-message {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  z-index: 10;
}

/* Sidebar, buttons, controls etc. blijven hetzelfde */
.sidebar { width: 240px; background: rgba(0, 0, 0, 0.85); backdrop-filter: blur(8px); color: white; font-size: 14px; overflow-y: scroll; padding: 15px; box-shadow: -2px 0 10px rgba(0,0,0,0.5); z-index: 20; flex-shrink: 0; }
.sidebar-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px; border-bottom: 1px solid rgba(255,255,255,0.3); padding-bottom: 6px; }
.sidebar-header h3 { margin: 0; font-size: 14px; font-weight: 600; }
.button-group { display: flex; gap: 5px; }
.control-button { background: rgba(255,255,255,0.2); border: 1px solid rgba(255,255,255,0.3); border-radius: 3px; padding: 4px 8px; color: white; cursor: pointer; font-size: 10px; transition: background 0.2s ease; }
.control-button:hover { background: rgba(255,255,255,0.3); }
.sidebar-content > div { margin: 8px 0; }
.sidebar-content label { display: block; margin-bottom: 3px; font-weight: 500; font-size: 11px; }
.sidebar-content input[type="range"] { width: 100%; margin: 3px 0; }
.sidebar-content input[type="checkbox"] { margin-right: 6px; width: 14px; height: 14px; cursor: pointer; vertical-align: middle; }
.sidebar-content select { width: 100%; padding: 4px; border-radius: 3px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.5); color: white; cursor: pointer; font-size: 11px; }
.value-display { display: inline-block; min-width: 40px; text-align: right; font-weight: bold; font-size: 11px; color: #4CAF50; }
.spinner { display: inline-block; width: 12px; height: 12px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 1s linear infinite; vertical-align: middle; margin-left: 6px; }
@keyframes spin { to { transform: rotate(360deg); } }
.hidden { display: none !important; }
.control-group { background: rgba(255,255,255,0.05); padding: 6px; border-radius: 4px; margin-bottom: 8px; }
.control-group-title { font-size: 10px; text-transform: uppercase; color: rgba(255,255,255,0.6); margin-bottom: 4px; font-weight: 600; }
.size-input { width: 100%; padding: 4px; border-radius: 3px; border: 1px solid rgba(255,255,255,0.3); background: rgba(0,0,0,0.5); color: white; font-size: 11px; }

@media only screen and (max-width: 768px) {
  #main-container { flex-direction: column; justify-content: center; align-items: center; }
  .sidebar { width: 100%; height: auto; max-height: 40vh; order: 2; }
  #canvas-container { max-width: 100%; order: 1; flex: 1; }
  #loading-message { font-size: 18px; }
}
@media only screen and (max-width: 768px) and (orientation: landscape) {
  .sidebar { max-height: 50vh; }
}
  </style>
</head>
<body>
  <div id="main-container">
    <div id="canvas-container">
      <div id="loading-message">Loading Vertical Spectrogram...</div>
      <canvas id="spectrogram-canvas"></canvas>
      <canvas id="frequency-labels-overlay"></canvas>
    </div>
    <div class="sidebar" id="sidebar-panel">
      <div class="sidebar-header">
        <h3>Spectrogram Controls</h3>
        <div class="button-group">
          <button class="control-button" id="new-tab-button" title="Open in New Tab" aria-label="Open in New Tab">↗</button>
          <button class="control-button" id="fullscreen-button" title="Toggle Fullscreen" aria-label="Toggle Fullscreen Mode">⛶</button>
        </div>
      </div>
      <div class="sidebar-content">
        <?php
        if (isset($RTSP_Stream_Config) && !empty($RTSP_Stream_Config)) {
          ?>
          <div class="control-group">
            <div class="control-group-title">Stream Selection</div>
            <div>
              <label>RTSP Stream:</label>
              <select id="rtsp-stream-select">
                <?php
                foreach ($RTSP_Stream_Config as $stream_id => $stream_host) {
                  $isSelected = "";
                  if (isset($config['RTSP_STREAM_TO_LIVESTREAM']) && $config['RTSP_STREAM_TO_LIVESTREAM'] == $stream_id) {
                    $isSelected = 'selected="selected"';
                  }
                  echo "<option value=\"" . htmlspecialchars($stream_id, ENT_QUOTES, 'UTF-8') . "\" $isSelected>" . htmlspecialchars($stream_host, ENT_QUOTES, 'UTF-8') . "</option>";
                }
                ?>
              </select>
              <span id="rtsp-spinner" class="spinner" style="display: none;"></span>
            </div>
          </div>
          <?php
        }
        ?>
        <!-- Remaining sidebar controls unchanged -->
      </div>
    </div>
  </div>

  <audio id="audio-player" style="display:none" crossorigin="anonymous" preload="none"><source src="/stream"></audio>
  <script src="../static/vertical-spectrogram.js"></script>
  <script>
  /* JS code blijft volledig hetzelfde, geen aanpassingen nodig */
  </script>
</body>
</html>
