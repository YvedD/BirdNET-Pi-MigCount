# ESP32/Teensy Bridge - Snel Antwoord

**Vraag:** Kan ik ESP32 of Teensy 4.1 tussen RPi en microfoons zetten als ADC?

**USB:** 4 poorten, 1 voor SSD, 3 beschikbaar.

---

## Direct Antwoord

✅ **JA, dit werkt!** Vooral Teensy 4.1 + I2S ADC is een goede oplossing.

---

## Beste Optie: Teensy 4.1 + I2S ADC ⭐

### Waarom Teensy

**Voordelen:**
- ✅ Je hebt Teensy 4.1 al (scheelt €40-50)
- ✅ Kan USB Audio Device zijn (plug-and-play met BirdNET-Pi!)
- ✅ Excellent Audio Library beschikbaar
- ✅ Krachtige processor (600 MHz ARM Cortex-M7)
- ✅ Slechts 1 USB poort nodig

### Setup

```
4x Primo 9767P microfoons
    ↓
4x Voorversterkers (TL072 op-amp)
    ↓
TLV320AIC3104 (4-channel I2S ADC codec)
    ↓
Teensy 4.1 (I2S interface)
    ↓
USB → Raspberry Pi (als USB audio device)
    ↓
BirdNET-Pi (werkt direct!)
```

### Kosten & Tijd

**Kosten:** €10-25
- TLV320AIC3104 ADC codec: €8-12
- Preamp componenten: €10-15
- PCB/breadboard: €5
- (Teensy heb je al!)

**Tijd:** 35-50 uur
- Proof of concept: 10-15u
- I2S integratie: 15-20u
- 4-channel volledig: 10-15u

**Audio kwaliteit:** Professioneel (>90 dB SNR)

---

## ESP32 Optie (Minder Geschikt)

### Probleem met ESP32

**ESP32 native ADC:**
❌ **Veel te veel ruis voor audio!**
- SNR ~40-50 dB (veel te laag)
- Professioneel audio vereist >90 dB
- WiFi interference maakt het erger

**ESP32 + I2S ADC codec:**
⚠️ **Kan wel, maar complexer**
- Moet I2S codec toevoegen (zelfde als Teensy)
- Programmeren moeilijker dan Teensy
- USB Audio niet native (moet streamen)
- WiFi streaming kan wel (wordt RTSP-achtig)

**Conclusie ESP32:** Alleen met I2S codec, maar dan is Teensy beter.

---

## Snelle Alternatieve Oplossing

### 2x Goedkope USB Audio Cards

**Setup:**
```
2x Primo 9767P → Preamp → Behringer UCA202 (USB 1)
2x Primo 9767P → Preamp → Behringer UCA202 (USB 2)
Beide USB → Raspberry Pi
```

**Kosten:** €50-70
- 2x Behringer UCA202: €50
- Preamp componenten: €10-15

**Tijd:** 10-15 uur (alleen preamps bouwen)

**Voordelen:**
- ✅ Sneller klaar dan custom hardware
- ✅ Professionele kwaliteit (>95 dB SNR)
- ✅ Plug-and-play met BirdNET-Pi
- ✅ Betrouwbaar (geen debugging)

**Nadelen:**
- ⚠️ Gebruikt 2 USB poorten (nog 1 vrij)
- ⚠️ Minder leerzaam project

---

## USB Poorten Strategie

### Met Teensy Oplossing

```
USB 1: SSD (noodzakelijk)
USB 2: Teensy (alle 4 microfoons)
USB 3: Vrij
USB 4: Vrij
```

**Perfect!** Genoeg vrij voor uitbreiding.

### Met 2x USB Cards

```
USB 1: SSD
USB 2: UCA202 #1 (2 mics)
USB 3: UCA202 #2 (2 mics)
USB 4: Vrij
```

**Ook goed!** Nog 1 poort vrij.

### Optioneel: USB Hub

**Powered USB 3.0 hub (€15-30):**
```
USB 1: SSD
USB 2: USB Hub → meerdere devices
USB 3-4: Vrij
```

Meer flexibiliteit, geen belasting op RPi power.

---

## Vergelijking

