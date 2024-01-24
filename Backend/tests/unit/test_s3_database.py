import pytest
from unittest.mock import patch, Mock
import boto3
boto3.setup_default_session(region_name="us-east-1")
from Backend.src.database.s3_database import S3Database
from Backend.tests.unit.test_dynamo_database import test_term

CLASSES_DICT = {"AERO 2001-Fall 2023": {
    "Subject": "AERO 2001", "Term": "Fall 2023", "Title": "Aerospace Engineering Graphical Design", 
    "Prerequisite": "Second-year status in Engineering.", "LectureSections": 
    [{"SectionID": "A", "CRN": "30037", "Status": "Registration Closed", "SectionType": "In person", "Instructor": "Pakeeza Hafeez", 
      "MeetingDates": [{"DayOfWeek": "Tue", "StartTime": "10:35", "EndTime": "11:25"}, {"DayOfWeek": "Thu", "StartTime": "10:35", "EndTime": "11:25"}], 
      "TermDuration": "Full Term", "AlsoRegister": [["L1"]], "StartDate": "2023-09-06", "EndDate": "2023-12-08"}], 
      "LabSections": [{"SectionID": "L1", "CRN": "30038", "Status": "Registration Closed", "SectionType": "In person", "Instructor": "Pakeeza Hafeez", 
                       "MeetingDates": [{"DayOfWeek": "Tue", "StartTime": "18:05", "EndTime": "19:55"}, {"DayOfWeek": "Thu", "StartTime": "18:05", "EndTime": "19:55"}], 
                       "TermDuration": "Full Term", "AlsoRegister": [["A"]], "StartDate": "2023-09-06", "EndDate": "2023-12-08", "WeekSchedule": "Every Week"}]
  }, "ERRORCLASS": {}
}
TERMS_COURSES_DICT = {"Fall 2023": ["AERO 2001", "AERO 2001 A"]}

@patch('boto3.resource')
@patch('json.load')
def generate_db(mock_json_file, mock_boto3_resource) -> S3Database:
    mock_boto3_resource.return_value = Mock()
    mock_json_file.side_effect = [CLASSES_DICT, TERMS_COURSES_DICT]
    mock_s3_object = Mock()
    mock_boto3_resource.return_value.Object.return_value = mock_s3_object
    mock_s3_object.get.return_value = {'Body': mock_json_file}
    
    
    return S3Database()

def test_create_db(monkeypatch):
    monkeypatch.setenv("aws_test_db_access_key_id", "test_id") 
    monkeypatch.setenv("aws_test_db_secret_access_key", "test_secret")
    db1 = generate_db()
    assert db1.classes_dict == CLASSES_DICT
    
    monkeypatch.delenv("aws_test_db_access_key_id") 
    monkeypatch.delenv("aws_test_db_secret_access_key")
    db2 = generate_db()
    assert db2.classes_dict == CLASSES_DICT

def test_get_course_code_and_section_list():
    db = generate_db()
    courses = db.get_course_code_and_section_list(test_term)
    assert sorted(courses) == ['AERO 2001', "AERO 2001 A"]

def test_get_terms():
    db = generate_db()
    assert db.get_terms() == [test_term]
    
    
def test_get_course():
    db = generate_db()
    code = "AERO 2001"
    course1 = db.get_course(code, test_term)
    course2 = db.get_course(code, "Winter 1999")

    assert course1.code == code
    assert course1.term == test_term
    assert course1.section_id_filter == None
    assert course2 == None
    

