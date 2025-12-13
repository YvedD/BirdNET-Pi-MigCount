# BirdNET-Pi-MigCount Codebase Audit

**Date:** December 13, 2025  
**Auditor:** GitHub Copilot  
**Repository:** YvedD/BirdNET-Pi-MigCount (Fork of Nachtzuster/BirdNET-Pi)

---

## Executive Summary

This codebase is a **fork of BirdNET-Pi**, a real-time acoustic bird classification system designed primarily for Raspberry Pi devices. The system uses machine learning models (BirdNET) to identify bird species from audio recordings. This audit assesses the feasibility of using this fork as a foundation for a field deployment system with 2-4 non-phantom-powered microphones.

**Key Finding:** ✅ **YES, this codebase can be used as a starting point** for a field deployment system with multiple microphones, with some considerations and modifications.

---

## 1. System Overview

### 1.1 What is BirdNET-Pi?

BirdNET-Pi is an acoustic monitoring system that:
- **Records audio** continuously from microphones or RTSP streams
- **Analyzes audio** in real-time using TensorFlow Lite machine learning models
- **Identifies bird species** from vocalizations
- **Stores detections** in a SQLite database
- **Provides a web interface** for viewing results, spectrograms, and statistics
- **Integrates with BirdWeather** for data sharing with the community

### 1.2 Architecture

```
┌─────────────────┐
│  Microphone(s)  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Audio Recording        │
│  (arecord/PulseAudio)   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Analysis Engine        │
│  (BirdNET ML Model)     │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  SQLite Database        │
│  Detection Storage      │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Web Interface (Caddy)  │
│  Visualization & Admin  │
└─────────────────────────┘
```

### 1.3 Core Components

1. **Recording Service** (`birdnet_recording.sh`)
   - Uses `arecord` (ALSA) with PulseAudio
   - Records in 15-second segments (configurable)
   - Supports stereo/mono (2-channel default)
   - Format: WAV, PCM_S16_LE, 48kHz

2. **Analysis Service** (`birdnet_analysis.py`)
   - Monitors recording directory with inotify
   - Processes audio chunks through BirdNET ML model
   - Extracts bird detections with confidence scores
   - Supports multiple models (BirdNET v2.4, Perch, BirdNET-Go)

3. **Web Interface** (PHP + Caddy)
   - Real-time spectrogram viewer
   - Detection history and statistics
   - Species charts and reports
   - System administration tools

4. **Database** (SQLite3)
   - Stores all detections with metadata
   - Species information and confidence scores
   - Temporal and spatial data

---

## 2. Hardware Requirements & Compatibility

### 2.1 Supported Platforms

**Official Support:**
- Raspberry Pi 5, 4B, 400 ✅
- Raspberry Pi 3B+ (ARM64-Lite only) ⚠️
- Raspberry Pi 0W2 (ARM64-Lite only) ⚠️
- x86_64 systems (Debian 12/13) ✅

**Operating System:**
- **Recommended:** RaspiOS Trixie (64-bit)
- **Also works:** RaspiOS Bookworm (64-bit)
- **Deprecated:** RaspiOS Bullseye

### 2.2 Storage Requirements

- **Repository size:** ~268 MB
- **ML Models:** 
  - BirdNET_GLOBAL_6K_V2.4_Model_FP16.tflite (~40 MB)
  - Additional metadata models (~15 MB each)
- **Runtime storage:**
  - Audio recordings: ~50-100 MB per hour (depending on format)
  - Database grows over time
  - Automatic disk management available (purge when >95% full)

### 2.3 Processing Performance

- **Pi 5/4:** Real-time analysis capable, can handle multiple streams
- **Pi 3B+:** Real-time possible with optimization
- **Pi 0W2:** May struggle with real-time analysis

---

## 3. Microphone Support Analysis

### 3.1 Current Microphone Configuration

**Default Setup:**
- **CHANNELS:** 2 (stereo)
- **Sample Rate:** 48 kHz
- **Format:** PCM_S16_LE (16-bit signed little-endian)
- **Recording Card:** `default` (PulseAudio)

