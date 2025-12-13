# GPIO/I2S Microphone Analysis - Primo 9767P Capsules

**Date:** December 13, 2025  
**Question:** Can 2-4 Primo 9767P microphone capsules be connected via the 40-pin GPIO connector on Raspberry Pi 4B 8GB?

---

## Direct Answer

**Technically Possible:** ✅ **YES, but with significant caveats**  
**Recommended:** ⚠️ **NOT RECOMMENDED for BirdNET-Pi without major modifications**

---

## Primo 9767P Microphone Capsule Overview

### Specifications
- **Type:** Electret condenser microphone (ECM)
- **Impedance:** ~2.2kΩ
- **Sensitivity:** ~-46 dB (typical for 9767 series)
- **Operating Voltage:** 1.5-10V DC (requires bias voltage)
- **Output:** Analog signal (NOT digital)
- **Connections:** 2-wire (Signal + Ground) or 3-wire with bias

### Key Characteristics
- **Analog output** - Requires ADC (Analog-to-Digital Converter)
- **Requires bias voltage** - Typically 2-10V through a resistor
- **Low-level signal** - Needs preamplification (~mV range)
- **No phantom power needed** - Uses bias voltage instead

---

## Technical Challenges

### Challenge 1: Raspberry Pi GPIO Has NO Built-in ADC

**Problem:**
- Raspberry Pi 4B GPIO pins are **digital only**
- No analog-to-digital converter on-board
- Primo 9767P outputs analog audio signal
- Cannot directly connect analog mic to digital GPIO

**Solution Required:**
- External ADC (Analog-to-Digital Converter) needed
- Options: I2S ADC, SPI ADC, or USB sound card

### Challenge 2: I2S vs Analog Signal

**Raspberry Pi 40-pin GPIO includes I2S interface:**
- Pin 12 (GPIO 18): I2S PCM_CLK (bit clock)
- Pin 35 (GPIO 19): I2S PCM_FS (frame sync / word select)
- Pin 40 (GPIO 21): I2S PCM_DIN (data in)
- Pin 38 (GPIO 20): I2S PCM_DOUT (data out)

**BUT:**
- I2S is a **digital** serial audio interface
- Primo 9767P outputs **analog** audio
- Cannot connect analog directly to I2S

**Solution:**
- Need I2S ADC codec chip (e.g., TLV320AIC3104, WM8731, CS5343)
- Or use dedicated I2S MEMS microphone modules instead

### Challenge 3: Multiple Microphones Complexity

**For 2-4 Primo 9767P capsules via GPIO:**

**Option A: Single I2S ADC with Analog Multiplexing**
- Use 4-channel ADC codec (e.g., TLV320AIC3204)
- Each Primo capsule → Preamp → ADC channel
- ADC → I2S → Raspberry Pi
- Complex circuit design required

**Option B: Multiple I2S ADCs**
- Raspberry Pi 4B has only ONE I2S interface
- Cannot connect multiple I2S devices easily
- Would need I2S multiplexer or USB hub approach

### Challenge 4: BirdNET-Pi Software Compatibility

**Current BirdNET-Pi Audio Stack:**
```bash
# From birdnet_recording.sh
arecord -f S16_LE -c${CHANNELS} -r48000 -t wav
```

**Expectations:**
- Uses ALSA (Advanced Linux Sound Architecture)
- Expects USB sound card or onboard audio (Pi Zero/3)
- REC_CARD can be set to ALSA device name

**For GPIO/I2S:**
- Requires kernel driver for I2S device
- Device tree overlay configuration
- ALSA device mapping

---

## Feasibility Assessment

### Option 1: Direct GPIO Connection (Analog Capsules)

**What You'd Need:**
1. **I2S ADC Codec Board** (e.g., based on TLV320AIC3104)
   - 4-channel ADC for 4 microphones
   - I2S output to Raspberry Pi
   - ~€30-60

2. **Preamp Circuitry** for each Primo 9767P
   - Bias resistor (2.2kΩ typical)
   - DC blocking capacitor (10µF)
   - Amplifier stage (op-amp like TL072 or on-codec preamp)
   - ~€10-20 in components

3. **Custom PCB or Breadboard**
   - Wire 4x Primo capsules to preamps
   - Preamps to ADC inputs
   - ADC I2S to Pi GPIO
   - Requires soldering/electronics skills

4. **Software Configuration**
   - Device tree overlay for I2S
   - Kernel module compilation (possibly)
   - ALSA configuration
   - Testing and debugging

**Complexity:** ⚠️⚠️⚠️ **VERY HIGH**
- Electronics design required
- PCB fabrication or complex breadboard
- Kernel/driver configuration
- Extensive testing

**Estimated Time:** 40-80 hours (experienced) / Not feasible (beginner)

**Estimated Cost:** €60-120 (components) + time

### Option 2: I2S MEMS Microphones (Alternative)

**Instead of Primo 9767P, use digital I2S MEMS mics:**

