import pytest
from Backend.src.model.section import Section

def test_to_dict():
    course_code = "CODE"
    section_id = "A"
    crn = "1234"
    instructor = "Professor X"
    times = []
    status = "OPEN"
    related_sections = []
    section = Section(course_code, section_id, crn, instructor, times, status, related_sections)
    assert section.to_dict() == {"CourseCode":course_code, "SectionID":section_id, "CRN":crn,
                                 "Instructor":instructor, "Times":times, "Status":status}