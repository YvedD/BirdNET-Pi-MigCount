# WM8960 Audio HAT - Snel Antwoord (Nederlands)

**Product:** WM8960 Hi-Fi Audio HAT voor Raspberry Pi  
**Vraag:** Kan ik hier mijn Primo 9767P microfooncapsules op aansluiten?

---

## ✅ JA - UITSTEKENDE OPLOSSING! ⭐⭐⭐

**Dit is één van de BESTE opties voor jouw gebruik!**

---

## Waarom WM8960 HAT Perfect Is

### Belangrijkste Voordelen

**1. Heeft ADC (niet DAC only!)**
- ✅ Kan microfoons opnemen
- ✅ Stereo input (2 kanalen)
- ✅ 24-bit, 48kHz, >98 dB SNR

**2. Ingebouwde Mic Preamp** 🎉
- ✅ **Primo 9767P direct aansluiten!**
- ✅ **GEEN externe preamp nodig!**
- ✅ Bias voltage voor electret capsules
- ✅ Scheelt veel soldeerwerk!

**3. Gebruikt GPIO/I2S**
- ✅ Past direct op 40-pin header
- ✅ Geen USB poort nodig
- ✅ Je wilde GPIO gebruiken!

**4. Professionele Kwaliteit**
- ✅ >98 dB SNR (excellent!)
- ✅ Beter dan goedkope USB cards
- ✅ Vergelijkbaar met Behringer

**5. Goedkoop & Simpel**
- ✅ €15-30 voor HAT
- ✅ 5-10 uur implementatie
- ✅ Linux drivers beschikbaar

---

## Primo 9767P Aansluiting

### Wat Je Nodig Hebt

**Per Primo 9767P capsule:**
- 1x 2.2kΩ resistor (bias)
- 1x 10µF capacitor (DC blocking)

**Totaal voor 2 capsules:** €2-5 componenten

### Simpel Circuit

```
WM8960 MICBIAS → [2.2kΩ] → Primo Signal pin
Primo Signal pin → [10µF cap] → WM8960 MICIN
Primo GND → GND
```

**Dat is alles!** Geen complexe op-amp preamp nodig.

---

## Voor 2 vs 4 Microfoons

### 2 Microfoons ⭐ **PERFECT**

**Setup:**
- 1x WM8960 HAT (€15-30)
- 2x Primo 9767P
- Weerstanden + capacitors (€2)
- **Totaal: €17-32**

**Tijd:** 5-10 uur  
**USB poorten:** Allemaal vrij! (SSD op USB, WM8960 op GPIO)  
**Kwaliteit:** Excellent

**DIT IS DE BESTE 2-MIC OPLOSSING!**

### 4 Microfoons

**WM8960 = Stereo (2 kanalen)**

**Oplossing A: WM8960 + USB card**
- WM8960 HAT: 2 Primo's (GPIO)
- Behringer UCA202: 2 Primo's (USB)
- Totaal: €42-55
- Tijd: 10-15 uur
- 1 USB poort gebruikt

**Oplossing B: 2x USB cards** (eenvoudiger)
- 2x UCA202: €50
- Alle 4 via USB
- Tijd: 10-15 uur
- 2 USB poorten gebruikt

---

## Installatie Stappen

### Hardware (5 uur)

1. **Monteer WM8960 HAT op RPi GPIO**
2. **Soldeer componenten:**
   - 2x bias resistor (2.2kΩ)
   - 2x DC blocking cap (10µF)
   - Primo 9767P capsules
3. **Sluit aan op HAT mic inputs**

### Software (2-5 uur)

```bash
# 1. Device tree overlay
sudo nano /boot/config.txt
# Toevoegen: dtoverlay=wm8960-soundcard

# 2. Reboot
sudo reboot

# 3. Test
arecord -l
# Moet WM8960 device tonen

# 4. Test opname
arecord -D hw:1,0 -f S16_LE -c2 -r48000 -d 10 test.wav
aplay test.wav

# 5. BirdNET-Pi config
sudo nano /etc/birdnet/birdnet.conf
# Zet: REC_CARD="hw:1,0"
# Zet: CHANNELS=2
```

---

## Vergelijking Alle Opties

| Oplossing | Kosten | Mics | USB | GPIO | Tijd | Preamp Bouwen |
|-----------|--------|------|-----|------|------|---------------|
| **WM8960 HAT** ⭐ | €17-32 | 2 | 0 | ✅ | 5-10u | ❌ **Nee!** |
| **WM8960 + UCA202** | €42-55 | 4 | 1 | ✅ | 10-15u | ⚠️ 2 mics |
| **2x UCA202** | €50 | 4 | 2 | ❌ | 10-15u | ✅ Ja (4x) |
| **Teensy + I2S** | €10-25 | 4 | 1 | ❌ | 35-50u | ✅ Ja (4x) |

