import json
import boto3
from typing import List

BUCKET_NAME = "carletonschedulingtool"
KEY_PATH = "web-scraping-stepfunction/"
CLASSES_FILENAME = "classes.json"
TERMS_COURSES_FILENAME = "terms_courses.json"

def lambda_handler(event: dict, context: dict) -> str:
    terms_courses_dict = {}
    classes_list = get_classes_list()
    
    for course in classes_list:
        subject = course["Subject"]
        term_key = course["Term"]
        terms_courses_dict.setdefault(term_key, []).append(subject)
        
        for lecture in course["LectureSections"]:
            terms_courses_dict.get(term_key).append(f"{subject} {lecture['SectionID']}")

    return write_terms_courses_to_s3(terms_courses_dict)
            

def get_s3_object(filename: str) -> object:
    '''
    Gets the s3 file object where the href list and classes files are.
    
    Parameters:
    filename: The filename of the object to get.
    
    Returns
    S3 Object: The s3 file object.
    '''
    s3 = boto3.resource("s3")
    return s3.Object(BUCKET_NAME, KEY_PATH + filename)


def get_classes_list() -> List[dict]:
    '''
    Gets the list of classes from s3.
    
    Returns
    List[dict]: list of dict classes.
    '''
    classes_file = get_s3_object(CLASSES_FILENAME)
    classes = json.load(classes_file.get()["Body"])

    return list(classes.values())
    

def write_terms_courses_to_s3(terms_courses: dict[str, str]) -> str:
    '''
    Writes terms courses to S3.

    Parameters: 
    terms_courses: dictionary of terms with corresponding courses.

    Returns:
    str: Message indicating all terms and courses written to S3.
    '''
    
    terms_courses_file = get_s3_object(TERMS_COURSES_FILENAME)
    terms_courses_file.put(Body=(bytes(json.dumps(terms_courses).encode("UTF-8"))))
    
    return "Terms and Courses written to s3!"