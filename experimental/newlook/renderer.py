import io
from pathlib import Path
from typing import Tuple

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import MaxNLocator  # noqa: E402


def render_spectrogram(
    freqs,
    times,
    db_spectrogram,
    *,
    cmap: str,
    figsize: Tuple[float, float],
    dpi: int,
    vmin: float,
    vmax: float,
    fmin: float,
    fmax: float,
) -> bytes:
    fig, ax = plt.subplots(figsize=figsize, dpi=dpi)
    mesh = ax.pcolormesh(times, freqs, db_spectrogram, shading="auto", cmap=cmap, vmin=vmin, vmax=vmax)
    ax.set_ylabel("Frequency (Hz)")
    ax.set_xlabel("Time (s)")
    ax.set_ylim(fmin, fmax)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label("Amplitude (dB)")
    cbar.set_ticks([vmin, vmax])
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer.read()


def save_png(png_bytes: bytes, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(png_bytes)
    return output_path