**Configuration File:** `/etc/birdnet/birdnet.conf`

```bash
REC_CARD=default    # Can be changed to specific ALSA device
CHANNELS=2          # Number of channels
```

### 3.2 Multiple Microphone Scenarios

#### ✅ **Scenario 1: Single USB Microphone (Current Support)**
- **Status:** Fully supported out-of-the-box
- **Setup:** Plug in USB mic, system auto-detects via PulseAudio
- **Best for:** Single monitoring point

#### ⚠️ **Scenario 2: Multiple USB Microphones on One Pi**
- **Status:** Possible with modifications
- **Challenge:** Current implementation records from ONE device
- **Solution Approaches:**
  1. **PulseAudio Multi-Source:** Combine inputs into one virtual device
  2. **Multiple Recording Services:** Run separate instances per microphone
  3. **RTSP Stream Approach:** Use each mic as an RTSP stream source

#### ✅ **Scenario 3: Multiple RTSP Streams**
- **Status:** Already supported!
- **Configuration:** `RTSP_STREAM` in config accepts comma-separated URLs
- **Code:** `birdnet_recording.sh` lines 27-46
- **Best for:** Network-connected microphones or distributed setup

#### ✅ **Scenario 4: Multi-Channel Audio Interface**
- **Status:** Supported via ALSA device selection
- **Example:** 4-channel USB audio interface
- **Setup:** Set `REC_CARD` to specific ALSA device
- **Note:** Analysis processes all channels but treats as mono/stereo

### 3.3 Non-Phantom-Powered Microphones

**Compatibility:** ✅ **Fully Compatible**

The system works with:
- **USB microphones** (self-powered via USB)
- **Line-level inputs** (e.g., from portable recorders)
- **Any ALSA-compatible audio device**

**NOT required:**
- Phantom power (48V)
- External preamps (unless your mics need them)
- Special drivers (standard Linux ALSA)

**Recommended Microphones for Field Use:**
- USB microphones with weatherproof housing
- Low self-noise (< 20 dBA)
- Omnidirectional pattern for bird monitoring
- USB powered (no phantom power needed)

---

## 4. Software Stack Analysis

### 4.1 Core Dependencies

**System Packages:**
- `pulseaudio` - Audio server for flexible routing
- `alsa-utils` - ALSA audio tools (`arecord`)
- `ffmpeg` - Audio/video processing (for RTSP streams)
- `sox` - Audio manipulation (for extractions)
- `sqlite3` - Database
- `caddy` - Web server
- `php-fpm`, `php-sqlite3` - Web interface backend

**Python Dependencies:** (from `requirements.txt`)
```
tensorflow          # BirdNET ML inference
librosa             # Audio processing
numpy, pandas       # Data manipulation
streamlit==1.44.0   # Web dashboard components
plotly, seaborn     # Visualization
apprise==1.9.5      # Multi-platform notifications
paho-mqtt           # MQTT support
soundfile           # Audio I/O
```

### 4.2 Machine Learning Models

**Available Models:**
1. **BirdNET_GLOBAL_6K_V2.4_Model_FP16** (Recommended)
   - 6,000+ species globally
   - FP16 precision (faster on Pi)
   - Supports metadata-based filtering (location, season)

2. **BirdNET-Go_classifier_20250916**
   - Newer experimental model
   
3. **Perch_v2**
   - Alternative model option

4. **BirdNET_6K_GLOBAL_MODEL**
   - Legacy v1 model

**Model Selection:** Configurable via web interface or `MODEL` variable in config

### 4.3 Analysis Pipeline

1. **Audio Segmentation:** 15-second WAV files
2. **Chunk Processing:** 3-second chunks with configurable overlap (0.0-2.9s)
3. **Inference:** TFLite model predicts species probabilities
4. **Filtering:** 
   - Confidence threshold (default: 0.7)
   - Privacy filter (human voice detection)
   - Location/season metadata filtering
