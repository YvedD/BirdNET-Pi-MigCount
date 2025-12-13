# WM8960 Audio HAT Analyse

**Product:** WM8960 Hi-Fi Audio HAT voor Raspberry Pi  
**Specificaties:** Stereo DAC+ADC, hoofdtelefoonversterker, microfoon, luidsprekeruitgang, I2S-interface, opname  
**Vraag:** Kan ik hier mijn Primo 9767P microfooncapsules op aansluiten?

---

## Direct Antwoord

**WM8960 HAT met Primo 9767P:** ✅ **JA, uitstekende oplossing!**  
**Aanbeveling:** ⭐ **ZEER GESCHIKT** - Dit is één van de beste opties!

---

## WM8960 Audio HAT Specificaties

### Wat is WM8960?

**Wolfson/Cirrus Logic WM8960:**
- **Type:** High-performance stereo CODEC (ADC + DAC)
- **ADC:** 2 kanalen (stereo recording)
- **DAC:** 2 kanalen (stereo playback)
- **Sample rates:** 8kHz tot 48kHz
- **Resolutie:** 24-bit
- **Interface:** I2S naar Raspberry Pi GPIO
- **Microphone inputs:** Differential microphone inputs met ingebouwde preamp
- **SNR:** >98 dB (excellent!)

### HAT Kenmerken

**Raspberry Pi HAT formaat:**
- Past direct op 40-pin GPIO header
- Geen extra kabels nodig
- Compact design
- I2S verbinding met RPi

**Ingebouwde features:**
- ✅ **Microphone preamp** (bias voltage voor electret mics)
- ✅ **Stereo ADC** (2 kanalen opname)
- ✅ **Headphone amplifier**
- ✅ **Speaker output**
- ✅ **Line in/out**

**Prijs:** €15-30 (afhankelijk van merk/verkoper)

---

## Waarom WM8960 Excellent is voor Jouw Gebruik

### Voordelen

**1. Heeft ADC (niet DAC only zoals PCM2704!)**
- ✅ Kan microfoons opnemen
- ✅ Stereo input (2 kanalen)
- ✅ Ingebouwde mic preamp

**2. Ingebouwde Mic Preamp**
- ✅ Primo 9767P kan DIRECT aangesloten worden
- ✅ Bias voltage voor electret capsules
- ✅ Geen externe preamp nodig!
- ✅ Ideaal voor electret condenser mics zoals 9767P

**3. I2S Interface naar GPIO**
- ✅ Gebruikt GPIO pins (je wilde GPIO gebruiken!)
- ✅ Professionele digitale audio kwaliteit
- ✅ Low latency
- ✅ Geen USB poort nodig (SSD + Teensy kunnen beide op USB)

**4. Kernel Support**
- ✅ Linux kernel drivers beschikbaar
- ✅ Werkt met ALSA
- ✅ BirdNET-Pi kan het gebruiken als audio device
- ✅ Veel community support

**5. Audio Kwaliteit**
- ✅ SNR >98 dB (professioneel)
- ✅ 24-bit resolutie
- ✅ Veel beter dan goedkope USB cards
- ✅ Vergelijkbaar met Behringer interfaces

---

## Primo 9767P Aansluiting op WM8960

### Hoe Aan te Sluiten

**WM8960 HAT heeft microphone inputs:**

**Typische pinout op HAT:**
- **MICIN1L/R:** Left/Right microphone input (differential)
- **MICBIAS:** Bias voltage output voor electret mics
- **GND:** Ground

**Voor 2x Primo 9767P (stereo):**

```
Primo 9767P #1 (Left Channel):
  Pin 1 (Signal) → MICIN1L (via DC blocking capacitor 10µF)
  Pin 2 (Ground) → GND
  Bias: MICBIAS → 2.2kΩ resistor → Primo Pin 1

Primo 9767P #2 (Right Channel):
  Pin 1 (Signal) → MICIN1R (via DC blocking capacitor 10µF)
  Pin 2 (Ground) → GND
  Bias: MICBIAS → 2.2kΩ resistor → Primo Pin 1
```

