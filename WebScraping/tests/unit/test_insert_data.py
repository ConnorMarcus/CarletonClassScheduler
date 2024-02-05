from WebScraping.functions.insertData.lambda_function import *
from unittest.mock import Mock, patch

FILE_PATH = "WebScraping.functions.insertData.lambda_function"
CLASS_DICT = {
    "Subject": "SYSC 4810", 
    "Term": "Fall 2023", 
    "Title": "Introduction to Network and Software Security", 
    "Prerequisite": "fourth-year status in Communications, Computer Systems or Software Engineering.",
    "LectureSections": [{
        "SectionID": "A", 
        "CRN": "35659", 
        "Status": "Registration Closed", 
        "SectionType": "In person", 
        "Instructor": "Test Professor", 
        "MeetingDates": [
            {"DayOfWeek": "Wed", "StartTime": "11:35", "EndTime": "12:55"}, 
            {"DayOfWeek": "Fri", "StartTime": "11:35", "EndTime": "12:55"}
        ], 
        "TermDuration": "Full Term", 
        "AlsoRegister": [["A1", "A2", "A3"]]
    }],
    "LabSections": []
}

def test_lambda_handler():

    with patch(f"{FILE_PATH}.get_classes_list") as mock_get_classes_list:
        mock_get_classes_list.return_value = [CLASS_DICT]

        with patch("boto3.resource") as mock_dynamodb:
            mock_table = mock_dynamodb().Table.return_value

            result = lambda_handler(event={}, context={})

            mock_get_classes_list.assert_called_once()
            mock_table.put_item.assert_called_once_with(Item=CLASS_DICT)
            assert result == {"Response": json.dumps("Classes inserted into carleton-courses DynamoDB table!")}


def test_get_classes_list():
    with patch("boto3.resource") as mock_s3:
        mock_s3_object = mock_s3().Object.return_value
        mock_s3_object.get.return_value = {"Body": Mock()}
        return_val = {"SYSC 4810-Fall 2023": CLASS_DICT}

        with patch("json.load", return_value=return_val):
            result = get_classes_list()

            assert result == [CLASS_DICT]
