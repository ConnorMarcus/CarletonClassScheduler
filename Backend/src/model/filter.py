from __future__ import annotations
from typing import List
from .day_of_week import DayOfWeek
from .date import ClassTime


class Filter:
    before_time: str = None
    after_time: str = None
    day_of_week: DayOfWeek = None
    between_times: List[ClassTime] = []

    def __init__(self, **kwargs):
        if kwargs.get('before_time') and not isinstance(kwargs.get('before_time'), str):
            raise TypeError("before_time must be of type str")
        if kwargs.get('after_time') and not isinstance(kwargs.get('after_time'), str):
            raise TypeError("after_time must be of type str")
        if kwargs.get('day_of_week') and not isinstance(kwargs.get('day_of_week'), DayOfWeek):
            raise TypeError("day_of_week must be of type DayOfWeek")
        if kwargs.get('between_times') and not isinstance(kwargs.get('between_times'), list):
            raise TypeError("between_times must be of type list")
        if kwargs.get('between_times') and any(not isinstance(between_time, ClassTime) for between_time in kwargs.get('between_times')):
            raise TypeError("between_times cannot contain objects of type other than ClassTime")

        self.before_time = kwargs.get('before_time', None)
        self.after_time = kwargs.get('after_time', None)
        self.day_of_week = kwargs.get('day_of_week', None)
        self.between_times = kwargs.get('between_times', [])

