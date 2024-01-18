import os
from .database import CourseDatabase
from .dynamo_database import DynamoDatabase
from .s3_database import S3Database

S3_DATABASE = "s3"
DYNAMO_DATABASE = "dynamodb"
databases = {S3_DATABASE: S3Database(), DYNAMO_DATABASE: DynamoDatabase()}
db_type = os.environ.get('database_type', S3_DATABASE)
course_database: CourseDatabase = databases[db_type]