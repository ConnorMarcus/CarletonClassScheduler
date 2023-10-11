from dataclasses import dataclass
from typing import List
from .date import Date

@dataclass
class Section:
    courseCode: str
    sectionId: str 
    crn: str
    instructor: str
    times: List[Date]
    status: str
    compatibleSectionIds: List[str]