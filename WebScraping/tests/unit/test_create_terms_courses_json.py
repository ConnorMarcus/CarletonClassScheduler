from WebScraping.functions.createTermsCoursesJson.lambda_function import *
from botocore.stub import Stubber
from unittest.mock import MagicMock, patch

FILE_PATH = "WebScraping.functions.createTermsCoursesJson.lambda_function"
TEST_TERM_COURSE = {"Fall 2023": ["SYSC 4310 A"], "Winter 2024": ["SYSC 4504"]}
CLASSES_DICT = {"AERO 2001-Fall 2023":
    {
        "Subject": "AERO 2001",
        "Term": "Fall 2023", 
        "Title": "Aerospace Engineering Graphical Design", 
        "Prerequisite": "Second-year status in Engineering.", 
        "LectureSections": [
            {
                "SectionID": "A", "CRN": "30037", "Status": "Registration Closed", 
                "SectionType": "In person", "Instructor": "Pakeeza Hafeez", 
                "MeetingDates": [{"DayOfWeek": "Tue", "StartTime": "10:35", "EndTime": "11:25"}, {"DayOfWeek": "Thu", "StartTime": "10:35", "EndTime": "11:25"}], 
                "TermDuration": "Full Term", "AlsoRegister": [["L1"]], "StartDate": "2023-09-06", "EndDate": "2023-12-08"}], 
      "LabSections": [
          {
              "SectionID": "L1", "CRN": "30038", "Status": "Registration Closed", 
              "SectionType": "In person", "Instructor": "Pakeeza Hafeez",
              "MeetingDates": [{"DayOfWeek": "Tue", "StartTime": "18:05", "EndTime": "19:55"}, {"DayOfWeek": "Thu", "StartTime": "18:05", "EndTime": "19:55"}], 
              "TermDuration": "Full Term", "AlsoRegister": [["A"]], "StartDate": "2023-09-06", "EndDate": "2023-12-08", "WeekSchedule": "Every Week"}]
    }
}

def test_lambda_handler():
    class_list = list(CLASSES_DICT.values())

    with patch(f"{FILE_PATH}.get_classes_list", return_value=class_list):
        with patch(f"{FILE_PATH}.write_terms_courses_to_s3") as mock_write_terms:
            lambda_handler(event=None, context=None)

            expected_result = {"Fall 2023": ["AERO 2001", "AERO 2001 A"]}
            mock_write_terms.assert_called_once_with(expected_result)


def test_get_s3_object():
    s3_client = boto3.client("s3")
    s3_stubber = Stubber(s3_client)

    test_filename = "Test_file.json"
    expected_key = KEY_PATH + test_filename
    expected_params = {"Bucket": BUCKET_NAME, "Key": expected_key}
    s3_stubber.add_response("get_object", {"Body": "test content"}, expected_params)

    with s3_stubber:
        result = get_s3_object(test_filename)

    assert result.bucket_name == BUCKET_NAME
    assert result.key == expected_key


def test_get_classes_list():
    s3_object = MagicMock()
    class_dict = json.dumps(CLASSES_DICT)
    s3_object.get.return_value = {"Body": MagicMock(read=lambda: class_dict)}

    with patch(f"{FILE_PATH}.get_s3_object", return_value=s3_object) as mock_s3:
        result = get_classes_list()
        mock_s3.assert_called_once_with(CLASSES_FILENAME)

        assert result == list(CLASSES_DICT.values())


def test_write_terms_courses_to_s3():
    s3_object = MagicMock()
    s3_object.put = MagicMock()

    with patch(f"{FILE_PATH}.get_s3_object", return_value=s3_object) as mock_s3:

        result = write_terms_courses_to_s3(TEST_TERM_COURSE)
        mock_s3.assert_called_once_with(TERMS_COURSES_FILENAME)

        expected_result = bytes(json.dumps(TEST_TERM_COURSE).encode("UTF-8"))
        s3_object.put.assert_called_once_with(Body=expected_result)

        assert result == {"Response": json.dumps("Terms and Courses written to s3!")}

    