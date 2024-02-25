import os
import boto3
import botocore.exceptions
from .database import CourseDatabase
from .dynamo_database import DynamoDatabase
from .s3_database import S3Database
from .database_error import ErrorCourseDatabase

S3_DATABASE = "s3"
DYNAMO_DATABASE = "dynamodb"
databases = {S3_DATABASE: S3Database, DYNAMO_DATABASE: DynamoDatabase}

def get_database_class(db_type):
    return databases[db_type]

def create_course_database(db_type) -> CourseDatabase:
    try:
        return get_database_class(db_type)()
    except botocore.exceptions.ClientError as error:
        return ErrorCourseDatabase()

db_type = os.environ.get('database_type', S3_DATABASE)
course_database: CourseDatabase = create_course_database(db_type)