5. **Storage:** Detections saved to SQLite with timestamps
6. **Extraction:** Clips of detections extracted for review

---

## 5. Code Quality & Maintainability

### 5.1 Testing Infrastructure

**Test Framework:** pytest
- `tests/test_analysis.py` - Analysis pipeline tests
- `tests/test_apprise_notifications.py` - Notification tests
- Mock-based unit tests with test audio files

**Linting:** Flake8 configured (`.flake8`)
- Max line length: 160
- Max complexity: 15

**CI/CD:** GitHub Actions
- `python-app.yml` - Main test suite
- `python-ci.yml` - Continuous integration

### 5.2 Code Organization

**Strengths:**
- ✅ Modular structure (`scripts/utils/` package)
- ✅ Clear separation of concerns (analysis, database, reporting)
- ✅ Service-based architecture (systemd services)
- ✅ Configurable via central config file

**Areas for Improvement:**
- ⚠️ Mix of Python and Bash scripts
- ⚠️ Some legacy code from original BirdNET-Pi
- ⚠️ Limited documentation in code comments
- ⚠️ PHP web interface (older tech stack)

### 5.3 Recent Improvements (This Fork)

- Backup & Restore functionality
- More responsive web UI
- Support for tmpfs (transient storage)
- Updated TFLite runtime (2.17.1 - faster)
- Daily plot service as daemon (efficiency improvement)
- Bookworm and Trixie support

---

## 6. Licensing & Usage Restrictions

### 6.1 License

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

**Key Points:**
- ❌ **NO COMMERCIAL USE** - Cannot be used to develop commercial products
- ✅ **Attribution required** - Must credit original authors
- ✅ **Share-alike** - Derivative works must use same license
- ✅ **Free for personal, educational, research use**

### 6.2 Implications for Field Deployment

**Allowed:**
- ✅ Personal bird monitoring
- ✅ Research projects
- ✅ Educational purposes
- ✅ Non-profit conservation efforts
- ✅ Community science initiatives

**NOT Allowed:**
- ❌ Selling the system or service
- ❌ Commercial bird monitoring services
- ❌ Integrating into commercial products

---

## 7. Field Deployment Feasibility

### 7.1 Deployment Scenarios

#### **Option A: Single Raspberry Pi with 2-4 USB Microphones**

**Approach:** Multi-source PulseAudio setup

**Pros:**
- Lower cost (one Pi)
- Centralized processing
- Single database

**Cons:**
- USB bandwidth limitations (USB 2.0 on older Pis)
- Cable length restrictions (~5m for USB)
- Single point of failure
- Requires custom PulseAudio configuration

**Feasibility:** ⚠️ **MODERATE** - Requires modifications to recording service

**Required Modifications:**
1. Configure PulseAudio to combine multiple USB inputs
2. Modify `birdnet_recording.sh` to use combined source
3. Test USB bandwidth with 4 simultaneous 48kHz streams
4. May need to reduce sample rate or channels per mic

#### **Option B: Distributed Raspberry Pis (One per Microphone)**

**Approach:** 2-4 Raspberry Pis, each with one microphone

**Pros:**
- No USB bandwidth issues
- Can spread over larger area
- Redundancy (if one fails, others continue)
- Each Pi is independent

**Cons:**
- Higher cost (multiple Pis, SD cards, power supplies)
- Multiple databases to manage
- Network required for centralized viewing

**Feasibility:** ✅ **HIGH** - Works with current code

**Setup:**
1. Install BirdNET-Pi on each device
2. Configure unique hostnames
3. Optionally: Set up central aggregation server
4. Power: USB power banks for field portability

#### **Option C: Hybrid - One Pi with RTSP Network Microphones**

**Approach:** Network audio devices streaming to one Pi

**Pros:**
- Flexible microphone placement
- Centralized processing
- Already supported by code!

**Cons:**
- Requires network infrastructure
- RTSP-capable microphones or converters needed
- Network bandwidth considerations

**Feasibility:** ✅ **HIGH** - Supported out-of-the-box

