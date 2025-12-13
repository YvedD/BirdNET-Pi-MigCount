# PCM2704 USB Audio Decoder Analyse

**Product:** PCM2704 USB-geluidsdecoder  
**Prijs:** <€10 per stuk  
**Vraag:** Kan dit de Teensy vervangen? Met soldeerwerk stereo → 2x mono voor 4x Primo 9767P?

---

## Direct Antwoord

**PCM2704 voor INPUT (opname):** ❌ **NIET MOGELIJK**  
**PCM2704 voor OUTPUT (playback):** ✅ **Alleen DAC, geen ADC!**  
**Kan Teensy vervangen:** ❌ **NEE - verkeerde richting**

---

## Kritiek Probleem: PCM2704 is een DAC, geen ADC!

### Wat is PCM2704?

**PCM2704 = USB DAC (Digital-to-Analog Converter)**

**Functie:**
- **DAC:** Digitaal → Analoog
- **USB audio playback** (output/afspelen)
- **NIET voor opname** (recording/input)

**Datarichting:**
```
Computer/RPi (USB) → PCM2704 → Analog Audio OUT → Speakers/Headphones
```

**Wat je nodig hebt voor microfoons:**
```
Microphones → Analog Audio IN → ADC → USB → Computer/RPi
```

**PCM2704 gaat de verkeerde kant op!**

### Technische Specificaties PCM2704

**Texas Instruments PCM2704:**
- **Type:** Stereo USB Audio DAC
- **Functie:** USB naar analoog audio uitgang
- **Sample rates:** 32kHz, 44.1kHz, 48kHz
- **Resolutie:** 16-bit
- **Output:** Stereo line-level of headphone
- **Input:** GEEN! Alleen USB digital input

**Gebruik:**
- USB speakers
- USB headphone amplifiers
- USB DAC modules
- **NIET voor microfoon opname!**

---

## Waarom PCM2704 NIET Werkt

### Probleem 1: Verkeerde Richting

**Je wilt:**
- Microfoons → Digitaal (USB) → RPi

**PCM2704 doet:**
- RPi (USB) → Analoog → Speakers

**Het is precies het tegenovergestelde!**

### Probleem 2: Geen ADC Functionaliteit

**PCM2704 heeft:**
- ✅ DAC (Digital-to-Analog)
- ❌ GEEN ADC (Analog-to-Digital)
- ❌ GEEN microphone input
- ❌ GEEN recording capability

**Analogie:**
- Je wilt een camera (opnemen)
- PCM2704 is een beamer (afspelen)
- Een beamer kan geen foto's maken!

### Probleem 3: Geen Input Pinnen

**PCM2704 chip pinout:**
- USB Data pins (D+, D-)
- Analog OUTPUT pins (VOUTL, VOUTR)
- Power pins (VCC, GND)
- **GEEN analog INPUT pins**

Je kunt er fysiek geen microfoons op aansluiten.

---

## Wat Je WEL Nodig Hebt: USB ADC

### Correcte Chip: PCM2900 Serie (ADC)

**PCM2900/PCM2902/PCM2903 = USB Audio CODEC (ADC + DAC)**

**Texas Instruments PCM290x serie:**
- ✅ **ADC:** Analoog IN → Digitaal (voor recording)
- ✅ **DAC:** Digitaal → Analoog OUT (voor playback)
- ✅ **Microphone input** met preamp
- ✅ **USB Audio Class compliant**
- ✅ **Stereo recording** capability

**Prijs:** €3-8 per chip (module €8-15)

### Vergelijking

| Chip | Type | Recording | Playback | Mic Input | Prijs |
|------|------|-----------|----------|-----------|-------|
| **PCM2704** | DAC only | ❌ Nee | ✅ Ja | ❌ Nee | €3-7 |
| **PCM2900** | CODEC | ✅ Ja | ✅ Ja | ✅ Ja | €4-8 |
| **PCM2902** | CODEC | ✅ Ja | ✅ Ja | ✅ Ja | €5-10 |
| **PCM2903** | CODEC | ✅ Ja | ✅ Ja | ✅ Ja | €6-12 |

**Let op model nummer!**
- PCM27xx = DAC (playback only)
- PCM29xx = CODEC (recording + playback)

---

## Oplossing voor Jouw Situatie

### Optie A: PCM2900 Serie Modules (Juiste Chip!)

**Als je goedkope USB audio wilt:**

**Zoek naar:**
- "PCM2902 USB sound card module"
- "PCM2903 USB audio codec module"
- "USB sound card ADC module"

**Kenmerken:**
- Stereo input (2 kanalen)
- USB Audio Class (plug-and-play)
- Prijs: €8-15 per module