**Let op:** Sommige WM8960 HAT's hebben 3.5mm jack - dan moet je adapter solderen.

### Circuit per Primo 9767P

**Simpel circuit (externe preamp NIET nodig!):**

```
        MICBIAS (2.8V van WM8960)
            |
          [2.2kΩ]
            |
    Primo 9767P Signal pin
            |
          [10µF] (DC blocking capacitor)
            |
        MICIN (WM8960 input)

Primo GND pin → GND
```

**Componenten per kanaal:**
- 1x 2.2kΩ resistor (bias)
- 1x 10µF electrolytic capacitor (DC blocking)
- Primo 9767P capsule

**Totaal voor 2 kanalen:** €2-5 (alleen weerstanden + condensatoren!)

---

## Configuratie voor 4 Microfoons

### Probleem: WM8960 = Stereo (2 kanalen)

**Je hebt 4 microfoons, WM8960 heeft 2 inputs.**

### Oplossingen

**Optie A: 2x WM8960 HAT's** ⚠️ **NIET MOGELIJK**
- RPi kan maar 1 HAT tegelijk hebben (GPIO conflict)
- Fysiek passen ze niet beide op GPIO header

**Optie B: 1x WM8960 + Mixer voor 4 mics** ⚠️ **COMPLEX**
- Passieve of actieve mixer
- Meng 4 mics naar 2 kanalen
- Verlies van ruimtelijke informatie
- Extra componenten

**Optie C: 2x Primo per kanaal (parallel)** ⚠️ **NIET AANBEVOLEN**
- 2 mics aan elk input
- Impedantie problemen
- Mogelijk feedback/ruis

**Optie D: 1x WM8960 + 1x USB card** ✅ **PRAKTISCH**
- WM8960 HAT: 2 Primo's (via GPIO/I2S)
- USB card: 2 Primo's (via USB)
- Gebruikt 1 USB poort + GPIO
- Beide devices in BirdNET-Pi

**Optie E: 2x WM8960 via I2S** ⚠️ **ZEER COMPLEX**
- Beide WM8960's op I2S bus (verschillende I2C addresses)
- Custom device tree overlay
- Complexe kernel configuratie
- Voor experts only

**Optie F: 1x WM8960 voor 2 mics** ✅ **EENVOUDIGST**
- Gebruik alleen 2 Primo 9767P's
- Simpelste oplossing
- Perfecte kwaliteit

---

## Mijn Aanbeveling

### Beste Scenario's

### Scenario 1: WM8960 HAT + 2x Primo 9767P ⭐ **AANBEVOLEN**

**Setup:**
- 1x WM8960 HAT (€15-30)
- 2x Primo 9767P capsules
- 2x 2.2kΩ resistor + 2x 10µF capacitor (€2)
- Totaal: €17-32

**Voordelen:**
- ✅ Excellent audio kwaliteit (>98 dB SNR)
- ✅ Gebruikt GPIO (je wilde dit!)
- ✅ GEEN externe preamp nodig (WM8960 heeft het ingebouwd)
- ✅ Geen USB poort nodig
- ✅ Simpele configuratie
- ✅ Goedkoop
- ✅ Professioneel resultaat

**Tijd:** 5-10 uur (solderen + software setup)

**USB poorten:**
- USB1: SSD
- USB2-4: Vrij! (of Teensy voor andere projecten)

### Scenario 2: WM8960 HAT + USB card voor 4 mics

**Setup:**
- 1x WM8960 HAT (€15-30)
- 1x Behringer UCA202 (€25)
- 4x Primo 9767P
- Componenten (€5)
- Totaal: €45-60

**Voordelen:**
- ✅ Alle 4 microfoons
- ✅ Gebruikt GPIO + 1 USB poort
- ✅ Excellent kwaliteit beide devices
- ✅ Geen externe preamps voor WM8960 kanalen

**Tijd:** 10-15 uur

**USB poorten:**
- USB1: SSD
- USB2: UCA202 (2 mics)
- USB3-4: Vrij

**WM8960:** 2 Primo's (geen preamp nodig)  
**UCA202:** 2 Primo's (simpele preamp nodig)

