from dataclasses import dataclass
from typing import List
from .date import ClassTime

@dataclass
class Section:
    course_code: str
    section_id: str 
    crn: str
    instructor: str
    times: List[ClassTime]
    status: str
    related_section_ids: List[List[str]] # Section IDs that must registered in with the given section 
                                         # i.e. [["ETU"], ["L1", "L2"]] would represent ETU and (L1 or L2)
    start_date: str
    end_date: str

    def to_dict(self) -> dict:
        return {"CourseCode":self.course_code, "SectionID":self.section_id, "CRN":self.crn, 
                "Instructor":self.instructor, "Times":[time.to_dict() for time in self.times],
                "Status":self.status, "StartDate": self.start_date, "EndDate": self.end_date}