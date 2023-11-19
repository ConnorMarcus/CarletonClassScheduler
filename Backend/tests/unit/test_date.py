import pytest
from Backend.src.model.date import ClassTime
from Backend.src.model.day_of_week import DayOfWeek
from Backend.src.model.term_duration import TermDuration

def testValidDate():
    date = ClassTime(DayOfWeek.MONDAY, TermDuration.EARLY_TERM, "12:12", "14:31")
    assert date.day == DayOfWeek.MONDAY
    assert date.term_duration == TermDuration.EARLY_TERM
    assert date.start_time == "12:12"
    assert date.end_time == "14:31"

def testInvalidDate():
    with pytest.raises(TypeError):
        ClassTime("Monday", TermDuration.FULL_TERM, "21:00", "22:00")
    with pytest.raises(TypeError):
        ClassTime(DayOfWeek.FRIDAY, "Full term", "21:00", "22:00")
    with pytest.raises(ValueError):
        ClassTime(DayOfWeek.FRIDAY, TermDuration.FULL_TERM, "25:00", "20:00")
    with pytest.raises(ValueError):
        ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "21:00", "20:00:12")
    with pytest.raises(ValueError):
        ClassTime(DayOfWeek.TUESDAY, TermDuration.FULL_TERM, "21:00", "20:00")

def testIsValidTime():
    assert ClassTime._is_valid_time("123456") == False
    assert ClassTime._is_valid_time("34:12") == False
    assert ClassTime._is_valid_time("25:05") == False
    assert ClassTime._is_valid_time("12;01") == False
    assert ClassTime._is_valid_time("01:61") == False
    assert ClassTime._is_valid_time("12:3O") == False
    assert ClassTime._is_valid_time("12:34") == True

def testAreTimesValid():
    assert ClassTime._are_times_valid("15:30", "12:45") == False
    assert ClassTime._are_times_valid("11:23", "20:19") == True

def testConvertTimeToFloat():
    assert ClassTime.convert_time_to_float("22:19") == 22.19
    with pytest.raises(ValueError):
        ClassTime.convert_time_to_float("12345")

def testDoesDateOverlap():
    date = ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:03", "12:54")
    assert date.does_date_overlap(ClassTime(DayOfWeek.TUESDAY, TermDuration.FULL_TERM, "01:34", "10:17")) == False
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.EARLY_TERM, "07:33", "10:12")) == True
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.LATE_TERM, "11:54", "14:22")) == True
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:03", "12:54")) == True
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:03", "12:00")) == True
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:03", "12:58")) == True
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "10:00", "12:54")) == True
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "08:00", "12:54")) == True
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "12:54", "18:59")) == False
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "07:00", "09:03")) == False
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "12:58", "18:59")) == False
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "07:00", "09:00")) == False
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "10:00", "11:00")) == True
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "07:00", "14:00")) == True
    date.term_duration = TermDuration.EARLY_TERM
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.LATE_TERM, "09:03", "12:54")) == False
    date.term_duration = TermDuration.LATE_TERM
    assert date.does_date_overlap(ClassTime(DayOfWeek.MONDAY, TermDuration.EARLY_TERM, "09:03", "12:54")) == False

def test_get_start_time_as_float():
    assert ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:03", "12:54").get_start_time_as_float() == 9.03

def test_get_end_time_as_float():
    assert ClassTime(DayOfWeek.MONDAY, TermDuration.FULL_TERM, "09:03", "12:54").get_end_time_as_float() == 12.54

def test_str():
    day = DayOfWeek.MONDAY
    duration = TermDuration.FULL_TERM
    start_time, end_time = "09:00", "12:00"
    assert ClassTime(day, duration, start_time, end_time).__str__() == f"DayOfWeek: {day}, term duration: {duration}, start time: {start_time}, end time: {end_time}"

def test_repr():
    day = DayOfWeek.MONDAY
    duration = TermDuration.FULL_TERM
    start_time, end_time = "09:00", "12:00"
    assert ClassTime(day, duration, start_time, end_time).__repr__() == f"ClassTime<DayOfWeek: {day}, term duration: {duration}, start time: {start_time}, end time: {end_time}>"

def test_to_dict():
    day = DayOfWeek.MONDAY
    duration = TermDuration.FULL_TERM
    start_time, end_time = "09:00", "12:00"
    assert ClassTime(day, duration, start_time, end_time).to_dict() == {"DayOfWeek":day.value, "TermDuration":duration.value, "StartTime":start_time, "EndTime":end_time}