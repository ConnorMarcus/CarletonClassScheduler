import pytest
import boto3
from botocore.exceptions import ClientError
from unittest.mock import patch
from Backend.src.database.database_error import ErrorCourseDatabase
from Backend.src.database.dynamo_database import DynamoDatabase

def test_valid_database_type(monkeypatch):
    # Test valid DB case
    monkeypatch.setenv("aws_test_db_access_key_id", "test_id") 
    monkeypatch.setenv("aws_test_db_secret_access_key", "test_secret")
    from Backend.src.database.database_type import course_database as db
    assert isinstance(db, DynamoDatabase) == True

@patch('Backend.src.database.database_type.get_database_class', side_effect=ClientError({}, ''))
def test_invalid_database_type(my_patch):
    from Backend.src.database.database_type import create_course_database
    assert isinstance(create_course_database(""), ErrorCourseDatabase) == True