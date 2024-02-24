from .database import CourseDatabase
from ..model.term_duration import TermDuration
from ..model.week_schedule import WeekSchedule

class CouresDatabaseException(Exception):
    pass

class ErrorCourseDatabase(CourseDatabase):
    '''
    Class used to simply throw an exception whenever the CourseDatabase could not be 
    established and one of the database methods is invoked.
    '''

    def exception(self):
        raise CouresDatabaseException("The CourseDatabase does not exist or it could not be connected to!")

    def get_resource(self):
       self.exception()

    def get_course(self, course_code: str, term: str):
        self.exception()

    def get_terms(self):
        self.exception()
    
    def get_course_code_and_section_list(self, term: str):
        self.exception()

    def convert_to_course(self, course_map: dict):
        self.exception()
    
    def convert_to_section(self, course_code: str, section_map: dict):
        self.exception()
        
    def convert_to_classtime(self, term_duration: TermDuration, meeting_date_map: dict, week_schedule: WeekSchedule):
        self.exception()