**WM8960 wint voor 2 mics omdat:**
- Goedkoopst
- Snelst
- Gebruikt GPIO (wat je wilde!)
- **GEEN preamp bouwen** (ingebouwd!)
- Professionele kwaliteit

---

## USB Poorten

### Met WM8960 HAT

```
USB 1: SSD
USB 2: Vrij
USB 3: Vrij
USB 4: Vrij

GPIO: WM8960 HAT (2 microfoons)
```

**Alle USB poorten beschikbaar!**

### Als je later 4 mics wilt

```
USB 1: SSD
USB 2: UCA202 (2 extra mics)
USB 3: Vrij
USB 4: Vrij

GPIO: WM8960 HAT (eerste 2 mics)
```

**Nog steeds 2 USB vrij!**

---

## Waarom Dit Beter Is Dan Andere Opties

### vs Teensy

**WM8960 voordelen:**
- ✅ Geen programmeren
- ✅ Ingebouwde preamp (Teensy moet je bouwen)
- ✅ Sneller klaar (5-10u vs 35-50u)
- ✅ Gebruikt GPIO (wat je wilde)

**Teensy voordelen:**
- ✅ 4 kanalen mogelijk
- ✅ Leerzaam project

### vs PCM2704

**WM8960:**
- ✅ Heeft ADC (kan opnemen!)
- ✅ Professionele kwaliteit

**PCM2704:**
- ❌ Alleen DAC (kan NIET opnemen)

### vs 2x USB cards

**WM8960:**
- ✅ Goedkoper (€17-32 vs €50)
- ✅ Gebruikt GPIO (je voorkeur)
- ✅ Geen USB poorten nodig
- ✅ Ingebouwde preamp

**USB cards:**
- ✅ 4 kanalen mogelijk
- ✅ Plug-and-play

---

## Mijn Sterke Aanbeveling

### Voor 2 Microfoons: WM8960 HAT ⭐⭐⭐

**Dit is DE oplossing voor jou!**

**Redenen:**
1. Je wilde GPIO gebruiken → ✅ WM8960 gebruikt GPIO
2. Je kunt solderen → ✅ Simpel soldeerwerk
3. Je hebt Primo 9767P → ✅ Perfect voor WM8960
4. Je wilt goedkoop → ✅ €17-32 totaal
5. Je wilt snel → ✅ 5-10 uur werk
6. **Je wilt GEEN complexe preamps bouwen → ✅ WM8960 heeft preamp ingebouwd!**

### Actie Nu

1. **Bestel WM8960 HAT** (€15-30)
   - Waveshare WM8960 Audio HAT
   - Seeed Studio versie
   - Of andere merk (check reviews)

2. **Componenten** (€2-5)
   - 2x 2.2kΩ resistor
   - 2x 10µF electrolytic capacitor

3. **Test & Implementeer**
   - Volg installatie stappen
   - Test met BirdNET-Pi

### Voor 4 Microfoons

**Start met WM8960 (2 mics)**

**Later als je meer wilt:**
- Voeg 1x UCA202 toe (€25)
- Bouw simpele preamps voor die 2 Primo's
- Totaal 4 mics

**Of:**
- Besluit dat 2 mics genoeg is
- Bespaar geld en tijd

---

## Conclusie

### Je Vraag Beantwoord

**WM8960 HAT + Primo 9767P:** ✅ **JA, PERFECT GESCHIKT!**

**Dit is waarschijnlijk DE BESTE oplossing voor jouw situatie:**
- ✅ Gebruikt GPIO (wat je wilde)
- ✅ Goedkoop (€17-32)
- ✅ Snel (5-10u)
- ✅ Professioneel (>98 dB SNR)
- ✅ **Ingebouwde preamp** (grootste voordeel!)
- ✅ Geen USB poorten nodig
- ✅ Direct compatible met Primo 9767P
- ✅ Werkt met BirdNET-Pi

**Zie WM8960_HAT_ANALYSIS.md voor volledige technische details.**

---

**TL;DR:** ✅ **JA! WM8960 HAT is UITSTEKEND!** Het heeft ADC (kan opnemen), **ingebouwde mic preamp** (Primo 9767P direct aansluiten zonder externe preamp!), gebruikt GPIO/I2S (wat je wilde), professioneel (>98 dB SNR), goedkoop (€17-32), snel (5-10u), geen USB nodig. **Voor 2 mics: DIT IS DE BESTE KEUZE!**
