from typing import List
import boto3
from boto3.dynamodb.types import TypeDeserializer
import os
from ..model.course import Course
from ..logger import logger
from .database import CourseDatabase

class DynamoDatabase(CourseDatabase):
    table_name = ''
    test_table_name = "carleton-courses-test"
    prod_table_name = "carleton-courses"
    deserializer = TypeDeserializer()
    ITEMS_CONSTANT = "Items"
    
    def __init__(self):
        aws_test_db_access_key_id = os.environ.get('aws_test_db_access_key_id', None)
        aws_test_db_secret_access_key = os.environ.get('aws_test_db_secret_access_key', None)

        # If running locally
        if (
            aws_test_db_access_key_id is not None and 
            aws_test_db_secret_access_key is not None
            ):
            self.table_name = self.test_table_name
            self.dynamodb = boto3.client(self.get_resource(),
                                    aws_access_key_id=aws_test_db_access_key_id,
                                    aws_secret_access_key=aws_test_db_secret_access_key,
                                    region_name=self.region)
        else:
           self.table_name = self.prod_table_name
           self.dynamodb = boto3.client(self.get_resource())

    def get_resource(self):
        return 'dynamodb'
    
    def deserialize_response(self, response: List[dict]) -> List[dict]:
        deserialized_response = []
        for item in response[self.ITEMS_CONSTANT]:
            data = {k: self.deserializer.deserialize(v) for k,v in item.items()}
            deserialized_response.append(data)

        return deserialized_response

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

    def get_terms(self) -> List[str]:
        '''
        Gets the list of terms in the database.
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
        
        return list({course.get(self.term_column) for course in all_courses})
    
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

