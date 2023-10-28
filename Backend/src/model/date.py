from __future__ import annotations
from .day_of_week import DayOfWeek

class Date:

    def __init__(self, day: DayOfWeek, start_time: str, end_time: str) -> None:
        if not isinstance(day, DayOfWeek):
            raise TypeError("Parameter day must be of type DayOfWeek")
        if not (Date._are_times_valid(start_time, end_time)):
            raise ValueError("Parameters start time and end time must be in the following format: xx:xx. Also start time must come before end time")

        self.day = day
        self.start_time = start_time
        self.end_time = end_time

    @staticmethod
    def _is_valid_time(time: str) -> bool:
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
    def _are_times_valid(start_time: str, end_time: str) -> bool:
        return (
            Date._is_valid_time(start_time) and
            Date._is_valid_time(end_time) and
            Date.convert_time_to_float(start_time) < Date.convert_time_to_float(end_time)
        )
    
    @staticmethod
    def convert_time_to_float(time: str) -> float:
        if not Date._is_valid_time(time):
            raise ValueError("Invalid time cannot be converted to float representation.")
        return float(time[0:2]) + float(time[3:5]) / 100

    def does_date_overlap(self, other_date: Date) -> bool:
        if self.day != other_date.day:
            return False

        start_time_1, end_time_1 = Date.convert_time_to_float(self.start_time), Date.convert_time_to_float(self.end_time)
        start_time_2, end_time_2 = Date.convert_time_to_float(other_date.start_time), Date.convert_time_to_float(other_date.end_time)
        return (
            start_time_2 <= start_time_1 < end_time_2 or 
            start_time_2 < end_time_1 <= end_time_2 or
            start_time_1 <= start_time_2 < end_time_1 or 
            start_time_1 < end_time_2 <= end_time_1
        )
    
    def get_start_time_as_float(self) -> float:
        return Date.convert_time_to_float(self.start_time)
    
    def get_end_time_as_float(self) -> float:
        return Date.convert_time_to_float(self.end_time)
    
    def get_day_of_the_week(self) -> DayOfWeek:
        return self.day