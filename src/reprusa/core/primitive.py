from __future__ import annotations

from dataclasses import dataclass
import math
from typing import List, Literal, Union

from .model import Point, Stroke, Bounds

GeometryKind = Literal["circle", "rectangle"]
PatternKind = Literal["none", "hatch", "crosshatch"]


@dataclass
class CircleGeometry:
    center: Point
    radius: float
    # Used only for polyline approximation (for plotting / hatch clipping)
    psides: int = 48

    def bounds(self) -> Bounds:
        return Bounds(
            min_x=self.center[0] - self.radius,
            min_y=self.center[1] - self.radius,
            max_x=self.center[0] + self.radius,
            max_y=self.center[1] + self.radius,
        )

    def outline(self) -> Stroke:
        points: Stroke = []
        n = max(8, int(self.psides))
        for i in range(n):
            a = 2.0 * math.pi * i / n
            x = self.center[0] + self.radius * math.cos(a)
            y = self.center[1] + self.radius * math.sin(a)
            points.append((x, y))
        points.append(points[0])
        return points


@dataclass
class RectangleGeometry:
    bottom_left: Point
    width: float
    height: float

    def bounds(self) -> Bounds:
        x, y = self.bottom_left
        return Bounds(min_x=x, min_y=y, max_x=x + self.width, max_y=y + self.height)

    def outline(self) -> Stroke:
        x, y = self.bottom_left
        return [
            (x, y),
            (x + self.width, y),
            (x + self.width, y + self.height),
            (x, y + self.height),
            (x, y),
        ]


Geometry = Union[CircleGeometry, RectangleGeometry]


@dataclass
class none_pattern:
    """No fill pattern (placeholder for a richer pattern system)."""

    kind: PatternKind = "none"


@dataclass
class hatch_pattern:
    """Hatch pattern settings.

    Kept compatible with `hatch_fill_ai()` which expects `angle`, `spacing`, `overscan`.
    """

    angle: float
    spacing: float
    overscan: float
    kind: PatternKind = "hatch"


@dataclass
class crosshatch_pattern:
    """Two-pass hatch fill.

    This is intentionally modeled so rendering can call `hatch_fill()` twice
    using two derived `hatch_pattern` settings.

    - Pass 1 uses (angle, spacing, overscan)
    - Pass 2 uses angle2 = angle + angle_offset, and (spacing2, overscan2)
    """

    angle: float
    spacing: float
    overscan: float

    angle_offset: float = 90.0
    spacing2: float | None = None
    overscan2: float | None = None
    kind: PatternKind = "crosshatch"

    def hatch1(self) -> hatch_pattern:
        return hatch_pattern(angle=self.angle, spacing=self.spacing, overscan=self.overscan)

    def hatch2(self) -> hatch_pattern:
        return hatch_pattern(
            angle=self.angle_offset,
            spacing=self.spacing if self.spacing2 is None else float(self.spacing2),
            overscan=self.overscan if self.overscan2 is None else float(self.overscan2),
        )


Pattern = Union[none_pattern, hatch_pattern, crosshatch_pattern]


class Shape:
    """Mutable, configurable shape container.

    This is designed for easy experimentation:
    - You can change geometry type (circle/rectangle) by assigning `geometry`.
    - You can change fill pattern + its settings by assigning `fillpattern`.
    """

    def __init__(
        self,
        geometry: Geometry,
        *,
        fillpattern: Pattern | None = None,
        perimeter: Stroke | None = None,
    ) -> None:
        self.geometry: Geometry = geometry
        self.fillpattern: Pattern | None = fillpattern
        self.perimeter: Stroke | None = perimeter

    @property
    def kind(self) -> GeometryKind:
        if isinstance(self.geometry, CircleGeometry):
            return "circle"
        return "rectangle"

    def bounds(self) -> Bounds:
        return self.geometry.bounds()

    def outline(self) -> Stroke:
        if self.perimeter is not None:
            pts = self.perimeter
            if pts and pts[0] != pts[-1]:
                return list(pts) + [pts[0]]
            return list(pts)
        return self.geometry.outline()

    # Convenience constructors
    @staticmethod
    def circle(
        *,
        center: Point,
        radius: float,
        psides: int = 48,
        fillpattern: Pattern | None = None,
    ) -> "Shape":
        return Shape(CircleGeometry(center=center, radius=radius, psides=psides), fillpattern=fillpattern)

    @staticmethod
    def rectangle(
        *,
        bottom_left: Point,
        width: float,
        height: float,
        fillpattern: Pattern | None = None,
    ) -> "Shape":
        return Shape(RectangleGeometry(bottom_left=bottom_left, width=width, height=height), fillpattern=fillpattern)

    



# Backwards-compatible type name used by hatch_fill_ai.
shape = Shape

def rotate_point(point: Point, angle_degrees: float) -> Point:
    angle_radians = math.radians(angle_degrees)
    x, y = point
    x_rotated = x * math.cos(angle_radians) - y * math.sin(angle_radians)
    y_rotated = x * math.sin(angle_radians) + y * math.cos(angle_radians)
    return (x_rotated, y_rotated)


