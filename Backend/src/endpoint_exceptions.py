class RequestBodyException(Exception):
    pass

class MissingCoursesKeyException(RequestBodyException):
    pass

class MissingCourseException(RequestBodyException):
    pass

class FiltersFormatException(RequestBodyException):
    pass