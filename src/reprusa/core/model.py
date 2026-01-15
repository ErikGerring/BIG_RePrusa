# This module defines basic geometric data structures used in the RePrusa application.

from __future__ import annotations # This enables postponed evaluation of annotations, ie you can refer to the class 'Point' in another annotation before it is defined. This helps with forward references, and cyclic dependencies.

from dataclasses import dataclass # This is used to create data classes, which are classes primarily meant to store data with automatically added special methods like __init__ and __repr__.

from typing import List, Tuple

Point = Tuple[float, float]
Stroke = List[Point]

@dataclass(frozen=True) # The frozen=True parameter makes instances of this class immutable after creation.
class Bounds:
    min_x: float
    min_y: float
    max_x: float
    max_y: float

    def w(self) -> float:
        return self.max_x - self.min_x

    def h(self) -> float:
        return self.max_y - self.min_y
    
@dataclass(frozen=True)
class Segment:
    kind: str  # eg "travel" or "draw"
    points: Stroke

@dataclass(frozen=True)
class Toolpath:
    segments: List[Segment]