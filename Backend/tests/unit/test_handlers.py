import json
import pytest
import boto3
boto3.setup_default_session(region_name="us-east-1")
from Backend.src import endpoints


@pytest.fixture()
def generate_schedules_event():
    """ Generates API GW Event"""

    return {
        "body": "{}"
    }


def test_generate_schedules_lambda_handler(generate_schedules_event):
    ret = endpoints.generate_schedules_lambda_handler(generate_schedules_event, "")
    data = json.loads(ret["body"])

    assert ret["statusCode"] == 400
    assert "Error" in ret["body"]
    assert "ErrorReason" in ret["body"]
    assert data["Error"] == True
    assert data["ErrorReason"] == "The JSON was missing a Term (or the Term was not a String)!"
