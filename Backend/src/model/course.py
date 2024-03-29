from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, List
from .section import Section
from .date import ClassTime
from .day_of_week import DayOfWeek
from .filter import Filter
from ..logger import logger

@dataclass
class Course:
    code: str
    title: str
    term: str
    prerequisite: str
    lecture_sections: List[Section]
    lab_sections: List[Section]
    section_id_filter: str

    @staticmethod
    def filter_all_courses(courses: List[Course], filter: Filter):
        if filter is None:
            raise ValueError("Parameter 'filter' cannot be None!")

        for course in courses:
            course.filter(filter)

    @staticmethod
    def time_filter(sections: List[Section], compare_function: Callable[[ClassTime], bool]) -> None:
        i = 0
        while i < len(sections):
            removed_section = False
            for date in sections[i].times:
                if compare_function(date):
                    del sections[i]
                    removed_section = True
                    break
                
            if not removed_section:
                i += 1

    def filter(self, filter: Filter) -> None:
        if not isinstance(filter, Filter):
            raise TypeError("Parameter 'filter' must be of type Filter")

        if filter.before_time:
            self.filter_before_time(filter.before_time)
        
        if filter.after_time:
            self.filter_after_time(filter.after_time)

        if filter.day_of_week:
            self.filter_day_off(filter.day_of_week)

        if filter.between_times:
            self.filter_between_times(filter.between_times)
        
        if self.section_id_filter:
            self.filter_by_section()

    def filter_before_time(self, time: str) -> None:
        '''
        Filter out all sections that take place before filter time
        '''
        if not isinstance(time, str):
            raise TypeError("Parameter 'time' must be of type str")
        
        def compare_function(date: ClassTime):
            return date.get_start_time_as_float() < ClassTime.convert_time_to_float(time)

        Course.time_filter(self.lecture_sections, compare_function)
        Course.time_filter(self.lab_sections, compare_function)       



    def filter_after_time(self, time: str) -> None:
        '''
        Filter out all sections that take place after filter time
        '''
        if not isinstance(time, str):
            raise TypeError("Parameter 'time' must be of type str")
        
        def compare_function(date: ClassTime):
            return date.get_end_time_as_float() > ClassTime.convert_time_to_float(time)

        Course.time_filter(self.lecture_sections, compare_function)
        Course.time_filter(self.lab_sections, compare_function) 
                

    def filter_day_off(self, day_of_week: DayOfWeek) -> None:
        '''
        Filter out all courses that take place on day_of_week
        '''
        if not isinstance(day_of_week, DayOfWeek):
            raise TypeError("Parameter 'day_of_week' must be of type DayOfWeek")

        def compare_function(date: ClassTime):
            return date.get_day_of_the_week() == day_of_week

        Course.time_filter(self.lecture_sections, compare_function)
        Course.time_filter(self.lab_sections, compare_function)

    def filter_between_times(self, between_times: List[ClassTime]) -> None:
        '''
        Filter out all sections that take place between a list of times
        '''
        if not isinstance(between_times, list):
            raise TypeError("Parameter 'between_times' must be of type list")
        
        for between_time in between_times:
            def compare_function(date: ClassTime):
                return date.does_date_overlap(between_time)

            Course.time_filter(self.lecture_sections, compare_function)
            Course.time_filter(self.lab_sections, compare_function) 

    def filter_by_section(self):
        if not isinstance(self.section_id_filter, str):
            raise TypeError("Attribute 'section_id_filter' must be of type str")

        sections = self.lecture_sections
        i = 0
        while i < len(sections):
            if sections[i].section_id != self.section_id_filter:
                del sections[i]
            else:
                i += 1

    def get_lecture_section(self, id: str) -> Section:
        '''
        Returns the first lecture Section object with the given ID.
        '''
        for section in self.lecture_sections:
            if section.section_id == id:
                return section
            
        logger.info(f"No Lecture Section with id {id} exists (Section may have been filtered out)")
        return None

    def get_lab_section(self, id: str) -> Section:
        '''
        Returns the first lab Section object with the given ID.
        '''
        for section in self.lab_sections:
            if section.section_id == id:
                return section
            
        logger.info(f"No Lab Section with id {id} exists (Section may have been filtered out)")
        return None

