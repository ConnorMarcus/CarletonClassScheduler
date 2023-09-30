from typing import List
from dataclasses import dataclass
from .course import Course

@dataclass
class Schedule:
    courses: List[Course]