**Recommended Products:**
- INMP441 I2S MEMS microphone modules (€3-5 each)
- SPH0645 I2S microphone breakout (Adafruit)
- ICS-43434 I2S MEMS mic

**Advantages:**
- ✅ Direct I2S digital output (no ADC needed)
- ✅ Pre-amplified
- ✅ Low self-noise
- ✅ Easy to wire (5 wires: VCC, GND, SCK, WS, SD)

**BUT:**
- ❌ Raspberry Pi 4B has only ONE I2S bus
- ❌ Cannot connect 2-4 mics to single I2S without multiplexing
- ❌ Still requires software configuration

**Complexity:** ⚠️⚠️ **HIGH** (for multi-mic)

### Option 3: Use Primo 9767P with USB Sound Card

**Much Simpler Approach:**

1. **Get multi-channel USB audio interface**
   - Behringer UCA202/222 (2 channels, €25-35)
   - Behringer U-PHORIA UMC204HD (4 channels, €80-100)
   - Focusrite Scarlett 2i2 (2 channels, €150+)

2. **Build simple preamp for each Primo 9767P**
   - Bias resistor + capacitor + op-amp
   - OR use FET preamp
   - ~€5-10 per channel

3. **Connect:**
   - Primo capsules → Preamps → USB interface line inputs
   - USB interface → Raspberry Pi USB port
   - BirdNET-Pi sees it as standard USB sound card

**Complexity:** ⚠️ **MODERATE**
- Basic electronics (preamp building)
- Plug-and-play USB
- Works with existing BirdNET-Pi code

**Estimated Time:** 10-20 hours
**Estimated Cost:** €50-150 (depending on USB interface)

---

## Recommendation for Your Use Case

### Best Option: USB Sound Card Approach

**Why NOT GPIO/I2S:**
1. ❌ Primo 9767P is analog - needs complex ADC
2. ❌ Raspberry Pi GPIO has no ADC
3. ❌ I2S requires codec chip and custom PCB
4. ❌ Software configuration is complex
5. ❌ BirdNET-Pi not designed for GPIO audio
6. ❌ Very time-consuming (40+ hours)
7. ❌ High failure risk without electronics experience

**Why USB Sound Card:**
1. ✅ Works with existing BirdNET-Pi code
2. ✅ ALSA automatically recognizes device
3. ✅ Simple configuration (set REC_CARD in config)
4. ✅ Proven approach (USB audio is standard)
5. ✅ Can use quality multi-channel interfaces
6. ✅ Much faster implementation (hours vs. days/weeks)
7. ✅ Lower risk of failure

### Recommended Implementation

**For 2-4 Primo 9767P Capsules:**

**Step 1: Choose USB Audio Interface**
- **2 microphones:** Behringer UCA222 (2-channel, €30)
- **4 microphones:** Behringer U-PHORIA UMC404HD (4-channel, €180)
- **Alternative:** 2x stereo USB sound cards (€30 each)

**Step 2: Build Preamps**

Each Primo 9767P needs:
```
Circuit per capsule:
+3.3V ──[2.2kΩ]──┬── Primo 9767P signal pin
                 │
                 ├──[10µF]── [Op-amp buffer] ── To USB interface input
                 │
Primo GND ───────┴── GND
```

**Components per channel:**
- 1x 2.2kΩ resistor (bias)
- 1x 10µF capacitor (DC blocking)
- 1x TL072 op-amp (dual, can do 2 channels)
- 1x 9V battery or USB power
- Total: ~€5-10 per channel

**Step 3: Configure BirdNET-Pi**

```bash
# In /etc/birdnet/birdnet.conf
REC_CARD="hw:1,0"  # Or whatever ALSA device name
CHANNELS=4         # For 4 microphones
```

**Step 4: Test**
```bash
arecord -D hw:1,0 -f S16_LE -c4 -r48000 -d 10 test.wav
aplay test.wav
```

**Total Cost:** €60-220 (depending on interface choice)  
**Time Required:** 10-20 hours (including learning/testing)  
**Complexity:** Moderate (basic electronics)

---

## Alternative: Professional I2S HAT Solution

**If you REALLY want GPIO/I2S:**

**Use Commercial I2S Audio HAT:**
- **ReSpeaker 4-Mic Array** (Seeed Studio, €25-35)
  - 4x MEMS microphones built-in
  - I2S interface
  - Software drivers available
  - Mounts on GPIO

- **IQaudIO Codec Zero** (€15-25)
  - Stereo codec HAT
  - Line input for external mics
  - I2S to GPIO

**Process:**
1. Buy HAT with I2S audio codec
2. Connect Primo capsules to line inputs (with preamps)
3. Install HAT drivers
4. Configure ALSA
5. Update BirdNET-Pi config

**Complexity:** ⚠️⚠️ **HIGH**
- Still needs preamps for Primo capsules
- Driver installation required
- May have compatibility issues
- Limited support/documentation

---

## Technical Deep Dive: Why GPIO Audio Is Hard

