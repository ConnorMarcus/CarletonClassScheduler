import json
import pytest
import boto3
from botocore.stub import Stubber
boto3.setup_default_session(region_name="us-east-1")
from Backend.src.model.section import Section
from Backend.src.model.date import ClassTime
from Backend.src.model.day_of_week import DayOfWeek
from Backend.src.model.term_duration import TermDuration
from Backend.src import endpoints
from Backend.src.database.database_type import course_database as database
from Backend.tests.unit.test_dynamo_database import test_scan_response1 as response1, test_scan_response2 as response2

TEST_TERM = "Fall 2023"
SAMPLE_SCHEDULE = [[Section("SYSC 4001", "B", "35905", "Test Prof 2", [ClassTime(DayOfWeek.TUESDAY, TermDuration.FULL_TERM, "08:35", "11:25")], "Registration Closed", [], "2023-09-06", "2023-12-08").to_dict()]]

@pytest.fixture()
def empty_json_event():
    return {
        "body": "{}"
    }

@pytest.fixture()
def no_courses_event():
    return {
        "body": f"{{\"Term\": \"{TEST_TERM}\"}}"
    }

@pytest.fixture()
def generate_schedules_event():
    return {
        "body": f"{{\"Term\": \"{TEST_TERM}\", \"Courses\": [{{\"SectionFilter\":\"B\", \"Name\":\"SYSC 4001\"}}]}}"
    }

@pytest.fixture()
def generate_schedules_with_filters_event():
    return {
        "body": f"{{\"Term\": \"{TEST_TERM}\", \"Filters\": {{\"BeforeTime\": \"08:00\", \"AfterTime\": \"19:00\", \"DayOfWeek\":\"Tue\"}}, \"Courses\": [{{\"SectionFilter\":\"B\", \"Name\":\"SYSC 4001\"}}]}}"
    }

@pytest.fixture()
def generate_schedules_with_empty_filters_event():
    return {
        "body": f"{{\"Term\": \"{TEST_TERM}\", \"Filters\": {{\"test\":\"empty\"}}, \"Courses\": [{{\"SectionFilter\":\"B\", \"Name\":\"SYSC 4001\"}}]}}"
    }

@pytest.fixture()
def generate_schedules_with_invalid_filter_event():
    return {
        "body": f"{{\"Term\": \"{TEST_TERM}\", \"Filters\": {{\"BeforeTime\": \"INVALID\"}}, \"Courses\": [{{\"SectionFilter\":\"B\", \"Name\":\"SYSC 4001\"}}]}}"
    }

@pytest.fixture()
def get_courses_without_term_event():
    return {
        "queryStringParameters": {}
    }

@pytest.fixture()
def get_courses_event():
    return {
        "queryStringParameters": {"Term": TEST_TERM}
    }

def test_generate_schedules_invalid_json():
    ret = endpoints.generate_schedules_lambda_handler("", "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 400
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert data["Error"] == True
    assert data["ErrorReason"] == "The body of the request must contain JSON!"

def test_generate_schedules_without_term(empty_json_event):
    ret = endpoints.generate_schedules_lambda_handler(empty_json_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 400
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert data["Error"] == True
    assert data["ErrorReason"] == "The JSON was missing a Term (or the Term was not a String)!"

def test_generate_schedules_without_courses(no_courses_event):
    ret = endpoints.generate_schedules_lambda_handler(no_courses_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 400
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert data["Error"] == True
    assert f"'Courses' attribute not passed in request body:" in data["ErrorReason"]

def test_generate_schedules_with_invalid_courses(generate_schedules_event):
    stubber = Stubber(database.dynamodb)
    stubber.add_response('scan', {'Items': []})
    
    with stubber:
        ret = endpoints.generate_schedules_lambda_handler(generate_schedules_event, "")
    
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 400
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert data["Error"] == True
    assert data["ErrorReason"] == f"Course SYSC 4001 does not exist for term {TEST_TERM}!"

def test_generate_schedules_success(generate_schedules_event):
    stubber = Stubber(database.dynamodb)
    stubber.add_response('scan', response2)
    
    with stubber:
        ret = endpoints.generate_schedules_lambda_handler(generate_schedules_event, "")
    
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert "Schedules" in ret["body"]
    assert data["Error"] == False
    assert data["ErrorReason"] == ""
    assert data["Schedules"] == SAMPLE_SCHEDULE

def test_generate_schedules_with_filters(generate_schedules_with_filters_event):
    stubber = Stubber(database.dynamodb)
    stubber.add_response('scan', response2)
    
    with stubber:
        ret = endpoints.generate_schedules_lambda_handler(generate_schedules_with_filters_event, "")
    
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert "Schedules" in ret["body"]
    assert data["Error"] == False
    assert data["ErrorReason"] == ""
    assert data["Schedules"] == []

def test_generate_schedules_with_empty_filters(generate_schedules_with_empty_filters_event):
    stubber = Stubber(database.dynamodb)
    stubber.add_response('scan', response2)
    
    with stubber:
        ret = endpoints.generate_schedules_lambda_handler(generate_schedules_with_empty_filters_event, "")
    
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert "Schedules" in ret["body"]
    assert data["Error"] == False
    assert data["ErrorReason"] == ""
    assert data["Schedules"] == SAMPLE_SCHEDULE

def test_generate_schedules_with_invalid_filters(generate_schedules_with_invalid_filter_event):
    stubber = Stubber(database.dynamodb)
    stubber.add_response('scan', response2)
    
    with stubber:
        ret = endpoints.generate_schedules_lambda_handler(generate_schedules_with_invalid_filter_event, "")
    
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 400
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert data["Error"] == True
    assert data["ErrorReason"] == "One or more of the filters are formatted incorrectly!"

def test_get_terms():
    stubber = Stubber(database.dynamodb)
    stubber.add_response('scan', response2)
    
    with stubber:
        ret = endpoints.get_terms_lambda_handler({}, "")
    
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert "Terms" in ret["body"]
    assert data["Error"] == False
    assert data["ErrorReason"] == ""
    assert data["Terms"] == [TEST_TERM]

def test_get_courses_without_term(get_courses_without_term_event):
    ret = endpoints.get_courses_lambda_handler(get_courses_without_term_event, "")
    
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 400
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert data["Error"] == True
    assert data["ErrorReason"] == "The Term must be included in the query string!"

def test_get_courses(get_courses_event):
    stubber = Stubber(database.dynamodb)
    stubber.add_response('scan', response1)
    stubber.add_response('scan', response2)
    
    with stubber:
        ret = endpoints.get_courses_lambda_handler(get_courses_event, "")
    
    data = json.loads(ret["body"])
    assert ret["statusCode"] == 200
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert "Courses" in ret["body"]
    assert data["Error"] == False
    assert data["ErrorReason"] == ""
    assert sorted(data["Courses"]) == ['ARCH 4505', 'ARCH 4505 A', 'SYSC 4001', 'SYSC 4001 B']