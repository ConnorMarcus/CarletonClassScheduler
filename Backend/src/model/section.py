from dataclasses import dataclass
from typing import List
from .date import Date

@dataclass
class Section:
    section: str 
    crn: str
    instructor: str
    times: List[str]
    status: str