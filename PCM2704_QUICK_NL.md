# PCM2704 - Snel Antwoord (Nederlands)

**Product:** PCM2704 USB-geluidsdecoder (<€10)  
**Vraag:** Kan dit Teensy vervangen voor 4x Primo 9767P microfoons?

---

## ❌ KRITIEK PROBLEEM: PCM2704 is een DAC, GEEN ADC!

### Direct Antwoord

**PCM2704 voor microfoon opname:** ❌ **WERKT NIET**  
**Reden:** Verkeerde richting - het is voor AFSPELEN, niet OPNEMEN

---

## Het Probleem

### PCM2704 = DAC (Digital-to-Analog)

**Wat het doet:**
```
Computer (USB) → PCM2704 → Analoge audio → Speakers/Koptelefoon
```

**Wat je nodig hebt:**
```
Microfoons → Analoge audio → ADC → USB → Computer
```

**PCM2704 gaat de verkeerde kant op!**

### Analogie

- Je wilt een **camera** (opnemen)
- PCM2704 is een **beamer** (afspelen)
- Een beamer kan geen foto's maken!

---

## Waarom Het NIET Werkt

**PCM2704 specificaties:**
- ✅ DAC: Digitaal → Analoog (afspelen)
- ❌ GEEN ADC: Analoog → Digitaal (opnemen)
- ❌ GEEN microphone input
- ❌ GEEN recording capability

**Fysiek:**
- Heeft alleen OUTPUT pinnen (naar speakers)
- Heeft GEEN INPUT pinnen (voor microfoons)
- Kan er geen microfoon op aansluiten

---

## Wat Je WEL Nodig Hebt

### Juiste Chip: PCM2900 Serie (CODEC)

**PCM2902/PCM2903 = ADC + DAC (beide richtingen)**

| Chip | Type | Opnemen | Afspelen | Mic Input | Prijs |
|------|------|---------|----------|-----------|-------|
| **PCM2704** | DAC | ❌ Nee | ✅ Ja | ❌ Nee | €3-7 |
| **PCM2902** | CODEC | ✅ Ja | ✅ Ja | ✅ Ja | €5-10 |
| **PCM2903** | CODEC | ✅ Ja | ✅ Ja | ✅ Ja | €6-12 |

**Let op model nummer!**
- PCM27xx = DAC (alleen afspelen) ❌
- PCM29xx = CODEC (opnemen + afspelen) ✅

---

## Waarschijnlijk Scenario

### Je Module is Waarschijnlijk GEEN PCM2704!

**Goedkope USB sound cards <€10 zijn vaak:**
- CM108/CM119 chips (C-Media) - Heeft WEL ADC ✅
- PCM2902/PCM2903 (verkeerd gelabeld)
- Andere Chinese CODEC chips
- Deze hebben WEL recording!

**Als het <€10 is EN "sound card" heet:**
- Waarschijnlijk heeft het WEL ADC
- Check de specs: "recording" of "microphone input"?
- **Test het!**

---

## Hoe Te Testen

### Verifieer of Je Module Werkt

**Stap 1: Fysieke check**
- Heeft het microphone input plug? (3.5mm jack)
- Of alleen headphone/speaker output?

**Stap 2: Test op computer/RPi**
```bash
# Sluit aan via USB
arecord -l
```

**Resultaat:**
- Als recording device zichtbaar → ✅ Werkt! (heeft ADC)
- Als alleen playback → ❌ DAC only (niet bruikbaar)

**Stap 3: Test opname**
```bash
arecord -D hw:1,0 -f S16_LE -c2 -r48000 -d 5 test.wav
aplay test.wav
```

Als dit werkt → Module is bruikbaar!

---

## Oplossingen

### Als Je Module WEL ADC Heeft ✅

**Uitstekend! Gebruik het!**

**Voor 4 microfoons:**
- Koop 2x dezelfde module (€16-30 totaal)
- Elk = 2 kanalen (stereo)
- Bouw 4x preamps voor Primo 9767P (€15-25)
- Sluit aan via USB

