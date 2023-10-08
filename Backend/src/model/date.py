from __future__ import annotations
from .dayOfWeek import DayOfWeek

class Date:

    def __init__(self, day: DayOfWeek, startTime: str, endTime: str) -> None:
        if not isinstance(day, DayOfWeek):
            raise TypeError("Parameter day must be of type DayOfWeek")
        if not (self._areTimesValid(startTime, endTime)):
            raise ValueError("Parameters start time and end time must be in the following format: xx:xx. Also start time must come before end time")

        self.day = day
        self.startTime = startTime
        self.endTime = endTime

    @staticmethod
    def _isValidTime(time: str) -> bool:
        if len(time) != 5:
            return False
        
        char1, char2, char3, char4, char5 = time[0], time[1], time[2], time[3], time[4]
        return ( 
            char1.isdigit() and 0 <= int(char1) <= 2 and
            char2.isdigit() and (char1 == '0' or char1 == '1' or 0 <= int(char2) <= 3) and
            char3 == ':' and
            char4.isdigit() and 0 <= int(char4) <= 5 and
            char5.isdigit()
            )

    @staticmethod    
    def _areTimesValid(startTime: str, endTime: str) -> bool:
        return (
            Date._isValidTime(startTime) and
            Date._isValidTime(endTime) and
            Date._convertTimeToFloat(startTime) < Date._convertTimeToFloat(endTime)
        )
    
    @staticmethod
    def _convertTimeToFloat(time: str) -> float:
        if not Date._isValidTime(time):
            raise ValueError("Invalid time cannot be converted to float representation.")
        return float(time[0:2]) + float(time[3:5]) / 100

    def doesDateOverlap(self, otherDate: Date) -> bool:
        if self.day != otherDate.day:
            return False

        startTime1, endTime1 = Date._convertTimeToFloat(self.startTime), Date._convertTimeToFloat(self.endTime)
        startTime2, endTime2 = Date._convertTimeToFloat(otherDate.startTime), Date._convertTimeToFloat(otherDate.endTime)
        return (
            startTime2 <= startTime1 < endTime2 or 
            startTime2 < endTime1 <= endTime2 or
            startTime1 <= startTime2 < endTime1 or 
            startTime1 < endTime2 <= endTime1
        )