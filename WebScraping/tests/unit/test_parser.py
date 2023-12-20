from WebScraping.functions.parser.lambda_function import *
from unittest.mock import MagicMock, patch
from bs4 import BeautifulSoup
from botocore.stub import Stubber
import os
import pytest

FILE_PATH = "WebScraping.functions.parser.lambda_function"

def test_lambda_handler():
    s3_href_object = MagicMock()
    s3_href_object.bucket_name = BUCKET_NAME
    s3_href_object.key = KEY_PATH + "href_list.json"
    s3_href_object.get.return_value = {"Body": MagicMock(read=lambda: "[]")}

    s3_classes_object = MagicMock()
    s3_classes_object.bucket_name = BUCKET_NAME
    s3_classes_object.key = KEY_PATH + "classes.json"
    s3_classes_object.get.return_value = {"Body": MagicMock(read=lambda: "")}

    with patch(f"{FILE_PATH}.get_s3_object", side_effect=[s3_href_object, s3_classes_object]):
        result = lambda_handler(event={}, context={})
        s3_href_object.get.assert_called_once_with()
        s3_classes_object.put.assert_called_once_with(Body=b"{}")
        assert result == "classes JSON written to s3"


def test_get_data():
    href_dict = {"href": "test-course-href", "also_register": "test-also-register-str"}
    test_html = "<html><body>Mocked HTML</body></html>"
    expected_url = BASE_URL + href_dict["href"]
    expected_bs4 = BeautifulSoup(test_html, "html.parser")

    with patch("urllib3.PoolManager.request") as mock_pool_manager:
        mock_response = MagicMock()
        mock_response.data = test_html.encode()
        mock_pool_manager.return_value = mock_response

        with patch(f"{FILE_PATH}.parse_data") as mock_parser:
            get_data(href_dict)
            mock_pool_manager.assert_called_once()
            mock_pool_manager.assert_called_once_with("GET", expected_url)
            mock_parser.assert_called_once_with(expected_bs4, href_dict["also_register"])


def test_get_s3_object():
    s3_client = boto3.client("s3")
    s3_stubber = Stubber(s3_client)

    expected_key = KEY_PATH + "href_list.json"
    expected_params = {"Bucket": BUCKET_NAME, "Key": expected_key}
    s3_stubber.add_response("get_object", {"Body": "test content"}, expected_params)

    with s3_stubber:
        result = get_s3_object("href_list.json")

    assert result.bucket_name == BUCKET_NAME
    assert result.key == expected_key


def get_bs4_parser(file_name):
    '''
    Helper function used to get bs4 html parser
    '''
    html_file_path = os.path.join(os.path.dirname(__file__), "..", "utils", file_name)
    with open(html_file_path, "r") as file:
        html_content = file.read()

    return BeautifulSoup(html_content, "html.parser")


@pytest.fixture
def get_lecture_bs4_object():
    return get_bs4_parser("sysc4810A.html")


@pytest.fixture
def get_lab_bs4_object():
    return get_bs4_parser("sysc4810A1.html")


def test_parse_data(get_lecture_bs4_object, get_lab_bs4_object):
    except_classess_dict = {"SYSC 4810-Fall 2023": 
        {
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
            "LabSections": [{
                "SectionID": "A1", 
                "CRN": "35660", 
                "Status": "Registration Closed", 
                "SectionType": "In person", 
                "Instructor": "", 
                "MeetingDates": [
                    {"DayOfWeek": "Thu", "StartTime": "10:05", "EndTime": "11:25"},
                ], 
                "TermDuration": "Full Term",
                "AlsoRegister": [["A"]],
                "WeekSchedule": "Every Week"
            }]
        }
    }

    mock_classes_dict = {}
    with patch(f"{FILE_PATH}.classes", mock_classes_dict):
        also_register_str_lecture = "SYSC 4810 A1 or A2 or A3"
        parse_data(get_lecture_bs4_object, also_register_str_lecture)

        also_register_str_lab = "SYSC 4810 A"
        parse_data(get_lab_bs4_object, also_register_str_lab)

        assert "SYSC 4810-Fall 2023" in mock_classes_dict
        assert len(mock_classes_dict) == 1
        assert mock_classes_dict == except_classess_dict


def test_is_lecture_section():
    assert is_lecture_section("A") == True
    assert is_lecture_section("E") == True

    assert is_lecture_section("L10") == False
    assert is_lecture_section("A2") == False


