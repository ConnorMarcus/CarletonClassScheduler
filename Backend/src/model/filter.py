from __future__ import annotations
from .day_of_week import DayOfWeek


class Filter:
    before_time: str = None
    after_time: str = None
    day_of_week: DayOfWeek = None

    def __init__(self, **kwargs):
        if kwargs.get('before_time') and not isinstance(kwargs.get('before_time'), str):
            raise TypeError("before_time must be of type str")
        if kwargs.get('after_time') and not isinstance(kwargs.get('after_time'), str):
            raise TypeError("after_time must be of type str")
        if kwargs.get('day_of_week') and not isinstance(kwargs.get('day_of_week'), DayOfWeek):
            raise TypeError("day_of_week must be of type DayOfWeek")

        self.before_time = kwargs.get('before_time', None)
        self.after_time = kwargs.get('after_time', None)
        self.day_of_week = kwargs.get('day_of_week', None)

