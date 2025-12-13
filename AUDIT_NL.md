# BirdNET-Pi-MigCount Codebase Audit (Nederlands)

**Datum:** 13 december 2025  
**Auditor:** GitHub Copilot  
**Repository:** YvedD/BirdNET-Pi-MigCount (Fork van Nachtzuster/BirdNET-Pi)

---

## Samenvatting

Deze codebase is een **fork van BirdNET-Pi**, een real-time akoestisch vogelclassificatiesysteem dat primair is ontworpen voor Raspberry Pi apparaten. Het systeem gebruikt machine learning modellen (BirdNET) om vogelsoorten te identificeren aan de hand van geluidsopnames.

**Hoofdconclusie:** ✅ **JA, deze codebase kan als vertrekpunt worden gebruikt** voor een veldsysteem met 2-4 niet-phantom-powered microfoons, met enkele overwegingen en aanpassingen.

---

## 1. Wat is BirdNET-Pi?

BirdNET-Pi is een akoestisch monitoringsysteem dat:
- **Audio opneemt** continu van microfoons of RTSP-streams
- **Audio analyseert** in real-time met TensorFlow Lite machine learning modellen
- **Vogelsoorten identificeert** aan de hand van vocalisaties
- **Detecties opslaat** in een SQLite database
- **Een webinterface biedt** voor het bekijken van resultaten, spectrogrammen en statistieken
- **Integreert met BirdWeather** voor het delen van data met de community

---

## 2. Hardware Vereisten

### 2.1 Ondersteunde Platforms

**Officiële ondersteuning:**
- Raspberry Pi 5, 4B, 400 ✅
- Raspberry Pi 3B+ (alleen ARM64-Lite) ⚠️
- Raspberry Pi 0W2 (alleen ARM64-Lite) ⚠️
- x86_64 systemen (Debian 12/13) ✅

**Besturingssysteem:**
- **Aanbevolen:** RaspiOS Trixie (64-bit)
- **Werkt ook:** RaspiOS Bookworm (64-bit)

### 2.2 Opslagvereisten

- **Repository grootte:** ~268 MB
- **ML Modellen:** ~40-55 MB
- **Runtime opslag:**
  - Audio-opnames: ~50-100 MB per uur
  - Database groeit in de loop van de tijd
  - Automatisch schijfbeheer beschikbaar (opruimen bij >95% vol)

---

## 3. Microfoonondersteuning

### 3.1 Huidige Configuratie

**Standaard setup:**
- **KANALEN:** 2 (stereo)
- **Sample Rate:** 48 kHz
- **Formaat:** PCM_S16_LE (16-bit)
- **Opnamekaart:** `default` (PulseAudio)

### 3.2 Scenario's met Meerdere Microfoons

#### ✅ **Scenario 1: Enkele USB-microfoon**
- **Status:** Volledig ondersteund out-of-the-box
- **Setup:** Plug USB-mic in, systeem detecteert automatisch
- **Best voor:** Enkelvoudig monitoringspunt

#### ⚠️ **Scenario 2: Meerdere USB-microfoons op Één Pi**
- **Status:** Mogelijk met aanpassingen
- **Uitdaging:** Huidige implementatie neemt op van ÉÉN apparaat
- **Oplossingen:**
  1. **PulseAudio Multi-Source:** Combineer inputs in één virtueel apparaat
  2. **Meerdere Recording Services:** Draai aparte instanties per microfoon
  3. **RTSP Stream Benadering:** Gebruik elke mic als RTSP-streambron

**Haalbaarheid:** ⚠️ **GEMIDDELD** - Vereist aanpassingen aan recording service

#### ✅ **Scenario 3: Meerdere RTSP-streams**
- **Status:** Reeds ondersteund!
- **Configuratie:** `RTSP_STREAM` in config accepteert komma-gescheiden URLs
- **Best voor:** Netwerkverbonden microfoons of gedistribueerde setup

#### ✅ **Scenario 4: Multi-Channel Audio Interface**
- **Status:** Ondersteund via ALSA-apparaatselectie
- **Voorbeeld:** 4-kanaals USB audio-interface
- **Setup:** Stel `REC_CARD` in op specifiek ALSA-apparaat

### 3.3 Niet-Phantom-Powered Microfoons

**Compatibiliteit:** ✅ **Volledig Compatibel**

Het systeem werkt met:
- **USB-microfoons** (zelf gevoed via USB)
- **Line-level inputs** (bijv. van draagbare recorders)
- **Elk ALSA-compatibel audioapparaat**