def test_has_keyword_in_text():
    # Testing using str as keyword arg
    assert has_keyword_in_text("test", "This is a test") == True
    assert has_keyword_in_text("test2", "This is a test") == False

    # Testing using list as keyword arg
    assert has_keyword_in_text(["test", "test2", "test3"], "This is a test") == True
    assert has_keyword_in_text(["test2", "test3", "test4"], "This is a test") == False


def test_get_prerequisite():
    test_preq = "SYSC TEST PREQ"
    assert get_prerequisite(f"Test description Prerequisite(s): {test_preq}") == test_preq

    test_preq2 = "Second year standing"
    assert get_prerequisite(f"Test description Prerequisite(s): {test_preq2}") == test_preq2

    # Test with &nbsp present
    test_preq_with_nbsp = "SYSC TEST\u00a0PREQ"
    assert get_prerequisite(f"Test description Prerequisite(s): {test_preq_with_nbsp}") == test_preq

    # Test when no Preq
    assert get_prerequisite("Test description with no preq") == ""


def test_get_section_type():
    assert get_section_type("IN-PERSON TEST") == "In person"
    assert get_section_type("IN-PERSON. NOT SUITABLE FOR ONLINE STUDENTS") == "In person"
    assert get_section_type("ONLINE TEST") == "Online"


def test_get_associated_sections():
    test_str_1 = "CHEM 1005 ATU and CHEM 1005 A1 or A6 or A7 or G1"
    assert get_associated_sections(test_str_1) == [["ATU"], ["A1", "A6", "A7", "G1"]]

    test_str_2 = "CHEM 1005 ATU or ATI and CHEM 1005 A1 or A6 or A7 or G1"
    assert get_associated_sections(test_str_2) == [["ATU", "ATI"], ["A1", "A6", "A7", "G1"]]

    test_str_3 = "CHEM 1005 A1 or A6 or A7 or G1"
    assert get_associated_sections(test_str_3) == [["A1", "A6", "A7", "G1"]]

    test_str_4 = "CHEM 1005 A1"
    assert get_associated_sections(test_str_4) == [["A1"]]

    assert get_associated_sections("") == []


def test_get_term_duration_str():
    assert get_term_duration_str("May 04, 2023 to Aug 16, 2023") == "Full Term"
    assert get_term_duration_str("Sep 11, 2023 to Dec 08, 2023") == "Full Term"
    assert get_term_duration_str("Jan 08, 2024 to Apr 10, 2024") == "Full Term"

    assert get_term_duration_str("May 04, 2023 to Jun 16, 2023") == "Early Term"
    assert get_term_duration_str("Sep 06, 2023 to Oct 20, 2023") == "Early Term"
    assert get_term_duration_str("Jan 08, 2024 to Feb 16, 2024") == "Early Term"

    assert get_term_duration_str("Oct 30, 2023 to Dec 08, 2023") == "Late Term"
    assert get_term_duration_str("Feb 26, 2024 to Apr 10, 2024") == "Late Term"
    assert get_term_duration_str("Jul 04, 2023 to Aug 16, 2023") == "Late Term"


def test_get_lab_week_schedule():
    assert get_lab_week_schedule("L10") == "Every Week"
    assert get_lab_week_schedule("E1") == "Every Week"

    assert get_lab_week_schedule("L10E") == "Even Week"
    assert get_lab_week_schedule("A2E") == "Even Week"

    assert get_lab_week_schedule("L4O") == "Odd Week"
    assert get_lab_week_schedule("A2O") == "Odd Week"


def test_get_meeting_date_list_edge_cases():
    '''
    This tests some edges cases in the get_meeting_date_list()
    '''
    tr_str1 = "<tr><td>May 04, 2023 to Jun 16, 2023</td><td>Mon Wed</td><td></td></tr>"
    tr_str2 = "<tr><td>May 04, 2023 to Jun 16, 2023</td><td>Wed Fri</td><td>11:35 - 14:25</td></tr>"
    mock_bs4_tr1 = BeautifulSoup(tr_str1, 'html.parser')
    mock_bs4_tr2 = BeautifulSoup(tr_str2, 'html.parser')

    result1 = get_meeting_date_list([mock_bs4_tr1])
    assert result1 == []

    result2 = get_meeting_date_list([mock_bs4_tr2, mock_bs4_tr2])
    expected_list = [{"DayOfWeek": "Wed", "StartTime": "11:35", "EndTime": "14:25"}, 
        {"DayOfWeek": "Fri", "StartTime": "11:35", "EndTime": "14:25"}]
    assert result2 == expected_list