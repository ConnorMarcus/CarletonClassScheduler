import pytest
from Backend.src.model.date import Date
from Backend.src.model.day_of_week import DayOfWeek

def testValidDate():
    date = Date(DayOfWeek.MONDAY, "12:12", "14:31")
    assert date.day == DayOfWeek.MONDAY
    assert date.start_time == "12:12"
    assert date.end_time == "14:31"

def testInvalidDate():
    with pytest.raises(TypeError):
        Date("Monday", "21:00", "22:00")
    with pytest.raises(ValueError):
        Date(DayOfWeek.FRIDAY, "25:00", "20:00")
    with pytest.raises(ValueError):
        Date(DayOfWeek.MONDAY, "21:00", "20:00:12")
    with pytest.raises(ValueError):
        Date(DayOfWeek.TUESDAY, "21:00", "20:00")

def testIsValidTime():
    assert Date._is_valid_time("123456") == False
    assert Date._is_valid_time("34:12") == False
    assert Date._is_valid_time("25:05") == False
    assert Date._is_valid_time("12;01") == False
    assert Date._is_valid_time("01:61") == False
    assert Date._is_valid_time("12:3O") == False
    assert Date._is_valid_time("12:34") == True

def testAreTimesValid():
    assert Date._are_times_valid("15:30", "12:45") == False
    assert Date._are_times_valid("11:23", "20:19") == True

def testConvertTimeToFloat():
    assert Date.convert_time_to_float("22:19") == 22.19
    with pytest.raises(ValueError):
        Date.convert_time_to_float("12345")

def testDoesDateOverlap():
    date = Date(DayOfWeek.MONDAY, "09:03", "12:54")
    assert date.does_date_overlap(Date(DayOfWeek.TUESDAY, "01:34", "10:17")) == False
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "07:33", "10:12")) == True
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "11:54", "14:22")) == True
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "09:03", "12:54")) == True
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "09:03", "12:00")) == True
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "09:03", "12:58")) == True
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "10:00", "12:54")) == True
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "08:00", "12:54")) == True
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "12:54", "18:59")) == False
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "07:00", "09:03")) == False
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "12:58", "18:59")) == False
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "07:00", "09:00")) == False
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "10:00", "11:00")) == True
    assert date.does_date_overlap(Date(DayOfWeek.MONDAY, "07:00", "14:00")) == True

def test_get_start_time_as_float():
    assert Date(DayOfWeek.MONDAY, "09:03", "12:54").get_start_time_as_float() == 9.03

def test_get_end_time_as_float():
    assert Date(DayOfWeek.MONDAY, "09:03", "12:54").get_end_time_as_float() == 12.54