**Voor 4 microfoons:**
- 2x PCM2902 modules = €16-30
- Elk module: 2 kanalen (stereo)
- Totaal: 4 kanalen

**Voordelen:**
- ✅ Goedkoop (€16-30 voor 4 kanalen)
- ✅ Plug-and-play USB
- ✅ Geen programmeren
- ✅ Werkt direct met BirdNET-Pi

**Nadelen:**
- ⚠️ Nog steeds preamps nodig voor Primo 9767P
- ⚠️ Gebruikt 2 USB poorten
- ⚠️ Lagere kwaliteit dan professionele interfaces (~80 dB SNR)

### Optie B: PCM2902 + Soldeerwerk

**Custom PCB bouwen:**

**Setup:**
```
4x Primo 9767P → 4x Preamps → 2x PCM2902 (stereo) → USB → RPi
```

**Componenten:**
- 2x PCM2902 chip: €10-16
- Preamp componenten: €15-25
- PCB/breadboard: €10
- USB connectoren: €5

**Totaal:** €40-56 + 30-50 uur werk

**Dit is complexer dan:**
- 2x Behringer UCA202 (€50, plug-and-play)
- Of Teensy + I2S ADC (€10-25, met Teensy die je al hebt)

---

## Waarom Dit Waarschijnlijk NIET de PCM2704 is Die Je Vond

### Veel Voorkomende Verwarring

**Goedkope "USB sound card" modules <€10:**

Deze zijn vaak:
1. **CM108/CM119** chips (C-Media) - CODEC, werkt wel!
2. **PCM2902/PCM2903** modules (verkeerd gelabeld als PCM2704)
3. **SSS1623** of andere goedkope CODEC chips
4. **Noname Chinese chips** die wel ADC hebben

**Hoe te controleren:**
- Kijk naar de chip opdruk (met vergrootglas)
- Check datasheet van verkoper
- Zoek naar "USB sound card RECORDING" in specs
- Test of het microphone input heeft

**Als het <€10 is EN recording capability heeft:**
- Het is NIET PCM2704 (dat is DAC only)
- Het is waarschijnlijk PCM2902, CM108, of andere CODEC
- **Dan kan het wel werken!**

---

## Praktische Test

### Hoe te Verifiëren of Jouw Module Werkt

**Stap 1: Check fysieke aansluitingen**
- Heeft het microphone input? (3.5mm jack of pinnen)
- Of alleen headphone/speaker output?

**Stap 2: Sluit aan op computer**
```bash
# Op Linux/RPi:
arecord -l
```

**Als het recording device toont → Het werkt!**
**Als alleen playback device → Het is DAC only (niet bruikbaar)**

**Stap 3: Test opname**
```bash
arecord -D hw:X,0 -f S16_LE -c2 -r48000 -d 5 test.wav
aplay test.wav
```

Als dit werkt → Module heeft ADC, kan gebruikt worden!

---

## Mijn Aanbeveling

### Scenario 1: Je Module Heeft WEL Recording (is geen PCM2704)

**Als je module ADC heeft (recording):**

✅ **Uitstekend! Gebruik het!**

**Setup voor 4 microfoons:**
- Koop 2x zelfde module
- Bouw 4x preamps voor Primo 9767P
- Sluit 2 mics per module (stereo = 2 kanalen)
- USB naar RPi

**Kosten:** €20-30 (2x modules + preamps)  
**Tijd:** 15-25 uur (preamps bouwen)  
**USB poorten:** 2 (nog 1 vrij)

**Configuratie BirdNET-Pi:**
```bash
# In /etc/birdnet/birdnet.conf
# Voor 2 aparte devices moet je mogelijk software aanpassen
# Of gebruik ALSA multi device
```

### Scenario 2: Je Module is Echt PCM2704 (DAC only)

❌ **Niet bruikbaar voor microfoon opname**

**Alternatieven:**
1. **Zoek PCM2902 modules** (€8-15 elk, 2 stuks nodig)
2. **Of: 2x Behringer UCA202** (€50 totaal, plug-and-play)
3. **Of: Teensy 4.1 + I2S ADC** (€10-25, je hebt Teensy al)

---

## Beste Optie Vergelijking

### Voor 4x Primo 9767P Microfoons

