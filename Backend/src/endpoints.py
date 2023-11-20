import json
from typing import Any, Dict
from .database.database import course_database
from .model.course import Course
from .model.date import ClassTime
from .model.day_of_week import DayOfWeek
from .model.filter import Filter
from .scheduler import generate_schedules
from .logger import logger

SUCCESS_CODE = 200
BAD_REQUEST_CODE = 400
QUERY_STRING_PARAMETERS = "queryStringParameters"

def generate_schedules_lambda_handler(event: dict, context: object) -> dict:
    try:
        body = json.loads(event['body'])
        term = body.get("Term")
        filters_object = body.get("Filters")
        courses = body.get("Courses")
        if term is None:
            return lambda_response(BAD_REQUEST_CODE, True, "The JSON was missing the Term!")
        
        # Get inputted courses
        inputted_courses = []
        for course in courses:
            course_code = course.get("Name", "")
            inputted_course = course_database.get_course(course_code, term)
            if inputted_course is None:
                return lambda_response(BAD_REQUEST_CODE, True, f"One or more courses do not exist for term {term}!")
            
            inputted_course.section_id_filter = course.get("SectionFilter")
            inputted_courses.append(inputted_course)

        # Filter courses
        if filters_object:
            before_time_input = filters_object.get("BeforeTime")
            after_time_input = filters_object.get("AfterTime")
            day_input = filters_object.get("DayOfWeek")
            try:
                day_of_week = None
                if before_time_input is not None:
                    ClassTime.convert_time_to_float(before_time_input)
                if after_time_input is not None:
                    ClassTime.convert_time_to_float(after_time_input)
                if day_input is not None:
                    day_of_week = DayOfWeek(day_input)
                class_filter = Filter(before_time=before_time_input, after_time=after_time_input, day_of_week=day_of_week)
                Course.filter_all_courses(inputted_courses, class_filter)
            except:
                return lambda_response(BAD_REQUEST_CODE, True, f"One or more of the filters are formatted incorrectly!")
        else:
            Course.filter_all_courses(inputted_courses, Filter())
            
        #Generate Schedules
        schedules = generate_schedules(inputted_courses)
        return lambda_response(SUCCESS_CODE, False, "", {"Schedules": [[section.to_dict() for section in schedule] for schedule in schedules]})

    except Exception as error:
        logger.error(error)
        return lambda_response(BAD_REQUEST_CODE, True, "The body of the request must contain JSON!")

def get_terms_lambda_handler(event: dict, context: object) -> dict:
    terms = course_database.get_terms()
    return lambda_response(SUCCESS_CODE, False, "", {"Terms": list(terms)})
    
def get_courses_lambda_handler(event: dict, context: object) -> dict:
    query_params: dict = event[QUERY_STRING_PARAMETERS]
    term = query_params.get("Term")
    if term is None:
        return lambda_response(BAD_REQUEST_CODE, True, "The Term must be included in the query string!")
    
    courses_with_sections = course_database.get_course_code_and_section_list(term)
    return lambda_response(SUCCESS_CODE, False, "", {"Courses": courses_with_sections})

def lambda_response(status: int, error: bool, error_reason: str, body: Dict[str, Any] = {}) -> dict:
    response_body = {
        "Error": error,
        "ErrorReason": error_reason    
    }
    response_body.update(body)
    response = {
        "statusCode": status,
        "headers": {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        },
        "body": json.dumps(response_body)
    }
    
    return response