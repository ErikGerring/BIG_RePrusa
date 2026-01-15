from __future__ import annotations

from typing import Optional, Sequence

from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPainter, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView, QVBoxLayout, QWidget

from ..core.primitive import Shape, crosshatch_pattern, hatch_pattern, hatch_fill


class Plotter2DView(QWidget):
    """Simple 2D preview canvas.

    Kept intentionally small so it's easy to swap for a more capable preview later
    without touching the rest of the UI.
    """

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)

        self._scene = QGraphicsScene(self)
        self._view = QGraphicsView(self._scene, self)
        self._view.setRenderHint(QPainter.Antialiasing, True)
        self._view.setBackgroundBrush(QBrush(QColor(235, 235, 235)))

        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.addWidget(self._view)

        self._bed_w = 180.0
        self._bed_h = 180.0
        self._grid_step = 10.0
        self._shapes: list[Shape] = []

        self.set_bed(self._bed_w, self._bed_h)

    def set_bed(self, bed_w: float, bed_h: float, grid_step: float = 10.0) -> None:
        self._bed_w = float(bed_w)
        self._bed_h = float(bed_h)
        self._grid_step = float(grid_step)

        self._redraw()

    def set_shapes(self, shapes: Sequence[Shape]) -> None:
        self._shapes = list(shapes)
        self._redraw()

    def _redraw(self) -> None:
        self._scene.clear()

        # Bed background
        bed_pen = QPen(QColor(40, 40, 40))
        bed_pen.setWidthF(0.0)
        self._scene.addRect(0, 0, self._bed_w, self._bed_h, bed_pen, QBrush(QColor(80, 80, 80)))

        # Grid
        grid_pen = QPen(QColor(120, 120, 120))
        grid_pen.setWidthF(0.0)
        step = max(1.0, float(self._grid_step))

        x = 0.0
        while x <= self._bed_w + 1e-6:
            self._scene.addLine(x, 0.0, x, self._bed_h, grid_pen)
            x += step

        y = 0.0
        while y <= self._bed_h + 1e-6:
            self._scene.addLine(0.0, y, self._bed_w, y, grid_pen)
            y += step

        # Shapes
        outline_pen = QPen(QColor(230, 230, 230))
        outline_pen.setWidthF(0.0)

        fill_pen = QPen(QColor(200, 200, 200))
        fill_pen.setWidthF(0.0)

        for s in self._shapes:
            # Fill (hatch)
            if isinstance(s.fillpattern, hatch_pattern):
                try:
                    segs = hatch_fill(s, s.fillpattern)
                except Exception:
                    segs = []
                for seg in segs:
                    if len(seg) < 2:
                        continue
                    (x1, y1), (x2, y2) = seg[0], seg[1]
                    self._scene.addLine(x1, y1, x2, y2, fill_pen)

            # Fill (crosshatch)
            elif isinstance(s.fillpattern, crosshatch_pattern):
                try:
                    segs1 = hatch_fill(s, s.fillpattern.hatch1())
                    segs2 = hatch_fill(s, s.fillpattern.hatch2())
                    segs = list(segs1) + list(segs2)
                except Exception:
                    segs = []

                for seg in segs:
                    if len(seg) < 2:
                        continue
                    (x1, y1), (x2, y2) = seg[0], seg[1]
                    self._scene.addLine(x1, y1, x2, y2, fill_pen)

            # Outline
            pts = s.outline()
            for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
                self._scene.addLine(x1, y1, x2, y2, outline_pen)

        self._scene.setSceneRect(0, 0, self._bed_w, self._bed_h)
        self._view.fitInView(self._scene.sceneRect(), Qt.KeepAspectRatio)