**NIET vereist:**
- Phantom power (48V)
- Externe preamps (tenzij je microfoons ze nodig hebben)
- Speciale drivers (standaard Linux ALSA)

**Aanbevolen microfoons voor veldgebruik:**
- USB-microfoons met weerbestendige behuizing
- Lage eigenruis (< 20 dBA)
- Omnidirectioneel patroon voor vogelmonitoring
- USB-gevoed (geen phantom power nodig)

---

## 4. Licentie & Gebruiksbeperkingen

### 4.1 Licentie

**Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)**

**Belangrijkste punten:**
- ❌ **GEEN COMMERCIEEL GEBRUIK** - Mag niet worden gebruikt voor commerciële producten
- ✅ **Naamsvermelding vereist** - Moet originele auteurs vermelden
- ✅ **Gelijk delen** - Afgeleide werken moeten dezelfde licentie gebruiken
- ✅ **Gratis voor persoonlijk, educatief, onderzoeksgebruik**

### 4.2 Implicaties voor Veldinzet

**Toegestaan:**
- ✅ Persoonlijke vogelmonitoring
- ✅ Onderzoeksprojecten
- ✅ Educatieve doeleinden
- ✅ Non-profit natuurbeschermingsinitiatieven
- ✅ Community science-initiatieven

**NIET toegestaan:**
- ❌ Verkopen van het systeem of de service
- ❌ Commerciële vogelmonitoringsdiensten
- ❌ Integratie in commerciële producten

---

## 5. Haalbaarheid Veldinzet

### 5.1 Inzetscenario's

#### **Optie A: Enkele Raspberry Pi met 2-4 USB-microfoons**

**Aanpak:** Multi-source PulseAudio setup

**Voordelen:**
- Lagere kosten (één Pi)
- Gecentraliseerde verwerking
- Enkele database

**Nadelen:**
- USB-bandbreedtebeperkingen
- Kabellengterestricties (~5m voor USB)
- Enkel storingspunt
- Vereist aangepaste PulseAudio-configuratie

**Haalbaarheid:** ⚠️ **GEMIDDELD** - Vereist aanpassingen aan recording service

#### **Optie B: Gedistribueerde Raspberry Pi's (Eén per Microfoon)**

**Aanpak:** 2-4 Raspberry Pi's, elk met één microfoon

**Voordelen:**
- Geen USB-bandbreedteproblemen
- Kan zich over groter gebied verspreiden
- Redundantie (als één faalt, gaan anderen door)
- Elke Pi is onafhankelijk