**Configuration:**
```bash
RTSP_STREAM="rtsp://mic1-ip/stream,rtsp://mic2-ip/stream,rtsp://mic3-ip/stream,rtsp://mic4-ip/stream"
```

### 7.2 Power Considerations for Field Use

**Raspberry Pi Power:**
- Pi 4B: ~3W idle, ~6W under load
- Pi 5: ~4W idle, ~12W under load
- Pi 3B+: ~2.5W idle, ~5W under load

**Field Power Options:**
1. **USB Power Banks:** 20,000mAh = ~24-48 hours for Pi 4B
2. **Solar + Battery:** Sustainable for long-term deployment
3. **PoE (Power over Ethernet):** If network available (requires PoE HAT)

**Microphones:**
- USB microphones: Powered via USB (~0.5-1W each)
- Total for 4 mics: ~2-4W additional

**Example Field Setup:**
- 1x Raspberry Pi 4B: 6W
- 4x USB microphones: 4W
- **Total: ~10W**
- **20,000mAh power bank:** ~15-20 hours runtime

### 7.3 Environmental Considerations

**Weatherproofing:**
- System is NOT waterproof by default
- Requires weatherproof enclosure
- Microphones need outdoor-rated housing or windscreens
- Consider desiccant packs for humidity

**Temperature:**
- Raspberry Pi operating range: 0°C to 50°C
- May throttle in high temperatures
- Heatsinks recommended for enclosed spaces

**Wildlife:**
- Secure cabling (animals may chew)
- Elevated mounting to prevent tampering
- Camouflage if in public areas

---

## 8. Multi-Microphone Implementation Guide

### 8.1 Recommended Approach for 2-4 Microphones

**Best Option:** **Option C (RTSP Hybrid)** or **Option B (Distributed Pis)**

#### If Using RTSP (Recommended for Flexibility):

**Step 1:** Set up audio streaming devices
- Use Raspberry Pi Zeros with microphones as RTSP servers
- Or use IP audio devices with RTSP output
- Software: Use `ffmpeg` to create RTSP streams

**Example RTSP Server Setup (Pi Zero with Mic):**
```bash
# On each microphone Pi
ffmpeg -f alsa -i hw:0 -acodec libmp3lame -ab 192k -ac 2 -f rtsp rtsp://0.0.0.0:8554/stream
```

**Step 2:** Configure main Pi
```bash
# In /etc/birdnet/birdnet.conf
RTSP_STREAM="rtsp://192.168.1.10:8554/stream,rtsp://192.168.1.11:8554/stream,rtsp://192.168.1.12:8554/stream"
```

**Step 3:** The system automatically handles multiple streams
- Code in `birdnet_recording.sh` loops over streams
- Creates separate WAV files with stream IDs
- Analysis processes all files

#### If Using Multiple USB Mics on One Pi:

**Requires Code Modification:**

1. **Create virtual PulseAudio device:**
```bash
# Load module-combine-sink to merge inputs
pactl load-module module-combine-sink
```

2. **Modify `birdnet_recording.sh`:**
```bash
# Change line 54 to use combined source
REC_CARD="combined-source"
```

3. **Test configuration:**
```bash
arecord -D combined-source -f S16_LE -c8 -r48000 -d 10 test.wav
```

**Note:** This approach is more complex and may require troubleshooting.

### 8.2 Field Deployment Checklist

**Hardware:**
- [ ] Raspberry Pi 4B or 5 (recommended)
- [ ] MicroSD card (32GB+ Class 10)
- [ ] USB microphones (2-4, weatherproof if possible)
- [ ] Power supply (USB-C for Pi 4/5, MicroUSB for 3B+)
- [ ] Power bank or solar setup for extended field use
- [ ] Weatherproof enclosure
- [ ] USB cables (quality cables, max 5m)
- [ ] Network cables (if using Ethernet for RTSP)

