import json
import boto3
from typing import List

BUCKET_NAME = "carletonschedulingtool"
KEY_PATH = "web-scraping-stepfunction/classes.json"
TABLE_NAME = "carleton-courses"

def lambda_handler(event: dict, context: dict) -> str:
    classes_list = get_classes_list()
    
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(TABLE_NAME)
    
    for course in classes_list:
        table.put_item(Item=course)
 
    return f"Classes inserted into {TABLE_NAME} DB!"


def get_classes_list() -> List[dict]:
    '''
    Gets the list of classes from s3
    
    Returns
    List[dict]: list of dict classes
    '''
    s3 = boto3.resource("s3")

    classes_file = s3.Object(BUCKET_NAME, KEY_PATH)
    classes = json.load(classes_file.get()["Body"])

    return list(classes.values())
   