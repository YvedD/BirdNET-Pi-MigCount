import io
import os
from pathlib import Path
from typing import Tuple

import datashader as ds
import datashader.transfer_functions as tf
import holoviews as hv
import matplotlib

matplotlib.use("Agg")
import matplotlib.cm as cm
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import xarray as xr
from matplotlib.ticker import MaxNLocator  # noqa: E402

from experimental.newlook.config import DatashaderRenderParams, MatplotlibRenderParams, PyQtGraphRenderParams

_QT_APP = None
_HOLOVIEWS_READY = False
_QT_BINDING = None


class RendererBackend:
    MATPLOTLIB = "matplotlib"
    PYQTGRAPH = "pyqtgraph"
    DATASHADER = "datashader"


def _palette_from_cmap(name: str):
    try:
        cmap = cm.get_cmap(name)
    except ValueError:
        cmap = cm.get_cmap("viridis")
    return [matplotlib.colors.to_hex(cmap(i / 255.0)) for i in range(256)]


def render_matplotlib(
    freqs: np.ndarray,
    times: np.ndarray,
    db_spectrogram: np.ndarray,
    *,
    params: MatplotlibRenderParams,
    vmin: float,
    vmax: float,
    fmin: float,
    fmax: float,
) -> bytes:
    fig, ax = plt.subplots(figsize=params.figsize, dpi=params.dpi)
    mesh = ax.pcolormesh(times, freqs, db_spectrogram, shading="auto", cmap=params.cmap, vmin=vmin, vmax=vmax)
    ax.set_ylabel("Frequency (Hz)")
    ax.set_xlabel("Time (s)")
    ax.set_ylim(fmin, fmax)
    ax.xaxis.set_major_locator(MaxNLocator(nbins=8))
    ax.yaxis.set_major_locator(MaxNLocator(nbins=8))
    cbar = fig.colorbar(mesh, ax=ax)
    cbar.set_label("Amplitude (dB)")
    cbar.set_ticks(np.linspace(vmin, vmax, num=3))
    fig.tight_layout()
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=params.dpi, bbox_inches="tight")
    plt.close(fig)
    buffer.seek(0)
    return buffer.read()


def _import_qt():
    global _QT_BINDING
    if _QT_BINDING:
        return _QT_BINDING
    try:
        from PyQt5 import QtCore, QtGui, QtWidgets

        _QT_BINDING = ("PyQt5", QtCore, QtGui, QtWidgets)
    except Exception:
        from PyQt6 import QtCore, QtGui, QtWidgets

        _QT_BINDING = ("PyQt6", QtCore, QtGui, QtWidgets)
    return _QT_BINDING


def _ensure_qt_application():
    """Ensure a Qt application exists; default to offscreen for headless rendering."""
    if "QT_QPA_PLATFORM" not in os.environ:
        os.environ["QT_QPA_PLATFORM"] = "offscreen"
    global _QT_APP
    _, _, _, QtWidgets = _import_qt()
    if _QT_APP is None:
        _QT_APP = QtWidgets.QApplication.instance()
        if _QT_APP is None:
            _QT_APP = QtWidgets.QApplication([])
    return _QT_APP


def _lut_for_pyqtgraph(cmap_name: str):
    import pyqtgraph as pg

    cmap = pg.colormap.get(cmap_name, source="matplotlib")
    return cmap.getLookupTable(0.0, 1.0, 256)


def render_pyqtgraph(
    freqs: np.ndarray,
    times: np.ndarray,
    db_spectrogram: np.ndarray,
    *,
    params: PyQtGraphRenderParams,
    vmin: float,
    vmax: float,
) -> bytes:
    import pyqtgraph as pg

    _ensure_qt_application()
    _, QtCore, QtGui, _ = _import_qt()

    data = db_spectrogram[:, :: params.downsample]
    normalized = np.clip((data - vmin) / (vmax - vmin), 0.0, 1.0)
    if params.gamma != 1.0:
        normalized = np.power(normalized, params.gamma)
    lut = _lut_for_pyqtgraph(params.cmap)
    argb, _ = pg.functions.makeARGB(np.flipud(normalized), lut=lut)
    arr = np.require(argb, requirements=["C_CONTIGUOUS"])
    h, w, _ = arr.shape
    qimg = QtGui.QImage(arr.tobytes(), w, h, QtGui.QImage.Format_RGBA8888).copy()
    qt_transform = getattr(QtCore.Qt, "SmoothTransformation", getattr(QtCore.Qt.TransformationMode, "SmoothTransformation", None))
    qt_fast = getattr(QtCore.Qt, "FastTransformation", getattr(QtCore.Qt.TransformationMode, "FastTransformation", None))
    transform_mode = qt_transform if params.interpolate else qt_fast
    qt_ignore = getattr(QtCore.Qt, "IgnoreAspectRatio", getattr(QtCore.Qt.AspectRatioMode, "IgnoreAspectRatio", None))
    qimg = qimg.scaled(params.width, params.height, qt_ignore, transform_mode)
    buffer = QtCore.QBuffer()
    buffer.open(QtCore.QIODevice.WriteOnly)
    qimg.save(buffer, "PNG")
    return bytes(buffer.data())


def render_datashader(
    freqs: np.ndarray,
    times: np.ndarray,
    db_spectrogram: np.ndarray,
    *,
    params: DatashaderRenderParams,
    vmin: float,
    vmax: float,
    fmin: float,
    fmax: float,
) -> bytes:
    global _HOLOVIEWS_READY
    if not _HOLOVIEWS_READY:
        hv.extension("bokeh", logo=False)
        _HOLOVIEWS_READY = True
    data_array = xr.DataArray(db_spectrogram, coords={"y": freqs, "x": times}, dims=("y", "x"))
    canvas = ds.Canvas(
        plot_width=params.width,
        plot_height=params.height,
        x_range=(float(times.min()), float(times.max())),
        y_range=(float(fmin), float(fmax)),
    )
    agg = canvas.raster(data_array)
    palette = _palette_from_cmap(params.cmap)
    if params.shading == "eq_hist":
        shaded = tf.shade(agg, cmap=palette, how=params.shading)
    else:
        shaded = tf.shade(agg, cmap=palette, how=params.shading, span=(vmin, vmax))
    pil_image = tf.set_background(shaded, "white").to_pil()
    buffer = io.BytesIO()
    pil_image.save(buffer, format="PNG")
    return buffer.getvalue()


def save_png(png_bytes: bytes, output_path: Path) -> Path:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(png_bytes)
    return output_path