### Understanding I2S

**I2S (Inter-IC Sound):**
- Digital serial audio interface
- 3 signals: Clock, Word Select, Data
- Transmits PCM digital audio
- Standard for connecting digital audio chips

**Raspberry Pi I2S on GPIO:**
- Designed for digital audio HATs
- Requires I2S-compatible codec chip
- NOT for direct analog microphones

### What Primo 9767P Actually Needs

**Signal Chain:**
```
Primo 9767P (analog) 
    ↓ (millivolts, analog)
Bias circuit (2.2kΩ resistor)
    ↓ (amplified analog)
Preamplifier (op-amp)
    ↓ (line-level analog)
ADC (Analog-to-Digital Converter)
    ↓ (digital I2S or USB)
Raspberry Pi (digital processing)
```

**Missing Link:**
Without ADC, cannot connect analog to digital Raspberry Pi.

---

## Comparison Table

| Approach | Cost | Time | Complexity | Compatibility | Recommended |
|----------|------|------|------------|---------------|-------------|
| **GPIO/I2S + Custom ADC** | €80-150 | 40-80h | Very High | Low | ❌ No |
| **USB Sound Card** | €60-220 | 10-20h | Moderate | High | ✅ **YES** |
| **I2S HAT (ReSpeaker)** | €50-100 | 20-40h | High | Medium | ⚠️ Maybe |
| **RTSP Streaming (from audit)** | €440-710 | 20-40h | Low-Med | Very High | ✅ **YES** |

---

## My Strong Recommendation

### Best Path Forward: USB Multi-Channel Sound Card

**Why:**
1. ✅ **Works immediately** with BirdNET-Pi (no code changes)
2. ✅ **Professional quality** audio interfaces available
3. ✅ **Easier to implement** than GPIO/I2S
4. ✅ **More reliable** - proven technology
5. ✅ **Better support** - standard ALSA devices
6. ✅ **Expandable** - can add more USB interfaces

**Specific Recommendation:**

**For 4x Primo 9767P Capsules:**
- **Interface:** Behringer U-PHORIA UMC404HD (€180)
  - 4x XLR/TRS combo inputs
  - High-quality preamps built-in
  - 48kHz capable
  - USB 2.0 class-compliant
  - Works with Raspberry Pi 4B

**OR Budget Option:**
- **2x Behringer UCA222** (€30 each = €60)
  - 2 channels each = 4 total
  - Connect both via USB hub
  - Configure as separate ALSA devices

**Preamp Needed:**
- Simple FET buffer or op-amp stage
- Provides bias for Primo capsules
- Amplifies to line level
- ~€5-10 per channel DIY

---

## Conclusion

### Question: Can you connect 2-4 Primo 9767P via 40-pin GPIO?

**Technical Answer:** 
- **Possible:** Yes, theoretically
- **Practical:** No, not recommended
- **Reason:** Requires custom ADC hardware + complex software setup

### What I Recommend Instead:

**Option 1: USB Sound Card (Best)**
- Use 4-channel USB audio interface
- Build simple preamps for Primo capsules
- Connect to USB, configure ALSA
- Works with existing BirdNET-Pi

**Option 2: Keep RTSP Approach (From Original Audit)**
- Use USB microphones on Pi Zero nodes
- RTSP streaming to main Pi
- Already proven and documented

**Option 3: Buy I2S Microphones (Not Primo)**
- If you MUST use GPIO/I2S
- Get INMP441 or similar I2S MEMS mics
- Still complex but simpler than analog

---

## Next Steps If Proceeding with USB Approach

1. **Decide on number of microphones** (2 or 4?)
2. **Select USB audio interface**
   - 4 mics: Behringer UMC404HD
   - 2 mics: Behringer UCA222 or similar
3. **Design/build preamp circuit** for Primo capsules
4. **Test single channel** before scaling to 4
5. **Configure BirdNET-Pi** for multi-channel USB device
6. **Field test** before full deployment

---

## Resources

**USB Audio Interfaces:**
- Behringer UMC Series: https://www.behringer.com/series.html?category=R-BEHRINGER-USBAUDIOSERIES
- Focusrite Scarlett: https://focusrite.com/scarlett

**Microphone Preamp Designs:**
- Simple FET preamp for ECM: Search "electret microphone preamp circuit"
- Op-amp designs: TL072, NE5532 based

**I2S on Raspberry Pi:**
- https://learn.adafruit.com/adafruit-i2s-mems-microphone-breakout
- https://github.com/respeaker/seeed-voicecard

**BirdNET-Pi Audio Setup:**
- See: `scripts/birdnet_recording.sh`
- Config: `/etc/birdnet/birdnet.conf`
- ALSA device selection: `arecord -l` and `arecord -L`

---

**End of Analysis**

**TL;DR:** GPIO/I2S with Primo 9767P is technically possible but practically NOT recommended. Use USB sound card instead - much simpler, more reliable, works with existing BirdNET-Pi code.
