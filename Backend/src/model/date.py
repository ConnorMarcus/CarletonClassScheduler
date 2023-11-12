from __future__ import annotations
from .day_of_week import DayOfWeek
from .term_duration import TermDuration

class ClassTime:

    def __init__(self, day: DayOfWeek, term_duration: TermDuration, start_time: str, end_time: str):
        if not isinstance(day, DayOfWeek):
            raise TypeError("Parameter day must be of type DayOfWeek")
        if not isinstance(term_duration, TermDuration):
            raise TypeError("Parameter term_duration must be of type TermDuration")
        if not (ClassTime._are_times_valid(start_time, end_time)):
            raise ValueError("Parameters start time and end time must be in the following format: xx:xx. Also start time must come before end time")

        self.day = day
        self.term_duration = term_duration
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
            ClassTime._is_valid_time(start_time) and
            ClassTime._is_valid_time(end_time) and
            ClassTime.convert_time_to_float(start_time) < ClassTime.convert_time_to_float(end_time)
        )
    
    @staticmethod
    def convert_time_to_float(time: str) -> float:
        if not ClassTime._is_valid_time(time):
            raise ValueError("Invalid time cannot be converted to float representation.")
        return float(time[0:2]) + float(time[3:5]) / 100

    def does_date_overlap(self, other_date: ClassTime) -> bool:
        if ((self.day != other_date.day) or 
            (self.term_duration == TermDuration.EARLY_TERM and 
             other_date.term_duration == TermDuration.LATE_TERM) or 
            (self.term_duration == TermDuration.LATE_TERM and 
             other_date.term_duration == TermDuration.EARLY_TERM)):
            return False

        start_time_1, end_time_1 = ClassTime.convert_time_to_float(self.start_time), ClassTime.convert_time_to_float(self.end_time)
        start_time_2, end_time_2 = ClassTime.convert_time_to_float(other_date.start_time), ClassTime.convert_time_to_float(other_date.end_time)
        return (
            start_time_2 <= start_time_1 < end_time_2 or 
            start_time_2 < end_time_1 <= end_time_2 or
            start_time_1 <= start_time_2 < end_time_1 or 
            start_time_1 < end_time_2 <= end_time_1
        )
    
    def get_start_time_as_float(self) -> float:
        return ClassTime.convert_time_to_float(self.start_time)
    
    def get_end_time_as_float(self) -> float:
        return ClassTime.convert_time_to_float(self.end_time)
    
    def get_day_of_the_week(self) -> DayOfWeek:
        return self.day
    
    def __str__(self) -> str:
        return f"DayOfWeek: {self.day}, term duration: {self.term_duration}, start time: {self.start_time}, end time: {self.end_time}"
    
    def __repr__(self) -> str:
        return f"ClassTime<{self.__str__()}>"