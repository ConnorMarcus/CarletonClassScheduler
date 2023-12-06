import pytest
import boto3
from botocore.stub import Stubber
boto3.setup_default_session(region_name="us-east-1")
from Backend.src.database.database import course_database
from Backend.src.database.database import Database


test_term = "Fall  2023"

test_scan_response1 = {
    "Items": [
        {
            'Title': {'S': 'Seminar in Theory and History'}, 
            'Term': {'S': test_term}, 
            'Prerequisite': {'S': 'fourth-year standing in the B.A.S. or B.A.'}, 
            'LabSections': {'L': []}, 
            'LectureSections': {'L': [{'M': {
                'Status': {'S': 'Registration Closed'}, 
                'SectionType': {'S': 'In person'}, 
                'Instructor': {'S': 'Test Prof'}, 
                'MeetingDates': {'L': [{'M': {'StartTime': {'S': '08:35'}, 'EndTime': {'S': '11:25'}, 'DayOfWeek': {'S': 'Mon'}}}]}, 
                'TermDuration': {'S': 'Full Term'}, 
                'AlsoRegister': {'L': []}, 
                'SectionID': {'S': 'A'}, 
                'CRN': {'S': '35904'}}}]}, 
            'Subject': {'S': 'ARCH 4505'}
        } 
    ],
    "LastEvaluatedKey": {'Key': {'S': 'TEST KEY'}}
}

test_scan_response2 = {
    "Items": [
        {
            'Title': {'S': 'Operating Systems'}, 
            'Term': {'S': test_term}, 
            'Prerequisite': {'S': 'fourth-year standing.'}, 
            'LabSections': {'L': []}, 
            'LectureSections': {'L': [{'M': {
                'Status': {'S': 'Registration Closed'}, 
                'SectionType': {'S': 'In person'}, 
                'Instructor': {'S': 'Test Prof 2'}, 
                'MeetingDates': {'L': [{'M': {'StartTime': {'S': '08:35'}, 'EndTime': {'S': '11:25'}, 'DayOfWeek': {'S': 'Tue'}}}]}, 
                'TermDuration': {'S': 'Full Term'}, 
                'AlsoRegister': {'L': []}, 
                'SectionID': {'S': 'B'}, 
                'CRN': {'S': '35905'}}}]}, 
            'Subject': {'S': 'SYSC 4001'}
        } 
    ]
}

def test_create_db(monkeypatch):
    '''
    test creating the database object
    '''
    monkeypatch.setenv("aws_test_db_access_key_id", "test_id") 
    monkeypatch.setenv("aws_test_db_secret_access_key", "test_secret")
    db1 = Database()
    assert db1.table_name == db1.test_table_name

    monkeypatch.delenv("aws_test_db_access_key_id") 
    monkeypatch.delenv("aws_test_db_secret_access_key")
    db2 = Database()
    assert db2.table_name == db2.prod_table_name

def test_get_course_code_and_section_list():
    stubber = Stubber(course_database.dynamodb)
    stubber.add_response('scan', test_scan_response1)
    stubber.add_response('scan', test_scan_response2)

    with stubber:
        result = course_database.get_course_code_and_section_list(test_term)

    assert sorted(result) == ['ARCH 4505', 'ARCH 4505 A', 'SYSC 4001', 'SYSC 4001 B']

def test_get_terms():
    stubber = Stubber(course_database.dynamodb)
    stubber.add_response('scan', test_scan_response1)
    stubber.add_response('scan', test_scan_response2)

    with stubber:
        result = course_database.get_terms()

    assert result == {test_term}

def test_get_course():
    stubber = Stubber(course_database.dynamodb)
    stubber.add_response('scan', {'Items': [], "LastEvaluatedKey": {'Key': {'S': 'TEST KEY'}}})
    stubber.add_response('scan', test_scan_response2)
    stubber.add_response('scan', {'Items': []})
    stubber.add_response('scan', {'Items': [item for item in (test_scan_response1['Items'][0], test_scan_response2['Items'][0])]})

    with stubber:
        course1 = course_database.get_course("SYSC 4001", test_term) # test valid case
        course2 = course_database.get_course("INVALID CODE", test_term) # test invalid case
        course3 = course_database.get_course("ARCH 4505", test_term) # test case where duplicate course in database

    assert course1.code == "SYSC 4001"
    assert course1.term == test_term
    assert course1.section_id_filter == None
    assert course2 == None
    assert course3.code == "ARCH 4505"
    assert course3.term == test_term
    assert course3.section_id_filter == None