| Oplossing | Kosten | Tijd | USB | Kwaliteit | Plug-and-play | Aanbeveling |
|-----------|--------|------|-----|-----------|---------------|-------------|
| **2x Goedkope USB ADC** | €20-30 | 15-25u | 2 | Redelijk (75-85 dB) | ✅ Ja | ⚠️ Als je soldeerwerk wilt |
| **2x UCA202** | €50 | 10-15u | 2 | Excellent (95+ dB) | ✅ Ja | ✅ **Best plug-and-play** |
| **Teensy + I2S ADC** | €10-25 | 35-50u | 1 | Excellent (90+ dB) | ✅ Ja | ✅ **Best custom/leren** |
| **1x UMC404HD** | €200 | 10-20u | 1 | Pro (100+ dB) | ✅ Ja | ✅ **Best kwaliteit** |
| **2x PCM2902 DIY** | €40-56 | 30-50u | 2 | Goed (80-85 dB) | ⚠️ Custom | ❌ Meer werk dan UCA202 |
| **PCM2704** | N/A | N/A | N/A | N/A | ❌ Nee | ❌ **Werkt niet (DAC)** |

---

## Conclusie & Advies

### Antwoord op Je Vraag

**PCM2704 module <€10:**
- ❌ Als het echt PCM2704 is → NIET bruikbaar (DAC only)
- ✅ Als het verkeerd gelabeld is en WEL ADC heeft → Prima!

**Test het eerst:**
1. Sluit aan op computer
2. Check `arecord -l` (Linux) of Sound Settings (Windows)
3. Als recording device zichtbaar → Gebruik het!
4. Als alleen playback → Zoek andere module

**Kan Teensy vervangen:**
- Als je module ADC heeft: Ja, kan goedkoper alternatief zijn
- Kwaliteit: Lager dan Teensy + I2S ADC
- Complexiteit: Minder dan Teensy programmeren
- Maar: Hogere kwaliteit met Teensy + I2S

### Mijn Sterke Aanbeveling

**Test je <€10 module eerst!**

**Als het recording heeft:**
- Koop 2e module (voor 4 kanalen totaal)
- Bouw preamps
- Test met BirdNET-Pi
- Kosten: €20-30, redelijke kwaliteit

**Als het GEEN recording heeft (echt PCM2704):**

**Beste alternatieven in volgorde:**

1. **2x Behringer UCA202** (€50) ⭐
   - Plug-and-play
   - Excellent kwaliteit
   - 10-15 uur werk (alleen preamps)
   - Meest betrouwbaar

2. **Teensy 4.1 + I2S ADC** (€10-25) ⭐
   - Je hebt Teensy al
   - Excellent kwaliteit
   - Leerzaam project
   - 35-50 uur werk

3. **2x goedkope USB ADC modules** (€16-30)
   - PCM2902 of CM108 gebaseerd
   - Check specs goed!
   - 15-25 uur werk

---

## Technische Details: DAC vs ADC vs CODEC

### Voor Duidelijkheid

**DAC (Digital-to-Analog Converter):**
- Computer → Speakers
- Afspelen/playback
- PCM2704, PCM5102, etc.
- **NIET voor microfoons**

**ADC (Analog-to-Digital Converter):**
- Microfoon → Computer
- Opnemen/recording
- Standalone ADC chips
- **WEL voor microfoons**

**CODEC (Coder-Decoder = ADC + DAC):**
- Beide richtingen
- Recording + Playback
- PCM2902, WM8731, CM108, etc.
- **Ideaal voor audio interfaces**

**BirdNET-Pi heeft alleen ADC nodig** (recording), maar CODEC werkt ook prima.

---

## Volgende Stappen

### Als Je Module ADC Heeft

1. **Verifieer functionaliteit**
   - Test recording op computer/RPi
   - Check sample rate (48kHz capable?)
   - Test audio kwaliteit met test mic

2. **Bestel 2e module** (voor 4 kanalen)

3. **Bouw preamps** voor Primo 9767P
   - 4x simpele op-amp circuits
   - Test elk apart

4. **Integreer met BirdNET-Pi**
   - Configureer beide USB devices
   - Test opname

### Als Je Module DAC Only Is

1. **Zoek juiste modules**
   - PCM2902/PCM2903
   - Of CM108/CM119
   - Of Behringer UCA202 (plug-and-play)

2. **Of ga voor Teensy oplossing**
   - Je hebt het al
   - Hogere kwaliteit mogelijk
   - Leerzaam

---

**End of Analysis**

**TL;DR:** PCM2704 is een **DAC** (afspelen only), GEEN ADC (opnemen). Je hebt **ADC** nodig voor microfoons! Als je module <€10 WEL recording heeft, is het waarschijnlijk verkeerd gelabeld (PCM2902 of CM108) en dan werkt het prima. Test het eerst! Anders: 2x UCA202 (€50, plug-and-play) of Teensy + I2S ADC (€10-25, betere kwaliteit).