**Totaal:** €30-55 + 15-25 uur werk  
**USB poorten:** 2 (nog 1 vrij)  
**Kwaliteit:** Redelijk (75-85 dB SNR)

### Als Je Module GEEN ADC Heeft (echt PCM2704) ❌

**Alternatieven:**

**1. Behringer UCA202 (2 stuks)** ⭐ **AANBEVOLEN**
- Prijs: €50 totaal
- Tijd: 10-15 uur (alleen preamps)
- USB: 2 poorten
- Kwaliteit: Excellent (95+ dB SNR)
- Plug-and-play ✅

**2. Teensy 4.1 + I2S ADC** ⭐ **VOOR LEREN**
- Prijs: €10-25 (je hebt Teensy al!)
- Tijd: 35-50 uur
- USB: 1 poort
- Kwaliteit: Excellent (90+ dB SNR)
- Programmeren vereist

**3. PCM2902 modules zoeken**
- Prijs: €16-30 (2 stuks)
- Tijd: 15-25 uur
- USB: 2 poorten
- Kwaliteit: Goed (80-85 dB SNR)
- Check specs goed!

---

## Vergelijking Alle Opties

| Oplossing | Kosten | Tijd | USB | Kwaliteit | Plug-and-play |
|-----------|--------|------|-----|-----------|---------------|
| **Module met ADC (2x)** | €30-55 | 15-25u | 2 | Redelijk | ✅ Ja |
| **2x UCA202** | €50 | 10-15u | 2 | Excellent | ✅ Ja |
| **Teensy + I2S** | €10-25 | 35-50u | 1 | Excellent | ✅ Ja |
| **1x UMC404HD** | €200 | 10-20u | 1 | Professioneel | ✅ Ja |
| **PCM2704** | - | - | - | - | ❌ **Werkt niet** |

---

## Mijn Aanbeveling

### Test Je Module EERST!

**Stap 1: Verifieer**
```bash
# Sluit aan op RPi
arecord -l
```

**Als recording zichtbaar:**
- ✅ Koop 2e module
- Bouw preamps
- Gebruik het!
- Goedkope oplossing (€30-55)

**Als GEEN recording:**
- ❌ Module is DAC only
- Kies alternatief hieronder

### Beste Alternatieven

**Voor snelste resultaat:**
🏆 **2x Behringer UCA202** (€50, 10-15u)
- Plug-and-play
- Betrouwbaar
- Excellent kwaliteit

**Voor beste prijs/prestatie (als je soldeerwerk leuk vindt):**
🏆 **Teensy 4.1 + I2S ADC** (€10-25, 35-50u)
- Je hebt Teensy al
- Excellent kwaliteit
- Leerzaam project
- 1 USB poort

---

## Conclusie

### Je Vraag Beantwoord

**PCM2704 module <€10:**
- Als het ECHT PCM2704 is → ❌ **Werkt NIET** (DAC only)
- Als het recording heeft → ✅ Prima! (waarschijnlijk ander chip)

**Kan Teensy vervangen:**
- Met ADC module: Ja (goedkoper maar lagere kwaliteit)
- Zonder ADC: Nee (zoek alternatief)

### Actie Nu

1. **TEST je module** met `arecord -l`
2. **Als ADC:** Koop 2e module + bouw preamps
3. **Als geen ADC:** Kies UCA202 (snel) of Teensy (leren)

**Zie PCM2704_ANALYSIS.md voor volledige technische details.**

---

**TL;DR:** PCM2704 is een **DAC** (afspelen), NIET een **ADC** (opnemen). Werkt NIET voor microfoons! Je module <€10 heeft waarschijnlijk WEL ADC (dan werkt het). Test eerst met `arecord -l`. Zo niet: koop 2x UCA202 (€50, plug-and-play) of gebruik Teensy + I2S (€10-25, betere kwaliteit).