**Nadelen:**
- Hogere kosten (meerdere Pi's, SD-kaarten, voedingen)
- Meerdere databases om te beheren
- Netwerk vereist voor gecentraliseerde weergave

**Haalbaarheid:** ✅ **HOOG** - Werkt met huidige code

**Setup:**
1. Installeer BirdNET-Pi op elk apparaat
2. Configureer unieke hostnamen
3. Optioneel: Stel centrale aggregatieserver op
4. Stroom: USB-powerbanks voor velddraagbaarheid

#### **Optie C: Hybride - Eén Pi met RTSP Netwerkmicrofoons**

**Aanpak:** Netwerk-audioapparaten streamen naar één Pi

**Voordelen:**
- Flexibele microfoonplaatsing
- Gecentraliseerde verwerking
- Reeds ondersteund door code!

**Nadelen:**
- Vereist netwerkinfrastructuur
- RTSP-compatibele microfoons of converters nodig
- Netwerkbandbreedteoverwegingen

**Haalbaarheid:** ✅ **HOOG** - Out-of-the-box ondersteund

**Configuratie:** (in `/etc/birdnet/birdnet.conf`)
```bash
RTSP_STREAM="rtsp://mic1-ip/stream,rtsp://mic2-ip/stream,rtsp://mic3-ip/stream,rtsp://mic4-ip/stream"
```

### 5.2 Stroomoverwegingen voor Veldgebruik

**Raspberry Pi Stroom:**
- Pi 4B: ~3W idle, ~6W onder belasting
- Pi 5: ~4W idle, ~12W onder belasting
- Pi 3B+: ~2.5W idle, ~5W onder belasting

**Veldstroomopties:**
1. **USB-powerbanks:** 20.000mAh = ~24-48 uur voor Pi 4B
2. **Solar + Batterij:** Duurzaam voor langdurige inzet
3. **PoE (Power over Ethernet):** Als netwerk beschikbaar is (vereist PoE HAT)

**Microfoons:**
- USB-microfoons: Gevoed via USB (~0,5-1W elk)
- Totaal voor 4 microfoons: ~2-4W extra

**Voorbeeld Veldopstelling:**
- 1x Raspberry Pi 4B: 6W
- 4x USB-microfoons: 4W
- **Totaal: ~10W**
- **20.000mAh powerbank:** ~15-20 uur looptijd

### 5.3 Omgevingsoverwegingen

**Weerbescherming:**
- Systeem is NIET waterdicht standaard
- Vereist weerbestendige behuizing
- Microfoons hebben outdoor-rated behuizing of windschermen nodig
- Overweeg droogmiddelpakjes voor vochtigheid

**Temperatuur:**
- Raspberry Pi bedrijfsbereik: 0°C tot 50°C
- Kan throttlen bij hoge temperaturen
- Koellichamen aanbevolen voor gesloten ruimtes

**Dierenleven:**
- Beveilig bekabeling (dieren kunnen knagen)
- Verhoogde montage om manipulatie te voorkomen
- Camouflage indien in openbare gebieden

---

## 6. Implementatiegids voor Meerdere Microfoons

### 6.1 Aanbevolen Aanpak voor 2-4 Microfoons

**Beste Optie:** **Optie C (RTSP Hybride)** of **Optie B (Gedistribueerde Pi's)**

#### Als RTSP Wordt Gebruikt (Aanbevolen voor Flexibiliteit):

**Stap 1:** Stel audio-streaming apparaten in
- Gebruik Raspberry Pi Zero's met microfoons als RTSP-servers
- Of gebruik IP-audioapparaten met RTSP-uitgang
- Software: Gebruik `ffmpeg` om RTSP-streams te maken

**Voorbeeld RTSP Server Setup (Pi Zero met Mic):**
```bash
# Op elke microfoon Pi
# Installeer eerst een RTSP server zoals MediaMTX (voorheen rtsp-simple-server)
# Download van: https://github.com/bluenviron/mediamtx/releases
# Start dan MediaMTX en gebruik ffmpeg om audio ernaar te pushen:

ffmpeg -f alsa -i hw:0 -acodec aac -ab 192k -ac 2 -f rtsp rtsp://localhost:8554/stream

# Of gebruik HLS streaming wat eenvoudiger is:
# ffmpeg -f alsa -i hw:0 -acodec aac -hls_time 2 -hls_list_size 3 /var/www/html/stream.m3u8
```

**Let op:** RTSP streaming vereist een draaiende RTSP server op elke microfoon Pi. MediaMTX wordt aanbevolen omdat het lichtgewicht is en goed geschikt voor Raspberry Pi.

**Stap 2:** Configureer hoofd-Pi

Bewerk `/etc/birdnet/birdnet.conf`:
```bash
RTSP_STREAM="rtsp://192.168.1.10:8554/stream,rtsp://192.168.1.11:8554/stream,rtsp://192.168.1.12:8554/stream"
```

**Stap 3:** Het systeem verwerkt automatisch meerdere streams
- Code in `birdnet_recording.sh` loopt over streams
- Maakt aparte WAV-bestanden met stream-ID's
- Analyse verwerkt alle bestanden

### 6.2 Veldinzet Checklist

**Hardware:**
- [ ] Raspberry Pi 4B of 5 (aanbevolen)
- [ ] MicroSD-kaart (32GB+ Class 10)
- [ ] USB-microfoons (2-4, weerbestendig indien mogelijk)
- [ ] Voeding (USB-C voor Pi 4/5, MicroUSB voor 3B+)
- [ ] Powerbank of zonne-energie setup voor verlengd veldgebruik
- [ ] Weerbestendige behuizing
- [ ] USB-kabels (kwaliteitskabels, max 5m)
- [ ] Netwerkkabels (bij gebruik van Ethernet voor RTSP)

**Software Setup:**
- [ ] Installeer RaspiOS Trixie 64-bit Lite
- [ ] Draai installer van basis repository:
  ```bash
  curl -s https://raw.githubusercontent.com/Nachtzuster/BirdNET-Pi/main/newinstaller.sh | bash
  ```
  **Let op:** Deze fork (YvedD/BirdNET-Pi-MigCount) is voor analyse/audit doeleinden. Voor installatie, gebruik de basis Nachtzuster repository die actief onderhouden wordt en het installatiescript bevat. Deze fork documenteert evaluatiebevindingen.
- [ ] Configureer locatie (breedtegraad/lengtegraad)
- [ ] Stel RTSP-streams of USB-micconfiguratie in
- [ ] Test opname met `arecord -l` en `arecord -D [apparaat] -d 10 test.wav`
- [ ] Verifieer dat analyse draait: `sudo systemctl status birdnet_analysis`
- [ ] Toegang tot webinterface om detecties te bevestigen

**Veldtesting:**
- [ ] Test stroomverbruik en batterijduur
- [ ] Verifieer audiokwaliteit op inzetlocatie
- [ ] Controleer netwerkconnectiviteit (bij gebruik van RTSP)
- [ ] Monitor gedurende eerste 24 uur om stabiliteit te verzekeren
- [ ] Stel schijfbeheer in (auto-opruimen oude opnames)

---

## 7. Voordelen & Beperkingen

### 7.1 Voordelen

**Voor Deze Codebase:**
- ✅ **Volwassen, getest systeem** met actieve community
- ✅ **Goed gedocumenteerd** (wiki, discussies)
- ✅ **Actief onderhouden** fork met verbeteringen
- ✅ **Out-of-box functionaliteit** voor basisgebruik
- ✅ **RTSP-ondersteuning** maakt flexibele microfoonplaatsing mogelijk
- ✅ **Automatisch schijfbeheer** voor langdurige inzet
- ✅ **Backup/restore** voor datamigratie
- ✅ **BirdWeather-integratie** voor data delen
- ✅ **Meertalige ondersteuning** voor soortnamen
- ✅ **Notificatiesysteem** (90+ platforms via Apprise)

**Voor Veldinzet:**
- ✅ **Laag stroomverbruik** (geschikt voor batterij/solar)
- ✅ **Bewezen hardware** (Raspberry Pi)
- ✅ **Offline-capabel** (geen internet vereist voor werking)
- ✅ **Open source** (kan worden aangepast voor specifieke behoeften)

### 7.2 Beperkingen

**Systeembeperkingen:**
- ⚠️ **Enkele microfoon standaard** - Multi-mic vereist configuratie
- ⚠️ **Geen ingebouwde waterdichting** - Behuizing nodig
- ⚠️ **Beperkt tot 48kHz sample rate** - Sommige vogels vocaliseren hoger
- ⚠️ **Verwerkingskracht-afhankelijk** - Real-time analyse heeft adequate Pi nodig
- ⚠️ **Opslagbeheer vereist** - Lange inzetten vullen schijf
- ⚠️ **Geen ingebouwd remote beheer** - Handmatige toegang nodig voor updates

**Licentiebeperkingen:**
- ❌ **Alleen niet-commercieel** - Mag niet verkopen of commercialiseren
- ⚠️ **Gelijk-delen-vereiste** - Aanpassingen moeten open-source zijn

**Technische Schuld:**
- ⚠️ **Gemengde tech stack** - Python, Bash, PHP
- ⚠️ **Legacy-componenten** - Enkele geërfde code
- ⚠️ **Beperkte multi-mic ondersteuning** - Heeft customisatie nodig

---

## 8. Aanbevelingen

### 8.1 Voor Jouw Gebruikssituatie (2-4 Microfoons in Veld)

**Primaire Aanbeveling:**
**Gebruik Optie C: Gedistribueerde Raspberry Pi's met RTSP-streaming**

**Waarom:**
1. ✅ Werkt met huidige code (geen aanpassingen nodig)
2. ✅ Maximale flexibiliteit in microfoonplaatsing
3. ✅ Elke microfoon kan 10-100 meter uit elkaar staan
4. ✅ Redundantie als één apparaat faalt
5. ✅ Kan goedkopere Pi Zero 2W gebruiken voor microfoonknooppunten

**Setup:**
- **Hoofdeenheid:** Raspberry Pi 4B (analyse + webinterface)
- **Mic-knooppunten:** 2-4x Raspberry Pi Zero 2W met USB-microfoons
- **Stroom:** USB-powerbanks of solar voor elk knooppunt
- **Netwerk:** WiFi-mesh of bedraad Ethernet

**Alternatief (Budgetvriendelijk):**
**Optie B: Aparte Raspberry Pi's, Geen RTSP**
- Elke Pi draait volledige BirdNET-Pi stack
- Bekijk data op elk individueel
- Lagere complexiteit, hogere hardwarekosten

### 8.2 Specifieke Actiepunten

**Vóór Inzet:**
1. **Test met één microfoon** - Verifieer dat systeem werkt in jouw omgeving
2. **Bepaal plaatsing** - Waar zullen microfoons worden geplaatst?
3. **Kies stroomstrategie** - Batterijlooptijd vs. solar vs. netspanning
4. **Selecteer behuizingen** - IP65+ geclassificeerd voor buitengebruik
5. **Netwerkplanning** - WiFi-bereik of kabeltrajecten voor RTSP

**Code-aanpassingen (indien nodig):**
1. **Fork deze repository** - Maak je eigen versie voor het volgen van wijzigingen
2. **Documenteer je setup** - Noteer configuratie voor toekomstige referentie
3. **Overweeg terug te bijdragen** - Deel verbeteringen met community (licentie vereist dit)

**Testfase:**
1. **Lab-testen** - Stel systeem binnenshuis in met alle microfoons
2. **24-uurs burn-in** - Verifieer stabiliteit
3. **Veldproef** - 1 week inzet met dagelijkse controles
4. **Parameters aanpassen** - Confidence threshold, opnamelengte, etc.

### 8.3 Toekomstige Verbeteringen om te Overwegen

**Voor Multi-Microfoon Ondersteuning:**
- Implementeer echte multi-channel analyse (ruimtelijke audio)
- Voeg microfoon-ID toe aan detectiegegevens
- Creëer visualisatie die toont welke mic welke soort detecteerde
- Implementeer geluidsbronlokalisatie (triangulatie)

**Voor Veldrobuustheid:**
- Voeg cellulaire connectiviteit toe voor remote monitoring
- Implementeer geautomatiseerde gezondheidscontroles en waarschuwingen
- Creëer backup-analysemodus als primaire Pi faalt
- Voeg omgevingssensoren toe (temperatuur, vochtigheid)

---

## 9. Conclusie

### 9.1 Samenvatting

**Vraag:** Kan deze fork worden gebruikt als vertrekpunt voor een veldsysteem met 2-4 niet-phantom-powered microfoons?

**Antwoord:** ✅ **JA, absoluut.**

Deze codebase is een solide basis voor jouw gebruikssituatie. Het systeem is:
- **Volwassen en getest** in real-world inzetten
- **Flexibel genoeg** om meerdere microfoons te ondersteunen via RTSP of gedistribueerde setup
- **Goed geschikt voor veldgebruik** met gepaste stroom en weerbescherming
- **Niet-commerciële licentie compatibel** met onderzoeks-/natuurbeschermingsprojecten

**Belangrijke Succesfactoren:**
1. Gebruik RTSP-streaming aanpak voor eenvoudigste multi-mic ondersteuning
2. Zorg voor adequate stroomvoorziening voor verlengd veldgebruik
3. Maak alle componenten goed weerbestendig
4. Test grondig vóór definitieve inzet
5. Plan voor data-ophaling en backup

### 9.2 Risicoanalyse

**Laag Risico:**
- Enkele microfoon inzet
- Korte-termijn monitoring (dagen tot weken)
- Nabije toegang voor onderhoud

**Gemiddeld Risico:**
- 2-4 microfoon gedistribueerd systeem
- Maandlange inzetten
- Afgelegen locaties met wekelijkse toegang

**Hoog Risico (vereist expertise):**
- Aangepaste multi-channel enkele-apparaat setup
- Langdurige onbeheerde inzetten (maanden)
- Extreme weersomstandigheden
- Volledig off-grid zonne-energie

### 9.3 Volgende Stappen

1. **Beslissing:** Kies inzetarchitectuur (Optie B of C)
2. **Prototype:** Bouw eerst enkele-mic systeem
3. **Test:** Verifieer in je doelomgeving
4. **Schaal:** Voeg extra microfoons toe
5. **Zet in:** Implementeer volledige veldsetup
6. **Monitor:** Regelmatige controles en onderhoud
7. **Itereer:** Verbeter op basis van ervaring

---

## Bijlage: Nuttige Commando's

**Controleer audio-apparaten:**
```bash
arecord -l                    # Lijst opnameapparaten
aplay -L                      # Lijst afspleelapparaten
pactl list sources short      # PulseAudio bronnen
```

**Test opname:**
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

**Controleer schijfgebruik:**
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

## Bijlage: Bronnen

**Officiële Documentatie:**
- BirdNET-Pi Wiki: https://github.com/mcguirepr89/BirdNET-Pi/wiki
- Originele BirdNET: https://github.com/kahst/BirdNET-Analyzer
- Deze Fork: https://github.com/Nachtzuster/BirdNET-Pi

**Community:**
- GitHub Discussies: https://github.com/mcguirepr89/BirdNET-Pi/discussions
- BirdWeather Platform: https://app.birdweather.com

**Hardware Gidsen:**
- Microfoonaanbevelingen: https://github.com/mcguirepr89/BirdNET-Pi/discussions/39
- DIY-microfoon bouwen: https://github.com/DD4WH/SASS/wiki

---

**Einde Audit**