# def hatch_fill_ai(s: shape, pattern: hatch_pattern) -> List[Stroke]:
#     """Generate hatch-fill line segments for any polygonal outline.

#     This implements the standard approach:
#     1) get the shape outline as a *closed* polyline
#     2) rotate into "hatch space" so hatch lines become horizontal
#     3) for each scanline y=y0, intersect it with polygon edges
#     4) sort x-intersections and pair them using the even–odd fill rule
#     5) overscan along the hatch direction, then rotate segments back

#     Notes
#     - Concave polygons work naturally.
#     - Holes are not represented by the current `shape.outline()` API; if you
#       later represent holes as additional rings, you can extend this by adding
#       intersections from hole rings (still using even–odd parity).
#     - Return type is `List[Stroke]` because hatch fill naturally produces many
#       disjoint 2-point segments.
#     """

#     if pattern.spacing <= 0:
#         raise ValueError("pattern.spacing must be > 0")

#     outline = s.outline()
#     if not outline or len(outline) < 3:
#         return []

#     # Ensure closed polygon.
#     if outline[0] != outline[-1]:
#         outline = list(outline) + [outline[0]]

#     angle = float(pattern.angle)
#     overscan = float(pattern.overscan)
#     spacing = float(pattern.spacing)

#     # Rotate into hatch space: hatch lines become horizontal (y = const).
#     theta = math.radians(-angle)
#     c = math.cos(theta)
#     si = math.sin(theta)

#     def rot(p: Point) -> Point:
#         x, y = p
#         return (x * c - y * si, x * si + y * c)

#     def unrot(p: Point) -> Point:
#         # inverse rotation is +angle
#         x, y = p
#         return (x * c + y * si, -x * si + y * c)

#     poly = [rot(p) for p in outline]
#     ys = [p[1] for p in poly]
#     y_min = min(ys)
#     y_max = max(ys)

#     # Choose scanlines aligned to y=0 so the hatch phase is consistent.
#     k0 = math.floor(y_min / spacing)
#     y0 = k0 * spacing

#     eps = 1e-9
#     segments: List[Stroke] = []

#     # Iterate scanlines covering the polygon.
#     while y0 <= y_max + eps:
#         xs: List[float] = []

#         # Intersect scanline with each polygon edge.
#         for (x1, y1), (x2, y2) in zip(poly, poly[1:]):
#             # Skip horizontal edges; they don't contribute under the half-open rule.
#             if abs(y2 - y1) < eps:
#                 continue

#             # Half-open interval to avoid double-counting vertices:
#             # include intersections where y is in [min, max)
#             ymin = y1 if y1 < y2 else y2
#             ymax = y2 if y1 < y2 else y1
#             if y0 < ymin or y0 >= ymax:
#                 continue

#             t = (y0 - y1) / (y2 - y1)
#             x = x1 + t * (x2 - x1)
#             xs.append(x)

#         xs.sort()

#         # Pair intersections (even–odd fill rule) => inside segments.
#         for i in range(0, len(xs) - 1, 2):
#             x_start = xs[i]
#             x_end = xs[i + 1]
#             if x_end - x_start <= eps:
#                 continue

#             x_start -= overscan
#             x_end += overscan

#             p1 = unrot((x_start, y0))
#             p2 = unrot((x_end, y0))
#             segments.append([p1, p2])

#         y0 += spacing

#     return segments

def hatch_fill(shape: shape, pattern: hatch_pattern) -> List[Stroke]:
    if pattern.spacing <= 0:
        raise ValueError("pattern.spacing must be > 0")
    
    if pattern.overscan < 0: 
        raise ValueError("pattern.overscan must be >= 0")
    
    outline = shape.outline()
    if not outline or len(outline) < 3:
        return []
    
    segments: List[Stroke] = [] 
    
    # Ensure closed polygon.
    if outline[0] != outline[-1]:
        outline = list(outline) + [outline[0]]
    
    outline_rot = [rotate_point(p, pattern.angle) for p in outline]

    ys = [ps[1] for ps in outline_rot]
    y_min = min(ys)
    y_max = max(ys)

    y_cur = y_min - pattern.overscan

    while y_cur <= y_max + pattern.overscan:
        x_intersections = []

        for (x1, y1), (x2, y2) in zip(outline_rot, outline_rot[1:]):
            if abs(y2 - y1) < 1e-9:
                continue
            
            ymin = min(y1, y2)
            ymax = max(y1, y2)
            if y_cur < ymin or y_cur >= ymax:
                continue
            
            t = (y_cur - y1) / (y2 - y1)
            x_int = x1 + t * (x2 - x1)
            x_intersections.append(x_int)
        
        x_intersections.sort()

        for i in range(0, len(x_intersections) - 1, 2):
            x_start = x_intersections[i] - pattern.overscan
            x_end = x_intersections[i + 1] + pattern.overscan

            p1_rot = (x_start, y_cur)
            p2_rot = (x_end, y_cur)

            p1 = rotate_point(p1_rot, -pattern.angle)
            p2 = rotate_point(p2_rot, -pattern.angle)

            segments.append([p1, p2])
        
        y_cur += pattern.spacing

    return segments












    