**Software Setup:**
- [ ] Install RaspiOS Trixie 64-bit Lite
- [ ] Run installer: `curl -s https://raw.githubusercontent.com/YvedD/BirdNET-Pi-MigCount/main/newinstaller.sh | bash`
- [ ] Configure location (latitude/longitude)
- [ ] Set up RTSP streams or USB mic configuration
- [ ] Test recording with `arecord -l` and `arecord -D [device] -d 10 test.wav`
- [ ] Verify analysis is running: `sudo systemctl status birdnet_analysis`
- [ ] Access web interface to confirm detections

**Field Testing:**
- [ ] Test power consumption and battery life
- [ ] Verify audio quality at deployment location
- [ ] Check network connectivity (if using RTSP)
- [ ] Monitor for first 24 hours to ensure stability
- [ ] Set up disk management (auto-purge old recordings)

---

## 9. Advantages & Limitations

### 9.1 Advantages

**For This Codebase:**
- ✅ **Mature, tested system** with active community
- ✅ **Well-documented** (wiki, discussions)
- ✅ **Actively maintained** fork with improvements
- ✅ **Out-of-box functionality** for basic use
- ✅ **RTSP support** enables flexible microphone placement
- ✅ **Automatic disk management** for long-term deployments
- ✅ **Backup/restore** for data migration
- ✅ **BirdWeather integration** for data sharing
- ✅ **Multi-language support** for species names
- ✅ **Notification system** (90+ platforms via Apprise)

**For Field Deployment:**
- ✅ **Low power consumption** (suitable for battery/solar)
- ✅ **Proven hardware** (Raspberry Pi)
- ✅ **Offline capable** (no internet required for operation)
- ✅ **Open source** (can be modified for specific needs)

### 9.2 Limitations

**System Limitations:**
- ⚠️ **Single microphone default** - Multi-mic requires configuration
- ⚠️ **No built-in waterproofing** - Enclosure needed
- ⚠️ **Limited to 48kHz sample rate** - Some birds vocalize higher
- ⚠️ **Processing power dependent** - Real-time analysis needs adequate Pi
- ⚠️ **Storage management required** - Long deployments fill disk
- ⚠️ **No built-in remote management** - Manual access needed for updates

**Licensing Limitations:**
- ❌ **Non-commercial only** - Cannot sell or commercialize
- ⚠️ **Share-alike requirement** - Modifications must be open-sourced

**Technical Debt:**
- ⚠️ **Mixed tech stack** - Python, Bash, PHP
- ⚠️ **Legacy components** - Some inherited code
- ⚠️ **Limited multi-mic support** - Needs customization

---

## 10. Recommendations

### 10.1 For Your Use Case (2-4 Microphones in Field)

**Primary Recommendation:**
**Use Option C: Distributed Raspberry Pis with RTSP streaming**

**Why:**
1. ✅ Works with current code (no modifications needed)
2. ✅ Maximum flexibility in microphone placement
3. ✅ Each microphone can be 10s-100s of meters apart
4. ✅ Redundancy if one device fails
5. ✅ Can use cheaper Pi Zero 2W for microphone nodes

**Setup:**
- **Main Unit:** Raspberry Pi 4B (analysis + web interface)
- **Mic Nodes:** 2-4x Raspberry Pi Zero 2W with USB mics
- **Power:** USB power banks or solar for each node
- **Network:** WiFi mesh or hardwired Ethernet

**Alternative (Budget-Friendly):**
**Option B: Separate Raspberry Pis, No RTSP**
- Each Pi runs full BirdNET-Pi stack
- View data on each individually
- Lower complexity, higher hardware cost

### 10.2 Specific Action Items

**Before Deployment:**
1. **Test with one microphone** - Verify system works in your environment
2. **Determine placement** - Where will microphones be located?
3. **Choose power strategy** - Battery runtime vs. solar vs. mains power
4. **Select enclosures** - IP65+ rated for outdoor use
5. **Network planning** - WiFi range or cable runs for RTSP

**Code Modifications (if needed):**
1. **Fork this repository** - Make your own version for tracking changes
2. **Document your setup** - Note configuration for future reference
3. **Consider contributing back** - Share improvements with community (license requires)

