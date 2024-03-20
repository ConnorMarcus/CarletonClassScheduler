import pytest
from Backend.src.model.section import Section

def test_to_dict():
    course_code = "CODE"
    section_id = "A"
    crn = "1234"
    instructor = "Professor X"
    times = []
    status = "OPEN"
    title = "COURSE TITLE"
    term = "Fall 2023"
    prerequisite = "None"
    related_sections = []
    start_date = "2023-09-06"
    end_date = "2023-12-08"
    section_type = "Online"
    section = Section(course_code, section_id, crn, instructor, times, status, title, term, prerequisite, related_sections, start_date, end_date, section_type)
    assert section.to_dict() == {"CourseCode":course_code, "SectionID":section_id, "CRN":crn,
                                 "Instructor":instructor, "Times":times, "Status":status, 
                                 "StartDate": start_date, "EndDate": end_date, "Title": title,
                                 "Term": term, "Prerequisite": prerequisite, "SectionType": section_type}