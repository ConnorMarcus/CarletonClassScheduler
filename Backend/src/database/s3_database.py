import copy
from typing import List, Dict
import boto3
import os
from ..model.course import Course
from ..logger import logger
from .database import CourseDatabase
import json

class S3Database(CourseDatabase):
    def __init__(self):
        aws_test_db_access_key_id = os.environ.get('aws_test_db_access_key_id', None)
        aws_test_db_secret_access_key = os.environ.get('aws_test_db_secret_access_key', None)
        bucket_name = "carletonschedulingtool"
        classes_json_file = "web-scraping-stepfunction/classes.json"
        terms_json_file = "web-scraping-stepfunction/terms.json"
        terms_courses_json_file = "web-scraping-stepfunction/terms_courses.json"

        # If running locally
        if (
            aws_test_db_access_key_id is not None and 
            aws_test_db_secret_access_key is not None
            ):
            s3 = boto3.resource(self.get_resource(), 
                                aws_access_key_id=aws_test_db_access_key_id, 
                                aws_secret_access_key=aws_test_db_secret_access_key, 
                                region_name=self.region)
        else:
            s3 = boto3.resource(self.get_resource())

        classes_file = s3.Object(bucket_name, classes_json_file)
        terms_file = s3.Object(bucket_name, terms_json_file)
        terms_courses_file = s3.Object(bucket_name, terms_courses_json_file)
        self.classes_dict: Dict[str, dict] = json.load(classes_file.get()["Body"])
        self.terms_dict: Dict[str, dict] = json.load(terms_file.get()["Body"])
        self.terms_courses_dict: Dict[str, List] = json.load(terms_courses_file.get()["Body"])

    def get_resource(self):
        return 's3'

    def get_course(self, course_code: str, term: str) -> Course | None:
        '''
        Gets the Course object associated with a given course code and term.
        Returns None if the course code does not exist for the given term.
        '''
        course_map = self.classes_dict.get(f"{course_code}-{term}", None)
        if course_map is None:
            logger.warning(f"There are no courses with code: {course_code} and term: {term}!")
            return None
        
        return self.convert_to_course(course_map)

    def get_terms(self) -> dict:
        '''
        Gets the terms dict in the database.
        '''
        return self.terms_dict


    def get_course_code_and_section_list(self, term: str) -> List[str]:
        '''
        Gets a list of the course codes and sections for a given term.
        '''
        return self.terms_courses_dict.get(term, [])