### Scenario 3: 2x WM8960 alternatief - Dual USB interfaces

**Als je echt 4 mics wilt zonder GPIO:**
- 2x Behringer UCA202 (€50)
- Simpeler software
- Gebruikt 2 USB poorten

---

## Software Configuratie

### WM8960 HAT Linux Setup

**Stap 1: Kernel drivers installeren**

```bash
# Voor RaspiOS/Debian
sudo apt update
sudo apt install -y i2c-tools

# Device tree overlay
# Meestal meegeleverd bij HAT
sudo nano /boot/config.txt

# Toevoegen:
dtoverlay=wm8960-soundcard
```

**Stap 2: Test I2C verbinding**

```bash
sudo i2cdetect -y 1
# Moet WM8960 tonen op address 0x1a
```

**Stap 3: Check ALSA device**

```bash
arecord -l
# Moet iets tonen zoals:
# card 1: wm8960soundcard [wm8960-soundcard], device 0
```

**Stap 4: Test opname**

```bash
arecord -D hw:1,0 -f S16_LE -c2 -r48000 -d 10 test.wav
aplay test.wav
```

**Stap 5: BirdNET-Pi configuratie**

```bash
# In /etc/birdnet/birdnet.conf
REC_CARD="hw:1,0"  # of naam van WM8960 device
CHANNELS=2
```

---

## Vergelijking met Andere Opties

| Oplossing | Kosten | Mics | USB | GPIO | Tijd | Kwaliteit | Preamp nodig |
|-----------|--------|------|-----|------|------|-----------|--------------|
| **WM8960 HAT** | €17-32 | 2 | 0 | ✅ | 5-10u | Excellent | ❌ Nee |
| **WM8960 + UCA202** | €45-60 | 4 | 1 | ✅ | 10-15u | Excellent | ⚠️ 2 mics |
| **2x UCA202** | €50 | 4 | 2 | ❌ | 10-15u | Excellent | ✅ Ja (4x) |
| **Teensy + I2S ADC** | €10-25 | 4 | 1 | ❌ | 35-50u | Excellent | ✅ Ja (4x) |
| **UMC404HD** | €200 | 4 | 1 | ❌ | 10-20u | Pro | ❌ Nee |

**WM8960 HAT wint als:**
- Je 2 mics genoeg vindt
- Je GPIO wilt gebruiken (zoals je wilde!)
- Je GEEN externe preamps wilt bouwen
- Je goedkope maar professionele oplossing wilt
- Je geen USB poort wilt gebruiken

---

## Praktische Implementatie

### Stap-voor-stap

**Week 1: Bestellen & Ontvangen**
1. Bestel WM8960 HAT (€15-30)
   - Waveshare, Seeed Studio, Adafruit hebben versies
   - Let op: sommige hebben al 3.5mm jacks
2. Bestel 2x Primo 9767P (als je ze nog niet hebt)
3. Componenten: 2x 2.2kΩ, 2x 10µF caps

**Week 2: Hardware Assemblage**
1. Monteer WM8960 HAT op RPi GPIO
2. Soldeer Primo's met bias resistors + caps
   - Of gebruik breadboard voor testing
3. Sluit aan op MICIN pinnen HAT

**Week 3: Software Setup**
1. Installeer kernel drivers
2. Configureer device tree
3. Test met arecord
4. Integreer met BirdNET-Pi

**Week 4: Testing & Tuning**
1. Test opname kwaliteit
2. Check gain settings
3. Verify BirdNET-Pi detecties
4. Field test

**Totaal: 5-10 uur actieve werk over 4 weken**

---

## Potentiële Problemen & Oplossingen

### Probleem 1: HAT heeft 3.5mm jack ipv pinnen

**Oplossing:**
- Soldeer Primo's aan 3.5mm plug (TRS connector)
- Of open HAT en soldeer direct op PCB pinnen
- Sommige HAT's hebben header pins EN jack

### Probleem 2: Driver niet automatisch geladen

**Oplossing:**
```bash
# Manual driver load
sudo modprobe snd-soc-wm8960
# Voeg toe aan /etc/modules voor autoload
```

