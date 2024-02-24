import json
import botocore.exceptions
from typing import Any, Dict, List
from .database.database_type import course_database
from .database.database_error import CouresDatabaseException
from .model.course import Course
from .model.date import ClassTime
from .model.day_of_week import DayOfWeek
from .model.term_duration import TermDuration
from .model.week_schedule import WeekSchedule
from .model.filter import Filter
from .scheduler import generate_schedules, MAX_SCHEDULES
from .logger import logger
from .endpoint_exceptions import RequestBodyException, MissingCourseException, MissingCoursesKeyException, FiltersFormatException

SUCCESS_CODE = 200
BAD_REQUEST_CODE = 400
SERVICE_UNAVAILABLE_CODE = 503
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
        except RequestBodyException as error:
            return lambda_response(BAD_REQUEST_CODE, True, str(error))
            
        #Generate Schedules
        schedules = generate_schedules(inputted_courses)[:MAX_SCHEDULES]
        return lambda_response(SUCCESS_CODE, False, "", {"Schedules": [[section.to_dict() for section in schedule] for schedule in schedules]})

    except (botocore.exceptions.ClientError, CouresDatabaseException) as error:
        logger.error(error)
        return lambda_response(SERVICE_UNAVAILABLE_CODE, True, "This service is currently unavailable, please try again later!")
    except Exception as error:
        logger.error(error)
        return lambda_response(BAD_REQUEST_CODE, True, "The body of the request must contain JSON!")

def get_terms_lambda_handler(event: dict, context: object) -> dict:
    try:
        terms = course_database.get_terms()
        return lambda_response(SUCCESS_CODE, False, "", {"Terms": terms})
    except (botocore.exceptions.ClientError, CouresDatabaseException) as error:
        logger.error(error)
        return lambda_response(SERVICE_UNAVAILABLE_CODE, True, "This service is currently unavailable, please try again later!")
    
def get_courses_lambda_handler(event: dict, context: object) -> dict:
    try:
        query_params: dict = event[QUERY_STRING_PARAMETERS]
        term = query_params.get("Term")
        if term is None:
            return lambda_response(BAD_REQUEST_CODE, True, "The Term must be included in the query string!")
        
        courses_with_sections = course_database.get_course_code_and_section_list(term)
        return lambda_response(SUCCESS_CODE, False, "", {"Courses": courses_with_sections})
    except (botocore.exceptions.ClientError, CouresDatabaseException) as error:
        logger.error(error)
        return lambda_response(SERVICE_UNAVAILABLE_CODE, True, "This service is currently unavailable, please try again later!")

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
        raise MissingCoursesKeyException(error_message)

    inputted_courses = []
    for course in courses:
        course_code = course.get("Name", "").strip()
        inputted_course = course_database.get_course(course_code, term)
        if inputted_course is None:
            error_message = f"Course {course_code} does not exist for term {term}!"
            logger.error(error_message)
            raise MissingCourseException(error_message)
        
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
        between_times_input = filters_object.get("BetweenTimes")
        try:
            day_of_week = None
            between_times = []
            if before_time_input is not None:
                ClassTime.convert_time_to_float(before_time_input)
            if after_time_input is not None:
                ClassTime.convert_time_to_float(after_time_input)
            if day_input is not None:
                day_of_week = DayOfWeek(day_input)
            if between_times_input is not None:
                between_times = [convert_to_classtime(between_time) for between_time in between_times_input]
            class_filter = Filter(before_time=before_time_input, after_time=after_time_input, day_of_week=day_of_week, between_times=between_times)
            Course.filter_all_courses(inputted_courses, class_filter)
        except:
            error_message = f"One or more of the filters are formatted incorrectly!"
            logger.error(error_message)
            raise FiltersFormatException(error_message)
    else:
        Course.filter_all_courses(inputted_courses, Filter())

def convert_to_classtime(between_time: dict) -> ClassTime:
    '''
    Helper function to convert a time sent in a request to a ClassTime object
    '''
    try:
        day_of_week = DayOfWeek(between_time.get("DayOfWeek"))
        start_time = between_time.get("StartTime")
        end_time = between_time.get("EndTime")
        return ClassTime(day_of_week, TermDuration.FULL_TERM, start_time, end_time, WeekSchedule.EVERY_WEEK)
    except:
        error_message = f"The BetweenTimes filters are formatted incorrectly!"
        logger.error(error_message)
        raise Exception(error_message)