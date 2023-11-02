import pytest
from Backend.src.model.date import Date
from Backend.src.model.day_of_week import DayOfWeek
from Backend.src.model.section import Section
from Backend.src.model.course import Course
from Backend.src.model.filter import Filter

def test_filter_before_time():
    section1 = Section("CODE1000", "A", "11111", "JON", [Date(DayOfWeek.MONDAY, "09:00", "12:00")], "OPEN", [])
    section2 = Section("CODE1000", "B", "22222", " JON", [Date(DayOfWeek.TUESDAY, "15:00", "18:00")], "OPEN", []) 
    course = Course("CODE1000", "CLASS NAME", "FALL", "N/A", [section1, section2], [], "B")

    course.filter_before_time("13:00")
    assert course.lecture_sections == [section2]

    #test error case
    with pytest.raises(TypeError):
        course.filter_before_time(12.00)

def test_filter_after_time():
    section1 = Section("CODE1000", "A", "11111", "JON", [Date(DayOfWeek.MONDAY, "09:00", "12:00")], "OPEN", [])
    section2 = Section("CODE1000", "B", "22222", " JON", [Date(DayOfWeek.TUESDAY, "15:00", "18:00")], "OPEN", []) 
    course = Course("CODE1000", "CLASS NAME", "FALL", "N/A", [section1, section2], [], "B")

    course.filter_after_time("13:00")
    assert course.lecture_sections == [section1]

    #test error case
    with pytest.raises(TypeError):
        course.filter_after_time(10)

def test_filter_day_off():
    section1 = Section("CODE1000", "A", "11111", "JON", [Date(DayOfWeek.MONDAY, "09:00", "12:00")], "OPEN", [])
    section2 = Section("CODE1000", "B", "22222", " JON", [Date(DayOfWeek.TUESDAY, "09:00", "12:00")], "OPEN", []) 
    course = Course("CODE1000", "CLASS NAME", "FALL", "N/A", [section1, section2], [], "B")

    course.filter_day_off(DayOfWeek.MONDAY)
    assert course.lecture_sections == [section2]

    #test error case
    with pytest.raises(TypeError):
        course.filter_day_off("MONDAY")


def test_filter_by_section():
    section1 = Section("CODE1000", "A", "11111", "JON", [Date(DayOfWeek.MONDAY, "09:00", "12:00")], "OPEN", [])
    section2 = Section("CODE1000", "B", "22222", "JON", [Date(DayOfWeek.TUESDAY, "09:00", "12:00")], "OPEN", [])
    course = Course("CODE1000", "CLASS NAME", "FALL", "N/A", [section1, section2], [], "B")

    course.filter_by_section()
    assert course.lecture_sections == [section2]

    #test error case
    with pytest.raises(TypeError):
        course.section_id_filter = None
        course.filter_by_section()

def test_filter_all_courses():
    section1 = Section("CODE1000", "A", "11111", "JON", [Date(DayOfWeek.MONDAY, "09:00", "12:00")], "OPEN", [])
    section2 = Section("CODE1000", "B", "22222", "JON", [Date(DayOfWeek.TUESDAY, "09:00", "12:00")], "OPEN", [])
    section3 = Section("CODE2000", "A", "11111", "JON", [Date(DayOfWeek.WEDNESDAY, "07:00", "12:00")], "OPEN", [])
    section4 = Section("CODE2000", "B", "22222", "JON", [Date(DayOfWeek.FRIDAY, "09:00", "12:00")], "OPEN", [])
    course1 = Course("CODE1000", "CLASS NAME", "FALL", "N/A", [section1, section2], [], "B")
    course2 = Course("CODE2000", "CLASS NAME 2", "FALL", "N/A", [section3], [section4], None)
    filter = Filter(before_time = "08:00", day_of_week = DayOfWeek.MONDAY, after_time = "22:00")
    Course.filter_all_courses([course1, course2], filter)
    assert course1.lecture_sections == [section2]
    assert course2.lecture_sections == []
    assert course2.lab_sections == [section4]

    #test error case
    with pytest.raises(ValueError):
        Course.filter_all_courses([], None)
    

def test_filter():
    section1 = Section("CODE1000", "A", "11111", "JON", [Date(DayOfWeek.MONDAY, "09:00", "12:00")], "OPEN", [])
    section2 = Section("CODE1000", "B", "22222", "JON", [Date(DayOfWeek.TUESDAY, "09:00", "12:00")], "OPEN", [])
    course = Course("CODE1000", "CLASS NAME", "FALL", "N/A", [section1, section2], [], None)
    course.filter(Filter())
    assert course.lecture_sections == [section1, section2]

    #test error case
    with pytest.raises(TypeError):
        course.filter(None)
        
