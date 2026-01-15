from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, List, Literal, Optional

from .model import Point, Stroke, Toolpath, Segment
from .toolpathing import generate_toolpath

GcodeUnit = Literal["mm", "in"]


@dataclass
class ToolProfile:
    """Editable per-tool profile for turning toolpaths into G-code.

    Keep machine/tool-specific behavior here (feedrates, tool on/off commands,
    Z lift strategy, and start/end blocks).
    """

    name: str = "default"

    # Motion settings
    travel_speed_mm_s: float = 80.0
    draw_speed_mm_s: float = 30.0

    # Toolpath optimisation
    opt_alg: str = "Naive"

    # Coordinate / formatting
    units: GcodeUnit = "mm"
    absolute: bool = True
    decimals: int = 3

    # Tool-state strategy (optional)
    # If provided, travel will use z_up and draw will use z_down.
    z_up: Optional[float] = None
    z_down: Optional[float] = None

    # Optional G-code snippets for toggling the tool (laser/plasma/relay/etc).
    tool_on_gcode: List[str] = field(default_factory=list)
    tool_off_gcode: List[str] = field(default_factory=list)

    # Optional pre/post blocks
    start_gcode: List[str] = field(default_factory=list)
    end_gcode: List[str] = field(default_factory=list)


def _mm_s_to_mm_min(v_mm_s: float) -> float:
    return float(v_mm_s) * 60.0


def _fmt(v: float, decimals: int) -> str:
    # Avoid scientific notation and keep output stable.
    return f"{v:.{decimals}f}"


def _emit(lines: List[str], block: Iterable[str]) -> None:
    for line in block:
        s = str(line).rstrip("\n")
        if s:
            lines.append(s)


def toolpath_to_gcode(toolpath: Toolpath, profile: ToolProfile) -> str:
    """Convert a Toolpath into a G-code program string."""

    lines: List[str] = []
    _emit(lines, profile.start_gcode)

    # Units / distance mode
    lines.append("G21" if profile.units == "mm" else "G20")
    lines.append("G90" if profile.absolute else "G91")

    current_feed_mm_min: Optional[float] = None
    tool_engaged: Optional[bool] = None

    def set_tool(engaged: bool) -> None:
        nonlocal tool_engaged
        if tool_engaged is engaged:
            return

        # Tool on/off via explicit snippets
        if engaged:
            _emit(lines, profile.tool_on_gcode)
        else:
            _emit(lines, profile.tool_off_gcode)

        # Tool on/off via Z-lift (if configured)
        if profile.z_up is not None and profile.z_down is not None:
            z = profile.z_down if engaged else profile.z_up
            lines.append(f"G0 Z{_fmt(z, profile.decimals)}")

        tool_engaged = engaged

    def set_feed(v_mm_min: float) -> str:
        nonlocal current_feed_mm_min
        if current_feed_mm_min is None or abs(current_feed_mm_min - v_mm_min) > 1e-9:
            current_feed_mm_min = v_mm_min
            return f" F{_fmt(v_mm_min, profile.decimals)}"
        return ""

    travel_feed = _mm_s_to_mm_min(profile.travel_speed_mm_s)
    draw_feed = _mm_s_to_mm_min(profile.draw_speed_mm_s)

    for seg in toolpath.segments:
        if not seg.points:
            continue

        if seg.kind == "travel":
            set_tool(False)
            feed_suffix = set_feed(travel_feed)
            # Travel segments are typically a single destination point.
            for (x, y) in seg.points:
                lines.append(
                    f"G0 X{_fmt(x, profile.decimals)} Y{_fmt(y, profile.decimals)}{feed_suffix}"
                )
                feed_suffix = ""  # only once per segment

        elif seg.kind == "draw":
            set_tool(True)
            feed_suffix = set_feed(draw_feed)
            # Emit a continuous polyline.
            for (x, y) in seg.points:
                lines.append(
                    f"G1 X{_fmt(x, profile.decimals)} Y{_fmt(y, profile.decimals)}{feed_suffix}"
                )
                feed_suffix = ""

        else:
            raise ValueError(f"Unknown Segment.kind: {seg.kind!r}")

    # Ensure tool is off at end.
    set_tool(False)
    _emit(lines, profile.end_gcode)

    return "\n".join(lines) + "\n"


def strokes_to_gcode(strokes: List[Stroke], profile: ToolProfile) -> str:
    """Convenience: strokes -> toolpath (optimised) -> G-code."""
    toolpath = generate_toolpath(strokes, optimisation=profile.opt_alg)
    return toolpath_to_gcode(toolpath, profile)

