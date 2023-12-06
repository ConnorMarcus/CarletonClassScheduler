from typing import List, Set
import boto3
from boto3.dynamodb.types import TypeDeserializer
import os
from ..model.course import Course
from ..model.section import Section
from ..model.term_duration import TermDuration
from ..model.day_of_week import DayOfWeek
from ..model.date import ClassTime
from ..logger import logger

class Database:
    table_name = ''
    test_table_name = "carleton-courses-test"
    prod_table_name = "carleton-courses"
    region = 'us-east-1'
    resource = 'dynamodb'
    deserializer = TypeDeserializer()
    ITEMS_CONSTANT = "Items"
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
    meeting_dates_column = "MeetingDates"
    day_of_week_column = "DayOfWeek"
    start_time_column = "StartTime"
    end_time_column = "EndTime"

    
    def __init__(self):
        self.aws_test_db_access_key_id = os.environ.get('aws_test_db_access_key_id', None)
        self.aws_test_db_secret_access_key = os.environ.get('aws_test_db_secret_access_key', None)

        # If running locally
        if (
            self.aws_test_db_access_key_id is not None and 
            self.aws_test_db_secret_access_key is not None
            ):
            self.table_name = self.test_table_name
            self.dynamodb = boto3.client(self.resource,
                                    aws_access_key_id=self.aws_test_db_access_key_id,
                                    aws_secret_access_key=self.aws_test_db_secret_access_key,
                                    region_name=self.region)
        else:
           self.table_name = self.prod_table_name
           self.dynamodb = boto3.client(self.resource)

    def deserialize_response(self, response: List[dict]) -> List[dict]:
        deserialized_response = []
        for item in response[self.ITEMS_CONSTANT]:
            data = {k: self.deserializer.deserialize(v) for k,v in item.items()}
            deserialized_response.append(data)

        return deserialized_response

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
        related_sections = section_map.get(self.also_register_column, [])
        term_duration = TermDuration(section_map.get(self.duration_column))
        meeting_dates_list = section_map.get(self.meeting_dates_column, [])
        meeting_times = [self.convert_to_classtime(term_duration, meeting_date_map) for meeting_date_map in meeting_dates_list]
        return Section(course_code, section_id, crn, instructor, meeting_times, status, related_sections)

    def convert_to_classtime(self, term_duration: TermDuration, meeting_date_map: dict) -> ClassTime:
        day_of_week = DayOfWeek(meeting_date_map.get(self.day_of_week_column))
        start_time = meeting_date_map.get(self.start_time_column)
        end_time = meeting_date_map.get(self.end_time_column)
        return ClassTime(day_of_week, term_duration, start_time, end_time)

    def get_course(self, course_code: str, term: str) -> Course | None:
        '''
        Gets the Course object associated with a given course code and term.
        Returns None if the course code does not exist for the given term.
        '''
        filter_expression = "#subject = :subject AND #term = :term"
        attribute_names = {"#subject": self.subject_column, "#term": self.term_column}
        attribute_values = {":subject": {"S": course_code}, ":term": {"S": term}}

        last_evaluated_key = None
        while True:
            if last_evaluated_key is not None:
                response = self.dynamodb.scan(
                    TableName=self.table_name,
                    FilterExpression=filter_expression,
                    ExpressionAttributeNames=attribute_names,
                    ExpressionAttributeValues=attribute_values,
                    ExclusiveStartKey = last_evaluated_key
                )
            else:
                response = self.dynamodb.scan(
                    TableName=self.table_name,
                    FilterExpression=filter_expression,
                    ExpressionAttributeNames=attribute_names,
                    ExpressionAttributeValues=attribute_values
                )
            courses = self.deserialize_response(response)
            last_evaluated_key = response.get("LastEvaluatedKey")
            if len(courses) != 0 or last_evaluated_key is None:
                break

        if len(courses) == 0:
            return None
        if len(courses) > 1:
            logger.warning(f"There are more than one courses with code: {course_code} and term {term}!")
        
        course_map = courses[0]
        return self.convert_to_course(course_map)

    def get_terms(self) -> Set[str]:
        '''
        Gets the set of terms in the database.
        '''
        last_evaluated_key = None
        all_courses = []
        while True:
            if last_evaluated_key is not None:
                response = self.dynamodb.scan(
                    TableName=self.table_name,
                    ExclusiveStartKey = last_evaluated_key
                )
            else:
                response = self.dynamodb.scan(
                    TableName=self.table_name
                )
            courses = self.deserialize_response(response)
            all_courses.extend(courses)
            last_evaluated_key = response.get("LastEvaluatedKey")
            if last_evaluated_key is None:
                break
        
        return {course.get(self.term_column) for course in all_courses}
    
    def get_course_code_and_section_list(self, term: str) -> List[str]:
        '''
        Gets a list of the course codes and sections for a given term.
        '''
        filter_expression = "#term = :term"
        attribute_names = {"#term": self.term_column}
        attribute_values = {":term": {"S": term}}
        
        last_evaluated_key = None
        all_courses = []
        while True:
            if last_evaluated_key is not None:
                response = self.dynamodb.scan(
                    TableName=self.table_name,
                    FilterExpression=filter_expression,
                    ExpressionAttributeNames=attribute_names,
                    ExpressionAttributeValues=attribute_values,
                    ExclusiveStartKey = last_evaluated_key
                )
            else:
                response = self.dynamodb.scan(
                    TableName=self.table_name,
                    FilterExpression=filter_expression,
                    ExpressionAttributeNames=attribute_names,
                    ExpressionAttributeValues=attribute_values
                )
            courses = self.deserialize_response(response)
            all_courses.extend(courses)
            last_evaluated_key = response.get("LastEvaluatedKey")
            if last_evaluated_key is None:
                break
        return list({combination for course in all_courses for section in course.get(self.lecture_sections_column) for combination in (course.get(self.subject_column), course.get(self.subject_column) + " " + section.get(self.section_id_column))})

course_database = Database()
