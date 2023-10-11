from dataclasses import dataclass
from typing import List
from .section import Section

@dataclass
class Course:
    name: str
    title: str
    term: str
    prerequisite: str
    lectureSections: List[Section]
    labSections: List[Section]

