from dataclasses import dataclass
from .section import Section

@dataclass
class Course:
    name: str
    title: str
    term: str
    prerequisite: str
    lectureSection: [Section]
    labSection: [Section]

