import pytest
import boto3
from botocore.stub import Stubber
boto3.setup_default_session(region_name="us-east-1")
from Backend.src.database.s3_database import S3Database
from Backend.src.database.database_type import course_database
from Backend.tests.unit.test_dynamo_database import test_scan_response1, test_scan_response2, test_term

#TODO: Implement tests for S3 database

CLASSES_DICT = {"AERO 2001-Fall 2023": 
                {"Subject": "AERO 2001", "Term": "Fall 2023", "Title": "Aerospace Engineering Graphical Design", 
                 "Prerequisite": "Second-year status in Engineering.", "LectureSections": 
                 [{"SectionID": "A", "CRN": "30037", "Status": "Registration Closed", "SectionType": "In person", "Instructor": "Pakeeza Hafeez", 
                   "MeetingDates": [{"DayOfWeek": "Tue", "StartTime": "10:35", "EndTime": "11:25"}, {"DayOfWeek": "Thu", "StartTime": "10:35", "EndTime": "11:25"}], 
                   "TermDuration": "Full Term", "AlsoRegister": [["L1"]], "StartDate": "2023-09-06", "EndDate": "2023-12-08"}], 
                   "LabSections": [{"SectionID": "L1", "CRN": "30038", "Status": "Registration Closed", "SectionType": "In person", "Instructor": "Pakeeza Hafeez", 
                                    "MeetingDates": [{"DayOfWeek": "Tue", "StartTime": "18:05", "EndTime": "19:55"}, {"DayOfWeek": "Thu", "StartTime": "18:05", "EndTime": "19:55"}], 
                                    "TermDuration": "Full Term", "AlsoRegister": [["A"]], "StartDate": "2023-09-06", "EndDate": "2023-12-08", "WeekSchedule": "Every Week"}]}
                }

# def test_create_db():

# def test_get_course_code_and_section_list():

# def test_get_terms():
    
# def test_get_course():
    

