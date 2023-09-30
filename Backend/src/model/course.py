from dataclasses import dataclass
from typing import List

@dataclass
class Course:
    name: str
    section: str
    crn: str
    times: List[str] #TODO: change to list of day-time objects