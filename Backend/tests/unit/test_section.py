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
    start_date = "2023-09-06"
    end_date = "2023-12-08"
    section = Section(course_code, section_id, crn, instructor, times, status, related_sections, start_date, end_date)
    assert section.to_dict() == {"CourseCode":course_code, "SectionID":section_id, "CRN":crn,
                                 "Instructor":instructor, "Times":times, "Status":status, "StartDate": start_date, "EndDate": end_date}