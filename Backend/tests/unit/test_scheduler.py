import pytest
from Backend.src import scheduler
from Backend.src.model.section import Section
from Backend.src.model.course import Course
from Backend.src.model.date import ClassTime
from Backend.src.model.day_of_week import DayOfWeek
from Backend.src.model.term_duration import TermDuration

def test_is_section_schedulable():
    '''
    Tests that isSectionShedulable can handle overlaping classes and schedulable classes
    '''
    section1 = Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section2 = Section("CODE2000", "B", "22222", "Bob", [ClassTime(DayOfWeek.TUESDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section3 = Section("CODE3000", "C", "33333", "Charlie", [ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [], "2023-09-06", "2023-12-08")
    section4 = Section("CODE3000", "C", "33333", "Charlie", [], "", [], "2023-09-06", "2023-12-08")
    schedule = [
        Section("CODE4000", "D", "44444", "Dom", [ClassTime(DayOfWeek.MONDAY, TermDuration.EARLY_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.EARLY_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08"),
        Section("CODE5000", "E", "55555", "Eric", [ClassTime(DayOfWeek.MONDAY, TermDuration.LATE_TERM, "11:05", "12:35"), ClassTime(DayOfWeek.THURSDAY, TermDuration.LATE_TERM, "10:05", "11:35") ], "", [], "2023-09-06", "2023-12-08")
    ]
    assert scheduler.is_section_schedulable(section1, schedule) == False
    assert scheduler.is_section_schedulable(section2, schedule) == False
    assert scheduler.is_section_schedulable(section3, schedule) == True
    assert scheduler.is_section_schedulable(section4, schedule) == True


def test_are_sections_schedulable():
    section1 = Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section2 = Section("CODE2000", "B", "22222", "Bob", [ClassTime(DayOfWeek.TUESDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section3 = Section("CODE3000", "C", "33333", "Charlie", [ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [], "2023-09-06", "2023-12-08")
    section4 = Section("CODE3000", "C", "33333", "Charlie", [], "", [], "2023-09-06", "2023-12-08")
    schedule = [
        Section("CODE4000", "D", "44444", "Dom", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08"),
        Section("CODE5000", "E", "55555", "Eric", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "11:05", "12:35"), ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "10:05", "11:35") ], "", [], "2023-09-06", "2023-12-08")
    ]
    assert scheduler.are_sections_schedulable([section1, section2, section3, section4], schedule) == False
    assert scheduler.are_sections_schedulable([section4, section1], schedule) == False
    assert scheduler.are_sections_schedulable([section3], schedule) == True
    assert scheduler.are_sections_schedulable([section3, section4], schedule) == True

def test_do_section_times_overlap():
    section1 = Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section2 = Section("CODE2000", "B", "22222", "Bob", [ClassTime(DayOfWeek.TUESDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section3 = Section("CODE3000", "C", "33333", "Charlie", [ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [], "2023-09-06", "2023-12-08")
    section4 = Section("CODE3000", "C", "33333", "Charlie", [], "", [], "2023-09-06", "2023-12-08")
    assert scheduler.do_section_times_overlap([section1, section2]) == True
    assert scheduler.do_section_times_overlap([section1, section3, section4]) == False
    assert scheduler.do_section_times_overlap([section2, section3, section4]) == False
    assert scheduler.do_section_times_overlap([section1]) == False

def test_get_related_section_combinations():
    section1 = Section("CODE1000", "A", "11111", "Alice", [], "", [["B"], ["C", "D"]], "2023-09-06", "2023-12-08")
    section2 = Section("CODE2000", "B", "22222", "Bob", [], "", [], "2023-09-06", "2023-12-08")
    section3 = Section("CODE3000", "C", "33333", "Charlie", [], "", [], "2023-09-06", "2023-12-08")
    section4 = Section("CODE3000", "D", "33333", "Charlie", [], "", [], "2023-09-06", "2023-12-08")
    course = Course("", "", "", "", [section1], [section2, section3, section4], "")
    assert scheduler.get_related_section_combinations(course, section1) == [[section2, section3], [section2, section4]]

    section1.related_section_ids = [["B", "C", "D"]]
    assert scheduler.get_related_section_combinations(course, section1) == [[section2], [section3], [section4]]

    section1.related_section_ids = [["B"], ["C"], ["D"]]
    assert scheduler.get_related_section_combinations(course, section1) == [[section2, section3, section4]]

    section1.related_section_ids = [["B", "C", "E"]]
    assert scheduler.get_related_section_combinations(course, section1) == [[section2], [section3], [None]]

    with pytest.raises(ValueError):    
        scheduler.get_related_section_combinations(None, section1)
    
    section1.related_section_ids = []
    with pytest.raises(ValueError):
        scheduler.get_related_section_combinations(course, section1)
    with pytest.raises(ValueError):    
        scheduler.get_related_section_combinations(course, None)



def test_can_take_together():
    '''
    Testing if a lecture and lab section are compatible to take together
    '''
    LECTURE_SECTION_ID = "A"
    LAB_SECTION_ID = "L01"
    lecture_section = Section("CODE1234", LECTURE_SECTION_ID, "54321", "Jill", [], "", [[LAB_SECTION_ID]], "2023-09-06", "2023-12-08")
    lab_section = Section("CODE1234", LAB_SECTION_ID, "54321", "Jill", [], "", [["Z", "Q"], [LECTURE_SECTION_ID]], "2023-09-06", "2023-12-08")
    assert scheduler.can_take_together(lecture_section, lab_section) == True
    lecture_section.related_section_ids.pop()
    assert scheduler.can_take_together(lecture_section, lab_section) == False
    assert scheduler.can_take_together(lab_section, lecture_section) == True


def test_generate_schedules_with_no_courses():
    '''
    Tests that generateSchedules function can handle empty courses list
    '''
    schedule = [
        Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    ]
    assert scheduler.generate_schedules([], schedule) == [schedule]

def test_generate_schedules_with_max_schedules():
    '''
    Tests that generateSchedules function terminates when it reaches the max amount of schedules
    '''
    max_schedules = scheduler.MAX_SCHEDULES
    scheduler.MAX_SCHEDULES = 1
    section1 = Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [["L"]], "2023-09-06", "2023-12-08")
    section2 = Section("CODE1000", "B", "12345", "Alice", [ClassTime(DayOfWeek.TUESDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [["L"]], "2023-09-06", "2023-12-08")
    sectionL = Section("CODE1000", "L", "12345", "Alice", [ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "19:05", "20:35")], "", [["A", "B"]], "2023-09-06", "2023-12-08")
    course1 = Course("CODE1000", "TESTCLASS", "Fall 2023", "NONE", [section1, section2], [sectionL], None)
    schedule = [
        section1,
        sectionL
    ]
    assert scheduler.generate_schedules([course1], []) == [schedule]
    scheduler.MAX_SCHEDULES = max_schedules # reset constant


def test_generate_schedules_with_lab_sections():
    '''
    Tests that the generateSchedules function can schedule courses with lab sections
    '''
    section1 = Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [["L1", "L2"]], "2023-09-06", "2023-12-08")
    section2A = Section("CODE1000", "L1", "12345", "Alice", [ClassTime(DayOfWeek.TUESDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [["A"]], "2023-09-06", "2023-12-08")
    section2B = Section("CODE1000", "L2", "12345", "Alice", [ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "19:05", "20:35")], "", [["A"]], "2023-09-06", "2023-12-08")
    section3 = Section("CODE4000", "D", "44444", "Dom", [ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section4 = Section("CODE5000", "E", "55555", "Eric", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "11:05", "12:35"), ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "12:05", "13:35") ], "", [], "2023-09-06", "2023-12-08")
    course1 = Course("CODE1000", "TESTCLASS", "Fall 2023", "NONE", [section1], [section2A, section2B], None)
    schedule1 = [
        section3, section4
    ]
    expected_schedule1 = [
       section3, section4, section1, section2A
    ]
    expected_schedule2 = [
       section3, section4, section1, section2B
    ]
    assert scheduler.generate_schedules([course1], schedule1) == [expected_schedule1, expected_schedule2]


def test_generate_schedules_without_lab_sections():
    '''
    Test that the generateSchedules function can schedule courses without lab section
    '''
    section1 = Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section2 = Section("CODE4000", "D", "44444", "Dom", [ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section3 = Section("CODE5000", "E", "55555", "Eric", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "11:05", "12:35"), ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "12:05", "13:35") ], "", [], "2023-09-06", "2023-12-08")
    course1 = Course("CODE1000", "TESTCLASS", "Fall 2023", "NONE", [section1], [], None)
    schedule1 = [
        section2, section3
    ]
    expected_schedule = [
        section2,
        section3,
        section1
    ]
    assert scheduler.generate_schedules([course1], schedule1) == [expected_schedule]

def test_generate_schedules_with_incompatible_lab():
    '''
    Tests the generateSchedules function with incomptible lecture/lab sections
    '''
    section1 = Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [["A1"]], "2023-09-06", "2023-12-08")
    section2 = Section("CODE1000", "A1", "12345", "Alice", [ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [["A"]], "2023-09-06", "2023-12-08")
    section3 = Section("CODE1000", "B1", "44444", "Dom", [ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [["B"]], "2023-09-06", "2023-12-08")
    course1 = Course("CODE1000", "TESTCLASS", "Fall 2023", "NONE", [section1], [section2, section3], None)
    expected_schedule = [
       section1, section2
    ]
    assert scheduler.generate_schedules([course1]) == [expected_schedule]


def test_generate_schedules_with_unschedulable_section():
    '''
    Tests the generateSchedules function unschedulable lecture AND lab section
    '''
    section1 = Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.WEDNESDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [["L1"]], "2023-09-06", "2023-12-08")
    section2 = Section("CODE1000", "L1", "12345", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "11:05", "13:55")], "", [["A"]], "2023-09-06", "2023-12-08")
    section3 = Section("CODE4000", "D", "44444", "Dom", [ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "12:05", "13:35"), ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section4 = Section("CODE5000", "E", "55555", "Eric", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "11:05", "12:35"), ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "12:05", "13:35") ], "", [], "2023-09-06", "2023-12-08")
    course1 = Course("CODE1000", "TESTCLASS", "Fall 2023", "NONE", [section1], [section2], None)
    course2 = Course("CODE4000", "TESTCLASS2", "Fall 2023", "NONE", [section3], [], None)
    schedule1 = [
        section4
    ]
    assert scheduler.generate_schedules([course1], schedule1) == []
    assert scheduler.generate_schedules([course2], schedule1) == []

def test_generate_schedules_with_lab_and_tutorials():
    '''
    Tests that the generateSchedules function can schedule courses with lab sections and tutorial sections
    '''
    section1 = Section("CODE1000", "A", "11111", "Alice", [ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [["ETU"], ["L1", "L2"]], "2023-09-06", "2023-12-08")
    section2A = Section("CODE1000", "L1", "12345", "Alice", [ClassTime(DayOfWeek.TUESDAY, TermDuration.FULL_TERM, "09:05", "10:35")], "", [["A"]], "2023-09-06", "2023-12-08")
    section2B = Section("CODE1000", "L2", "12345", "Alice", [ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "19:05", "20:35")], "", [["A"]], "2023-09-06", "2023-12-08")
    section2C = Section("CODE1000", "ETU", "12345", "Alice", [ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "20:05", "21:35")], "", [["A"]], "2023-09-06", "2023-12-08")
    
    section3 = Section("CODE4000", "D", "44444", "Dom", [ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "09:05", "10:35"), ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "09:05", "10:35") ], "", [], "2023-09-06", "2023-12-08")
    section4 = Section("CODE4000", "E", "55555", "Eric", [ClassTime(DayOfWeek.THURSDAY, TermDuration.FULL_TERM, "12:05", "13:35") ], "", [], "2023-09-06", "2023-12-08")
    
    course1 = Course("CODE1000", "TESTCLASS", "Fall 2023", "NONE", [section1], [section2A, section2B, section2C], None)
    course2 = Course("CODE4000", "TESTCLASS", "Fall 2023", "NONE", [section3, section4], [], None)

    expected_schedule1 = [
       section3, section1, section2C, section2A
    ]
    expected_schedule2 = [
       section4, section1, section2C, section2A
    ]
    assert scheduler.generate_schedules([course1, course2]) == [expected_schedule1, expected_schedule2]
