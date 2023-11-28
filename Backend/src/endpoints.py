import json
from typing import Any, Dict, List
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
        body: dict = json.loads(event['body'])
        term = body.get("Term")
        if term is None or not isinstance(term, str):
            return lambda_response(BAD_REQUEST_CODE, True, "The JSON was missing a Term (or the Term was not a String)!")
        
        term = term.strip() # remove leading/trailing whitespace from term
        
        try:
            inputted_courses = get_inputted_courses(body, term)
            filter_inputted_courses(body, inputted_courses)
        except Exception as error:
            return lambda_response(BAD_REQUEST_CODE, True, str(error))
            
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
    courses_with_sections.sort()
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


def get_inputted_courses(request_body: dict, term: str) -> List[Course]:
    '''
    Helper function to get a list of the inputted courses from a user's request.
    '''
    courses: List[dict] = request_body.get("Courses")
    if courses is None:
        error_message = f"'Courses' attribute not passed in request body: {request_body}"
        logger.error(error_message)
        raise Exception(error_message)

    inputted_courses = []
    for course in courses:
        course_code = course.get("Name", "").strip()
        inputted_course = course_database.get_course(course_code, term)
        if inputted_course is None:
            error_message = f"Course {course_code} does not exist for term {term}!"
            logger.error(error_message)
            raise Exception(error_message)
        
        inputted_course.section_id_filter = course.get("SectionFilter")
        inputted_courses.append(inputted_course)

    return inputted_courses

def filter_inputted_courses(request_body: dict, inputted_courses: List[Course]) -> None:
    '''
    Helper function to filter all of the inputted courses by using the filters included in the request body.
    '''
    filters_object: dict = request_body.get("Filters")
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
            error_message = f"One or more of the filters are formatted incorrectly!"
            logger.error(error_message)
            raise Exception(error_message)
    else:
        Course.filter_all_courses(inputted_courses, Filter())