### Probleem 3: Gain te laag/hoog

**Oplossing:**
```bash
# ALSA mixer gebruiken
alsamixer
# Adjust "Mic Volume" en "Capture Volume"
```

### Probleem 4: Device tree conflict

**Oplossing:**
- Check welke overlays actief zijn
- Disable onboard audio: `dtparam=audio=off`
- Gebruik juiste WM8960 overlay voor je HAT model

---

## Conclusie

### Antwoord op Je Vraag

**WM8960 HAT + Primo 9767P:** ✅ **JA, PERFECT!**

**Waarom dit excellent is:**
1. ✅ **Heeft ADC** (kan opnemen, niet DAC only!)
2. ✅ **Ingebouwde mic preamp** (Primo 9767P direct aansluiten)
3. ✅ **Gebruikt GPIO/I2S** (wat je wilde!)
4. ✅ **Geen USB poort nodig** (SSD + andere blijven vrij)
5. ✅ **Professionele kwaliteit** (>98 dB SNR)
6. ✅ **Goedkoop** (€17-32 voor 2 mics)
7. ✅ **Geen complexe preamps bouwen**
8. ✅ **Linux drivers beschikbaar**
9. ✅ **Werkt met BirdNET-Pi**

**Voor 2 microfoons:** ⭐ **DIT IS DE BESTE OPLOSSING!**

**Voor 4 microfoons:**
- Combineer met 1x UCA202 (€25 extra)
- Of gebruik 2e oplossing voor andere 2 mics

### Vergelijking met Eerdere Opties

**WM8960 HAT vs Teensy:**
- **Goedkoper:** €17-32 vs €10-25 (Teensy) + componenten
- **Sneller:** 5-10u vs 35-50u
- **Eenvoudiger:** Geen programmeren
- **Ingebouwde preamp:** Ja vs Nee (moet bouwen)
- **Aantal mics:** 2 vs 4
- **GPIO:** Ja vs USB

**Voor 2 mics:** WM8960 wint!  
**Voor 4 mics:** Combinatie of Teensy

---

## Mijn Sterke Aanbeveling

### Voor Jou: WM8960 HAT ⭐⭐⭐

**Kies WM8960 HAT omdat:**
1. Je wilde GPIO gebruiken (niet USB)
2. Je kunt solderen
3. Je Primo 9767P capsules hebt
4. Je goedkope maar professionele oplossing wilt
5. Je GEEN externe preamps wilt bouwen
6. Je snel werkend systeem wilt (5-10u)

**Setup:**
- €17-32 totaal
- 2x Primo 9767P
- Simpele soldeerwerk
- Excellent kwaliteit
- Plug direct op GPIO
- BirdNET-Pi werkt ermee

**Als je later 4 mics wilt:**
- Voeg 1x UCA202 toe (€25)
- Of 2x goedkope USB cards
- WM8960 blijft voor eerste 2 mics

---

## Volgende Stappen

### Actie Nu

1. **Bestel WM8960 HAT** (€15-30)
   - Waveshare WM8960 Audio HAT
   - Of Seeed Studio/andere merken
   - Check specificaties (2 mic inputs)

2. **Test met je Primo 9767P's**
   - Breadboard eerst
   - Verifieer het werkt

3. **Integreer met BirdNET-Pi**
   - Drivers installeren
   - ALSA configureren
   - Test detecties

4. **Besluit over 4e mic later**
   - Misschien zijn 2 genoeg
   - Zo niet: voeg USB card toe

**Dit is de oplossing die je zocht!**

---

**End of Analysis**

**TL;DR:** ✅ **JA! WM8960 HAT is UITSTEKEND** voor jouw Primo 9767P microfoons! Het heeft ADC (kan opnemen), ingebouwde mic preamp (geen externe preamp nodig!), gebruikt GPIO/I2S (wat je wilde), professionele kwaliteit (>98 dB SNR), goedkoop (€17-32), en werkt met BirdNET-Pi. Voor 2 mics is dit DE BESTE oplossing. Voor 4 mics: combineer met 1 USB card.
