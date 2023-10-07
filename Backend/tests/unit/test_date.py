import pytest
from Backend.src.model.date import Date
from Backend.src.model.dayOfWeek import DayOfWeek

def testValidDate():
    date = Date(DayOfWeek.Monday, "12:12", "14:31")
    assert date.day == DayOfWeek.Monday
    assert date.startTime == "12:12"
    assert date.endTime == "14:31"

def testInvalidDate():
    with pytest.raises(TypeError):
        Date("Monday", "21:00", "22:00")
    with pytest.raises(ValueError):
        Date(DayOfWeek.Friday, "25:00", "20:00")
    with pytest.raises(ValueError):
        Date(DayOfWeek.Monday, "21:00", "20:00:12")
    with pytest.raises(ValueError):
        Date(DayOfWeek.Tuesday, "21:00", "20:00")

def testIsValidTime():
    assert Date._isValidTime("123456") == False
    assert Date._isValidTime("34:12") == False
    assert Date._isValidTime("25:05") == False
    assert Date._isValidTime("12;01") == False
    assert Date._isValidTime("01:61") == False
    assert Date._isValidTime("12:3O") == False
    assert Date._isValidTime("12:34") == True

def testAreTimesValid():
    assert Date._areTimesValid("15:30", "12:45") == False
    assert Date._areTimesValid("11:23", "20:19") == True

def testConvertTimeToFloat():
    assert Date._convertTimeToFloat("22:19") == 22.19
    with pytest.raises(ValueError):
        Date._convertTimeToFloat("12345")

def testDoesDateOverlap():
    date = Date(DayOfWeek.Monday, "09:03", "12:54")
    assert date.doesDateOverlap(Date(DayOfWeek.Tuesday, "01:34", "10:17")) == False
    assert date.doesDateOverlap(Date(DayOfWeek.Monday, "07:33", "10:12")) == True
    assert date.doesDateOverlap(Date(DayOfWeek.Monday, "11:54", "14:22")) == True
    assert date.doesDateOverlap(Date(DayOfWeek.Monday, "09:03", "12:54")) == True
    assert date.doesDateOverlap(Date(DayOfWeek.Monday, "12:55", "18:59")) == False