**Testing Phase:**
1. **Lab testing** - Set up system indoors with all microphones
2. **24-hour burn-in** - Verify stability
3. **Field trial** - 1 week deployment with daily checks
4. **Adjust parameters** - Confidence threshold, recording length, etc.

### 10.3 Future Enhancements to Consider

**For Multi-Microphone Support:**
- Implement true multi-channel analysis (spatial audio)
- Add microphone ID to detection records
- Create visualization showing which mic detected which species
- Implement sound source localization (triangulation)

**For Field Robustness:**
- Add cellular connectivity for remote monitoring
- Implement automated health checks and alerts
- Create backup analysis mode if primary Pi fails
- Add environmental sensors (temperature, humidity)

---

## 11. Conclusion

### 11.1 Summary

**Question:** Can this fork be used as a starting point for a field system with 2-4 non-phantom-powered microphones?

**Answer:** ✅ **YES, absolutely.**

This codebase is a solid foundation for your use case. The system is:
- **Mature and tested** in real-world deployments
- **Flexible enough** to support multiple microphones via RTSP or distributed setup
- **Well-suited for field use** with appropriate power and weatherproofing
- **Non-commercial license compatible** with research/conservation projects

**Key Success Factors:**
1. Use RTSP streaming approach for easiest multi-mic support
2. Ensure adequate power supply for extended field use
3. Properly weatherproof all components
4. Test thoroughly before final deployment
5. Plan for data retrieval and backup

### 11.2 Risk Assessment

**Low Risk:**
- Single microphone deployment
- Short-term monitoring (days to weeks)
- Nearby access for maintenance

**Medium Risk:**
- 2-4 microphone distributed system
- Month-long deployments
- Remote locations with weekly access

**High Risk (requires expertise):**
- Custom multi-channel single-device setup
- Long-term unattended deployments (months)
- Extreme weather conditions
- Fully off-grid solar power

### 11.3 Next Steps

1. **Decision:** Choose deployment architecture (Option B or C)
2. **Prototype:** Build single-mic system first
3. **Test:** Verify in your target environment
4. **Scale:** Add additional microphones
5. **Deploy:** Implement full field setup
6. **Monitor:** Regular checks and maintenance
7. **Iterate:** Improve based on experience

---

## Appendix A: Useful Commands

**Check audio devices:**
```bash
arecord -l                    # List recording devices
aplay -L                      # List playback devices
pactl list sources short      # PulseAudio sources
```

**Test recording:**
```bash
arecord -D hw:0 -f S16_LE -c2 -r48000 -d 10 test.wav
aplay test.wav
```

**Monitor services:**
```bash
sudo systemctl status birdnet_recording
sudo systemctl status birdnet_analysis
journalctl -fu birdnet_analysis
```

**Check disk usage:**
```bash
df -h
du -sh ~/BirdSongs/*
```

**Database queries:**
```bash
sqlite3 ~/BirdNET-Pi/scripts/birds.db
.tables
SELECT * FROM detections LIMIT 10;
```

---

## Appendix B: Resources

**Official Documentation:**
- BirdNET-Pi Wiki: https://github.com/mcguirepr89/BirdNET-Pi/wiki
- Original BirdNET: https://github.com/kahst/BirdNET-Analyzer
- This Fork: https://github.com/Nachtzuster/BirdNET-Pi

**Community:**
- GitHub Discussions: https://github.com/mcguirepr89/BirdNET-Pi/discussions
- BirdWeather Platform: https://app.birdweather.com

**Hardware Guides:**
- Microphone recommendations: https://github.com/mcguirepr89/BirdNET-Pi/discussions/39
- DIY microphone build: https://github.com/DD4WH/SASS/wiki

**Alternative Software:**
- BirdNET Analyzer (Python version): https://github.com/kahst/BirdNET-Analyzer
- BirdNET-Go (newer, faster): https://github.com/tphakala/birdnet-go

---

**End of Audit**
