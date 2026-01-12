from dataclasses import dataclass
from typing import Tuple

SAMPLE_RATES = (24000, 48000)
NFFT_OPTIONS = (2048, 4096, 8192)
WINDOW_OPTIONS = ("hann", "blackman", "hamming")

MATPLOTLIB_CMAPS = ("magma", "inferno", "viridis", "cividis", "plasma", "gray_r", "hot", "jet")
PYQTGRAPH_CMAPS = ("magma", "inferno", "viridis", "plasma", "cividis", "gray")
DATASHADER_CMAPS = ("viridis", "plasma", "magma", "inferno", "cividis", "gray", "fire")
DATASHADER_SHADINGS = ("linear", "eq_hist", "log", "cbrt")

RENDERER_CHOICES = (
    "Matplotlib (reference)",
    "PyQtGraph (fast)",
    "Datashader + Holoviews (dense)",
)
DEFAULT_RENDERER = RENDERER_CHOICES[0]

DEFAULT_FMIN = 0.0
DEFAULT_FMAX = 12000.0
DEFAULT_DB_RANGE = 60.0
DEFAULT_PER_FREQ_NORM = True
DEFAULT_CMAP = "magma"
DEFAULT_DPI = 140
DEFAULT_FIGSIZE = (10.0, 4.0)


@dataclass(frozen=True)
class SpectrogramDSP:
    sample_rate: int = SAMPLE_RATES[-1]
    n_fft: int = NFFT_OPTIONS[1]
    hop_length: int = 512
    window: str = WINDOW_OPTIONS[0]
    fmin: float = DEFAULT_FMIN
    fmax: float = DEFAULT_FMAX
    per_freq_norm: bool = DEFAULT_PER_FREQ_NORM
    db_range: float = DEFAULT_DB_RANGE


@dataclass(frozen=True)
class MatplotlibRenderParams:
    cmap: str = DEFAULT_CMAP
    dpi: int = DEFAULT_DPI
    figsize: Tuple[float, float] = DEFAULT_FIGSIZE


@dataclass(frozen=True)
class PyQtGraphRenderParams:
    cmap: str = DEFAULT_CMAP
    width: int = 900
    height: int = 420
    interpolate: bool = True
    gamma: float = 1.0
    downsample: int = 1


@dataclass(frozen=True)
class DatashaderRenderParams:
    cmap: str = DEFAULT_CMAP
    shading: str = DATASHADER_SHADINGS[0]
    width: int = 900
    height: int = 420
