from dataclasses import dataclass
from typing import List
from .date import Date

@dataclass
class Section:
    course_code: str
    section_id: str 
    crn: str
    instructor: str
    times: List[Date]
    status: str
    related_section_ids: List[List[str]] # Section IDs that must registered in with the given section 
                                         # i.e. [["ETU"], ["L1", "L2"]] would represent ETU and (L1 or L2)