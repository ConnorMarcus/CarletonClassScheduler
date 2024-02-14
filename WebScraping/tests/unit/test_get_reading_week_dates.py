from WebScraping.functions.getReadingWeekDates.lambda_function import *
from unittest.mock import MagicMock, patch
from botocore.stub import Stubber

FILE_PATH = "WebScraping.functions.getReadingWeekDates.lambda_function"

TERMS_DICT = {
    "Fall 2023": {
        "ReadingWeekStart": "2023-10-21", 
        "ReadingWeekEnd": "2023-10-30", 
        "ReadingWeekNext": "2023-11-06"
    }
}

CLASSES_DICT = {
    "AERO 2001-Fall 2023": {
        "Subject": "AERO 2001",
        "Term": "Fall 2023", 
        "Title": "Aerospace Engineering Graphical Design", 
        "Prerequisite": "Second-year status in Engineering.", 
        "LectureSections": [], 
        "LabSections": []
    },
    "SYSC 4101-Fall 2023": {
        "Subject": "SYSC 4101",
        "Term": "Fall 2023", 
        "Title": "Software Validation", 
        "Prerequisite": "SYSC 3120 or SYSC 3020.", 
        "LectureSections": [], 
        "LabSections": []
    },
    "AERO 2001-Winter 2024": {
        "Subject": "AERO 2001",
        "Term": "Winter 2024", 
        "Title": "Aerospace Engineering Graphical Design", 
        "Prerequisite": "Second-year status in Engineering.", 
        "LectureSections": [], 
        "LabSections": []
    },
    "AERO 2001-Summer 2024": {
        "Subject": "AERO 2001",
        "Term": "Summer 2024", 
        "Title": "Aerospace Engineering Graphical Design", 
        "Prerequisite": "Second-year status in Engineering.", 
        "LectureSections": [], 
        "LabSections": []
    }
}

MOCK_HTML = """
    <tbody>
        <tr class="even firstrow">
            <td class="column0">FALL TERM 2023</td> 
            <td class="column1"></td> 
        </tr>
        <tr class="odd">
            <td class="column0">October 23-27, 2023</td> 
            <td class="column1">Fall break, no classes.</td> 
        </tr>
    </tbody>
    <tbody>
        <tr class="even firstrow">
            <td class="column0">WINTER TERM 2024</td> 
            <td class="column1"></td> 
        </tr>
        <tr class="odd">
            <td class="column0">February 19-23, 2024</td> 
            <td class="column1">Winter break, no classes. </td> 
        </tr>
    </tbody>
    <tbody>
        <tr class="even firstrow">
            <td class="column0">SUMMER TERM 2024</td> 
            <td class="column1"></td> 
        </tr>
        <tr class="odd">
            <td class="column0">June 18, 2024</td> 
            <td class="column1">Last day of early summer classes. (NOTE: full summer classes resume July 2.)</td> 
        </tr>
        <tr class="odd">
            <td class="column0">July 2, 2024</td> 
            <td class="column1">Late summer classes begin and full summer classes resume. </td> 
        </tr>
    </tbody>
"""

def test_lambda_handler():
    with patch(f'{FILE_PATH}.get_parser') as mock_get_parser, \
         patch(f'{FILE_PATH}.get_classes_dict') as mock_get_classes_dict, \
         patch(f'{FILE_PATH}.write_terms_file_to_s3') as mock_write_terms_file_to_s3:
        
        mock_get_parser.return_value = BeautifulSoup(MOCK_HTML, "html.parser")
        mock_get_classes_dict.return_value = CLASSES_DICT
        mock_write_terms_file_to_s3.return_value = {"Response": json.dumps("Terms JSON written to s3 with reading week dates!")}

        lambda_handler({}, {})

        mock_get_parser.assert_called_once()
        mock_get_classes_dict.assert_called_once()
        mock_write_terms_file_to_s3.assert_called_once()


def test_get_parser():
    test_html = "<html><body>Mocked HTML</body></html>"
    expected_bs4 = BeautifulSoup(test_html, "html.parser")

    with patch("urllib3.PoolManager.request") as mock_pool_manager:
        mock_response = MagicMock()
        mock_response.data = test_html.encode()
        mock_pool_manager.return_value = mock_response

        results = get_parser()
        assert results == expected_bs4


def test_get_s3_object():
    s3_client = boto3.client("s3")
    s3_stubber = Stubber(s3_client)

    expected_params = {"Bucket": BUCKET_NAME, "Key": KEY_PATH}
    s3_stubber.add_response("get_object", {"Body": "test content"}, expected_params)

    with s3_stubber:
        result = get_s3_object("test.json")

    assert result.bucket_name == BUCKET_NAME
    assert result.key == KEY_PATH + "test.json"


def test_get_classes_dict():
    s3_object = MagicMock()
    class_dict = json.dumps(CLASSES_DICT)
    s3_object.get.return_value = {"Body": MagicMock(read=lambda: class_dict)}

    with patch(f"{FILE_PATH}.get_s3_object", return_value=s3_object) as mock_s3:
        result = get_classes_dict()
        mock_s3.assert_called_once_with("classes.json")

        assert result == CLASSES_DICT


def test_get_terms_from_class_dict():
    results = get_terms_from_class_dict(CLASSES_DICT)
    expected_terms = ["Fall 2023", "Winter 2024", "Summer 2024"]
    assert results == expected_terms


def test_get_formatted_fall_or_winter_dates():
    results = get_formatted_fall_or_winter_dates("October 23-27, 2023")
    expected_dates = ("2023-10-21", "2023-10-30", "2023-11-06")
    assert results == expected_dates

    results = get_formatted_fall_or_winter_dates("February 19-23, 2024")
    expected_dates = ("2024-02-17", "2024-02-26", "2024-03-04")
    assert results == expected_dates


def test_get_formatted_summer_dates():
    results = get_formatted_summer_dates("June 18, 2024", "July 2, 2024")
    expected_dates = ("2024-06-18", "2024-07-02", "2024-07-02")
    assert results == expected_dates


def test_write_terms_file_to_s3():
    s3_object = MagicMock()
    s3_object.put = MagicMock()

    with patch(f"{FILE_PATH}.get_s3_object", return_value=s3_object) as mock_s3:

        result = write_terms_file_to_s3(TERMS_DICT)
        mock_s3.assert_called_once_with("terms.json")

        expected_result = bytes(json.dumps(TERMS_DICT).encode("UTF-8"))
        s3_object.put.assert_called_once_with(Body=expected_result)

        assert result == {"Response": json.dumps("Terms JSON written to s3 with reading week dates!")}
