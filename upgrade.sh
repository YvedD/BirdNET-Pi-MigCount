#!/usr/bin/env bash
# Upgrade script voor bestaande BirdNET-Pi installaties
# Installeert ontbrekende dependencies voor analyse en experimentele spectrogrammen

set -e  # Stop bij fouten

echo "=========================================="
echo "BirdNET-Pi Dependencies Upgrade Script"
echo "=========================================="
echo ""

# Check of we niet als root draaien
if [ "$EUID" == 0 ]; then
  echo "❌ Fout: Voer dit script uit als normale gebruiker, niet als root."
  echo "   Gebruik: ./upgrade.sh"
  exit 1
fi

# Bepaal gebruiker en home directory
if [ -n "${BIRDNET_USER}" ]; then
  USER=${BIRDNET_USER}
  HOME=/home/${BIRDNET_USER}
else
  USER=$(whoami)
  HOME=$HOME
fi

# Bepaal de BirdNET-Pi directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Check of we in de BirdNET-Pi directory staan
if [ -f "$SCRIPT_DIR/requirements.txt" ] && [ -f "$SCRIPT_DIR/newinstaller.sh" ]; then
  BIRDNET_DIR="$SCRIPT_DIR"
elif [ -d "$HOME/BirdNET-Pi" ]; then
  BIRDNET_DIR="$HOME/BirdNET-Pi"
elif [ -d "$HOME/BirdNET-Pi-MigCount" ]; then
  BIRDNET_DIR="$HOME/BirdNET-Pi-MigCount"
else
  echo "❌ Fout: BirdNET-Pi directory niet gevonden"
  echo "   Verwachtte: $HOME/BirdNET-Pi of $HOME/BirdNET-Pi-MigCount"
  echo "   Of voer dit script uit vanuit de BirdNET-Pi directory"
  exit 1
fi

echo "✓ BirdNET-Pi directory gevonden: $BIRDNET_DIR"
echo ""

# Check of requirements.txt bestaat
if [ ! -f "$BIRDNET_DIR/requirements.txt" ]; then
  echo "❌ Fout: requirements.txt niet gevonden in $BIRDNET_DIR"
  exit 1
fi

echo "📦 Dependencies die worden geïnstalleerd:"
echo ""
echo "   Voor analyse functionaliteit:"
echo "   - scipy (highpass audio filter)"
echo ""
echo "   Voor experimentele spectrogrammen:"
echo "   - datashader (high-performance rendering)"
echo "   - holoviews (visualisatie framework)"
echo "   - xarray (data arrays)"
echo "   - pyqtgraph (alternatieve rendering)"
echo ""

# Check of virtual environment bestaat
if [ -d "$BIRDNET_DIR/birdnet" ]; then
  echo "✓ Virtual environment gevonden"
  VENV_PYTHON="$BIRDNET_DIR/birdnet/bin/python3"
  VENV_PIP="$BIRDNET_DIR/birdnet/bin/pip3"
  
  if [ ! -f "$VENV_PYTHON" ]; then
    echo "❌ Fout: Python niet gevonden in virtual environment"
    exit 1
  fi
else
  echo "⚠️  Virtual environment niet gevonden"
  echo "   Systeem-wide Python wordt gebruikt"
  VENV_PYTHON="python3"
  VENV_PIP="pip3"
fi

echo ""
echo "🔄 Dependencies installeren..."
echo ""

cd "$BIRDNET_DIR"

# Installeer dependencies
if $VENV_PIP install -U -r requirements.txt; then
  echo ""
  echo "=========================================="
  echo "✅ Upgrade succesvol voltooid!"
  echo "=========================================="
  echo ""
  echo "Geïnstalleerde/geüpgrade dependencies:"
  echo "  ✓ scipy"
  echo "  ✓ datashader"
  echo "  ✓ holoviews"
  echo "  ✓ xarray"
  echo "  ✓ pyqtgraph"
  echo ""
  echo "💡 Volgende stappen:"
  echo "   - Herstart BirdNET-Pi services met: sudo systemctl restart birdnet_analysis.service"
  echo "   - Of herstart het hele systeem met: sudo reboot"
  echo ""
  echo "📊 Experimentele spectrogrammen zijn nu beschikbaar in:"
  echo "   - experimental/spectrogram_generator.py"
  echo "   - experimental/newlook/app.py"
  echo ""
else
  echo ""
  echo "=========================================="
  echo "❌ Fout tijdens installatie"
  echo "=========================================="
  echo ""
  echo "Mogelijke oplossingen:"
  echo "  1. Controleer je internetverbinding"
  echo "  2. Probeer opnieuw: ./upgrade.sh"
  echo "  3. Handmatig installeren:"
  echo "     cd $BIRDNET_DIR"
  echo "     source birdnet/bin/activate"
  echo "     pip3 install -U scipy datashader holoviews xarray pyqtgraph"
  echo ""
  exit 1
fi
