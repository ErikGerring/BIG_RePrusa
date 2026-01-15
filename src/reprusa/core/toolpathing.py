from __future__ import annotations

import math
from typing import List

from .model import Point, Stroke, Toolpath, Segment

def dist(a: Point, b: Point) -> float:
    """Euclidean distance between two points."""
    return math.hypot(b[0] - a[0], b[1] - a[1])

def optimisation_algorithm(algorithm: str, strokes: List[Stroke]) -> List[Stroke]:
    if algorithm == "None":
        return strokes
    elif algorithm == "Naive":
        return naive_optimisation(strokes)
    else:
        raise ValueError(f"Unknown optimisation algorithm: {algorithm}")
    
def naive_optimisation(strokes: List[Stroke]) -> List[Stroke]:
    """A naive optimisation that does searches for the next closest stroke to continue from."""
    if not strokes:
        return []
    
    remaining = strokes.copy()
    ordered: List[Stroke] = []
    
    # Start from the first stroke
    current_stroke = remaining.pop(0)
    ordered.append(current_stroke)
    
    while remaining:
        last_point = current_stroke[-1]
        # Find the closest stroke
        closest_index = -1
        closest_distance = float('inf')

        reverse = False
        
        for i, stroke in enumerate(remaining):
            start_distance = dist(last_point, stroke[0])
            end_distance = dist(last_point, stroke[-1])
            if start_distance < closest_distance:
                closest_distance = start_distance
                closest_index = i
                reverse = False
            if end_distance < closest_distance:
                closest_distance = end_distance
                closest_index = i
                reverse = True
        
        # Append the closest stroke to the ordered list
        next_stroke = remaining.pop(closest_index)
        if reverse:
            next_stroke = list(reversed(next_stroke))
        
        ordered.append(next_stroke)
        current_stroke = next_stroke
    
    return ordered
        
def generate_toolpath(strokes: List[Stroke], optimisation: str) -> Toolpath:
    """Generate a toolpath from strokes with specified optimisation."""
    optimized_strokes = optimisation_algorithm(optimisation, strokes)
    
    segments: List[Segment] = []
    prev_end: Point | None = None

    for i, stroke in enumerate(optimized_strokes):
        if not stroke:
            continue

        start = stroke[0]
        end = stroke[-1]

        # Only travel if this stroke does not start where the last one ended
        if i == 0 or prev_end is None or start != prev_end:
            segments.append(Segment(kind="travel", points=[start]))

        # Draw the stroke
        segments.append(Segment(kind="draw", points=stroke))

        prev_end = end
    
    return Toolpath(segments=segments)