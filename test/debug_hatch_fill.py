"""Debug-only hatch fill visualizer.

This file is intentionally standalone and meant to be deleted later.

Run:
  python debug_hatch_fill.py

If you get ImportError for matplotlib:
  python -m pip install matplotlib
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Sequence, Tuple

from src.reprusa.core.model import Point, Stroke
from src.reprusa.core.primitive import Shape, hatch_fill_ai, hatch_pattern, hatch_fill


@dataclass(frozen=True)
class PolyLike:
    """Minimal polygon-like object compatible with hatch_fill_ai()."""

    points: Sequence[Point]

    def outline(self) -> Stroke:
        pts = list(self.points)
        if not pts:
            return []
        if pts[0] != pts[-1]:
            pts.append(pts[0])
        return pts


def _plot_polyline(ax, stroke: Stroke, **kwargs) -> None:
    if not stroke:
        return
    xs = [p[0] for p in stroke]
    ys = [p[1] for p in stroke]
    ax.plot(xs, ys, **kwargs)


def _plot_segments(ax, segments: List[Stroke], **kwargs) -> None:
    for seg in segments:
        if len(seg) < 2:
            continue
        (x1, y1), (x2, y2) = seg[0], seg[1]
        ax.plot([x1, x2], [y1, y2], **kwargs)


def _plot_travel(ax, segments: List[Stroke], **kwargs) -> None:
    """Draw simple travel moves between hatch segments (gcode-like)."""

    if not segments:
        return

    prev_end: Point | None = None
    for seg in segments:
        if len(seg) < 2:
            continue
        start = seg[0]
        end = seg[1]
        if prev_end is not None:
            ax.plot([prev_end[0], start[0]], [prev_end[1], start[1]], **kwargs)
        prev_end = end


def main() -> None:
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib is not installed. Install it with: python -m pip install matplotlib")
        return

    pattern = hatch_pattern(angle=0.0, spacing=3.0, overscan=0.0)

    shapes: List[Tuple[str, object]] = [
        (
            "Rectangle",
            Shape.rectangle(bottom_left=(10.0, 10.0), width=70.0, height=40.0, fillpattern=pattern),
        ),
        (
            "Circle (approximated)",
            Shape.circle(center=(45.0, 35.0), radius=25.0, psides=48, fillpattern=pattern),
        ),
        (
            "Concave polygon",
            PolyLike(
                points=[
                    (10.0, 10.0),
                    (80.0, 10.0),
                    (80.0, 30.0),
                    (50.0, 30.0),
                    (50.0, 60.0),
                    (80.0, 60.0),
                    (80.0, 80.0),
                    (10.0, 80.0),
                ]
            ),
        ),
    ]

    fig, axes = plt.subplots(1, len(shapes), figsize=(5.5 * len(shapes), 5.0), constrained_layout=True)
    if len(shapes) == 1:
        axes = [axes]

    for ax, (name, shp) in zip(axes, shapes):
        outline = shp.outline()  # type: ignore[attr-defined]
        hatch_segments = hatch_fill(shp, pattern)  # type: ignore[arg-type]

        _plot_polyline(ax, outline, color="black", linewidth=2.0)
        _plot_segments(ax, hatch_segments, color="tab:blue", linewidth=1.0)
        _plot_travel(ax, hatch_segments, color="tab:orange", linewidth=0.8, linestyle="--", alpha=0.7)

        ax.set_title(name)
        ax.set_aspect("equal", adjustable="box")
        ax.grid(True, linewidth=0.3, alpha=0.3)

    fig.suptitle(f"Hatch fill debug: angle={pattern.angle}°, spacing={pattern.spacing}, overscan={pattern.overscan}")
    plt.show()


if __name__ == "__main__":
    main()
