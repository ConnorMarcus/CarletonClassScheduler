from typing import List
from dataclasses import dataclass
from Backend.model.course import Course

@dataclass
class Schedule:
    courses: List[Course]