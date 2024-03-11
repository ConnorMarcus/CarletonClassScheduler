import pytest
from Backend.src.database.database_error import ErrorCourseDatabase, CouresDatabaseException

error_db = ErrorCourseDatabase()

def test_get_resource():
    with pytest.raises(CouresDatabaseException):
        error_db.get_resource()

def test_get_course():
    with pytest.raises(CouresDatabaseException):
        error_db.get_course("", "")

def test_get_terms():
    with pytest.raises(CouresDatabaseException):
        error_db.get_terms()

def test_get_course_code_and_section_list():
    with pytest.raises(CouresDatabaseException):
        error_db.get_course_code_and_section_list("")

def test_convert_to_course():
    with pytest.raises(CouresDatabaseException):
        error_db.convert_to_course(None)

def test_convert_to_section():
    with pytest.raises(CouresDatabaseException):
        error_db.convert_to_section(None, None, None, None, None)
    
def test_convert_to_classtime():
    with pytest.raises(CouresDatabaseException):
        error_db.convert_to_classtime(None, None, None)