| Oplossing | Kosten | Tijd | USB Poorten | Kwaliteit | BirdNET-Pi Compatibiliteit |
|-----------|--------|------|-------------|-----------|----------------------------|
| **Teensy + I2S ADC** | €10-25 | 35-50u | 1 | Excellent | ✅ USB Audio Device |
| **2x USB Cards** | €50-70 | 10-15u | 2 | Excellent | ✅ Plug-and-play |
| **1x UMC404HD** | €200-240 | 10-20u | 1 | Professioneel | ✅ Plug-and-play |
| **ESP32 + I2S** | €15-30 | 40-60u | 0 (WiFi) | Goed | ⚠️ Custom streaming |

---

## Mijn Aanbeveling

### Voor Jou: Teensy 4.1 + I2S ADC ⭐

**Redenen:**
1. Je hebt Teensy al (kost niets extra)
2. Professionele audio kwaliteit
3. Leuk en leerzaam project
4. Werkt direct met BirdNET-Pi (USB Audio)
5. Slechts 1 USB poort nodig
6. Je kunt het later uitbreiden/aanpassen

### Als Je Snel Wilt Starten

**2x Behringer UCA202**
- €50, klaar in 15 uur
- Direct werkend
- Minder uitdaging maar betrouwbaar

---

## Implementatie Stappenplan (Teensy)

### Fase 1: Test (10-15 uur)

1. **Bestel componenten** (€10-25)
   - TLV320AIC3104 breakout board
   - TL072 of NE5532 op-amps
   - Weerstanden, condensatoren
   - Breadboard

2. **Bouw 1 preamp**
   - Voor 1 Primo 9767P
   - Test met multimeter

3. **Programmeer Teensy**
   - Arduino IDE: Tools > USB Type > "Audio"
   - Teensy Audio Library gebruiken
   - Test met 1 kanaal

4. **Test met RPi**
   - Sluit Teensy aan via USB
   - Check: `arecord -l` (moet Teensy zien)
   - Opname test: `arecord -D hw:X,0 -d 10 test.wav`

### Fase 2: I2S Integratie (15-20 uur)

1. **Verbind I2S codec met Teensy**
   - SCK, WS, SD pinnen
   - I2C voor configuratie

2. **Test 2 kanalen** (stereo)
   - Bouw 2e preamp
   - Configureer codec
   - Test opname

### Fase 3: 4-Channel (10-15 uur)

1. **Bouw 4 preamps**
   - Op PCB of breadboard
   - Netjes bedraden

2. **Configureer 4 kanalen**
   - Codec setup voor quad
   - Teensy Audio Library aanpassen

3. **Integratie met BirdNET-Pi**
   - Set `REC_CARD` in config
   - Set `CHANNELS=4`
   - Test volledige systeem

---

## Teensy Code Voorbeeld

```cpp
#include <Audio.h>

// I2S Audio input (van codec)
AudioInputI2S            i2s1;
// USB Audio output (naar RPi)
AudioOutputUSB           usb1;

// Verbindingen: 4 kanalen
AudioConnection patchCord1(i2s1, 0, usb1, 0);  // Ch 1
AudioConnection patchCord2(i2s1, 1, usb1, 1);  // Ch 2
// ... meer voor ch 3 & 4

void setup() {
  AudioMemory(12);
  // I2S codec configureren via I2C
  // Sample rate: 48000 Hz
}

void loop() {
  // Audio streaming is automatisch!
}
```

**Upload naar Teensy, USB naar RPi, klaar!**

---

## Conclusie

### Jouw Vraag Beantwoord

**ESP32/Teensy tussen RPi en mics?**
✅ **JA!**

**Welke?**
🏆 **Teensy 4.1 + I2S ADC codec**

**Waarom?**
- Je hebt het al
- Beste audio kwaliteit (met I2S codec)
- USB Audio Device (plug-and-play)
- Leerzaam en flexibel
- 1 USB poort, 2 blijven vrij

### Actie Nu

**Kies:**
1. **Teensy project** → Bestel TLV320AIC3104 + componenten
2. **Snelle oplossing** → Bestel 2x UCA202

Beide werken perfect met BirdNET-Pi!

---

**Zie ESP32_TEENSY_BRIDGE_ANALYSIS.md voor volledige technische details.**
