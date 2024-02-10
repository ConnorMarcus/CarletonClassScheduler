from abc import ABC, abstractmethod
from typing import List, Set
from ..model.course import Course
from ..model.section import Section
from ..model.term_duration import TermDuration
from ..model.week_schedule import WeekSchedule
from ..model.day_of_week import DayOfWeek
from ..model.date import ClassTime

class CourseDatabase(ABC):
    region = 'us-east-1'
    title_column = "Title"
    term_column = "Term"
    subject_column = "Subject"
    prerequisite_column = "Prerequisite"
    lecture_sections_column = "LectureSections"
    lab_sections_column = "LabSections"
    crn_column = "CRN"
    also_register_column = "AlsoRegister"
    instructor_column = "Instructor"
    section_id_column = "SectionID"
    status_column = "Status"
    duration_column = "TermDuration"
    week_schedule_column = "WeekSchedule"
    meeting_dates_column = "MeetingDates"
    day_of_week_column = "DayOfWeek"
    start_time_column = "StartTime"
    end_time_column = "EndTime"
    start_date_column = "StartDate"
    end_date_column = "EndDate"

    @abstractmethod
    def get_resource(self):
        '''
        Gets the AWS resource used by the database
        '''

    @abstractmethod
    def get_course(self, course_code: str, term: str) -> Course | None:
        '''
        Gets the Course object associated with a given course code and term.
        Returns None if the course code does not exist for the given term.
        '''

    @abstractmethod
    def get_terms(self) -> List[str] | dict:
        '''
        Gets the dict or list of terms from the database.
        '''
    
    @abstractmethod
    def get_course_code_and_section_list(self, term: str) -> List[str]:
        '''
        Gets a list of the course codes and sections for a given term.
        '''

    def convert_to_course(self, course_map: dict) -> Course:
        subject = course_map.get(self.subject_column, "")
        title = course_map.get(self.title_column, "")
        term = course_map.get(self.term_column, "")
        prerequisite = course_map.get(self.prerequisite_column, "")
        lecture_section_list = course_map.get(self.lecture_sections_column, [])
        lecture_sections = [self.convert_to_section(subject, section_map) for section_map in lecture_section_list]
        lab_section_list = course_map.get(self.lab_sections_column, [])
        lab_sections = [self.convert_to_section(subject, section_map) for section_map in lab_section_list]

        return Course(subject, title, term, prerequisite, lecture_sections, lab_sections, None)
    
    def convert_to_section(self, course_code: str, section_map: dict) -> Section:
        section_id = section_map.get(self.section_id_column, "")
        crn = section_map.get(self.crn_column, "")
        status = section_map.get(self.status_column, "")
        instructor = section_map.get(self.instructor_column, "")
        start_date = section_map.get(self.start_date_column, "")
        end_date = section_map.get(self.end_date_column, "")
        related_sections = section_map.get(self.also_register_column, [])
        term_duration = TermDuration(section_map.get(self.duration_column))
        week_schedule = WeekSchedule(section_map.get(self.week_schedule_column, WeekSchedule.EVERY_WEEK))
        meeting_dates_list = section_map.get(self.meeting_dates_column, [])
        meeting_times = [self.convert_to_classtime(term_duration, meeting_date_map, week_schedule) for meeting_date_map in meeting_dates_list]
        return Section(course_code, section_id, crn, instructor, meeting_times, status, related_sections, start_date, end_date)

    def convert_to_classtime(self, term_duration: TermDuration, meeting_date_map: dict, week_schedule: WeekSchedule) -> ClassTime:
        day_of_week = DayOfWeek(meeting_date_map.get(self.day_of_week_column))
        start_time = meeting_date_map.get(self.start_time_column)
        end_time = meeting_date_map.get(self.end_time_column)
        return ClassTime(day_of_week, term_duration, start_time, end_time, week_schedule)
