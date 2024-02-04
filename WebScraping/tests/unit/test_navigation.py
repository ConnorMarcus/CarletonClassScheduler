from unittest.mock import patch, MagicMock, call
from WebScraping.functions.navigation.lambda_function import *
import os

FILE_PATH = "WebScraping.functions.navigation.lambda_function"

def test_handler():
    with patch('selenium.webdriver.Chrome') as mock_webdriver, \
         patch('boto3.resource') as mock_boto3_resource, \
         patch(f'{FILE_PATH}.scrape_terms') as mock_scrape_terms, \
         patch(f'{FILE_PATH}.select_terms') as mock_select_terms, \
         patch(f'{FILE_PATH}.scrape_course_options') as mock_scrape_course_options, \
         patch(f'{FILE_PATH}.select_options') as mock_select_options, \
         patch(f'{FILE_PATH}.parse') as mock_parse, \
         patch(f'{FILE_PATH}.click_btn') as mock_click_btn: 
        

        mock_driver_instance = MagicMock()
        mock_webdriver.return_value = mock_driver_instance
        mock_select_element = MagicMock()
        mock_select_element.tag_name = 'select'
        mock_scrape_terms.return_value = ['term1', 'term2']
        mock_scrape_course_options.return_value = ['option1', 'option2', '']
        mock_driver_instance.find_element.return_value = mock_select_element
        with patch('boto3.resource') as mock_boto3_client:
            mock_s3_instance = MagicMock()
            mock_boto3_client.return_value = mock_s3_instance 
            mock_event = {}
            mock_context = {}

            response = handler(mock_event, mock_context)

            assert response == "Href list written to S3", "Handler response did not match expected response."
            mock_webdriver.assert_called_once()
            mock_boto3_client.assert_called_once_with('s3')
            mock_scrape_terms.assert_called_once_with(mock_driver_instance)
            assert mock_select_terms.call_count == 2
            assert mock_scrape_course_options.call_count == 2
            assert mock_select_options.call_count == 4


def test_init():
    with patch('selenium.webdriver.Chrome') as mock_driver:
        
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance

        webdriver = init()

        mock_driver.assert_called_once()
        _, kwargs = mock_driver.call_args
        assert '--headless' in kwargs['options'].arguments, "Webdriver not initialized with headless option."
        mock_driver_instance.get.assert_called_once_with(PAGE_SOURCE)
        assert webdriver is not None


def test_scrape_terms():
    with patch('selenium.webdriver.Chrome') as mock_driver:
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance

        mock_select_element = MagicMock()
        mock_select_element.tag_name = 'select'

        mock_option1 = MagicMock()
        mock_option1.get_attribute.return_value = "Fall 2023 (September-December)"
        mock_option2 = MagicMock()
        mock_option2.get_attribute.return_value = "Winter 2024 (January-April)"
        mock_option3 = MagicMock()
        mock_option3.get_attribute.return_value = "Summer 2024 (May-August)"
        
        mock_select_element.find_elements.return_value = [mock_option1, mock_option2, mock_option3]
        mock_driver_instance.find_element.return_value = mock_select_element

        result = scrape_terms(mock_driver_instance)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result == ["Fall 2023 (September-December)", "Winter 2024 (January-April)", "Summer 2024 (May-August)"]    


def test_select_terms():
    with patch('selenium.webdriver.Chrome') as mock_driver, \
        patch(f'{FILE_PATH}.select_dropdown_by_value') as mock_select_dropdown:

        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance

        mock_term_dropdown = MagicMock()
        mock_term_dropdown.tag_name = 'select'
        mock_driver_instance.find_element.return_value = mock_term_dropdown

        mock_option_fall = MagicMock()
        mock_option_fall.get_attribute.return_value = "202009"
        mock_option_winter = MagicMock()
        mock_option_winter.get_attribute.return_value = "202101"
        mock_term_dropdown.find_elements.return_value = [mock_option_fall, mock_option_winter]

        select_terms(mock_driver_instance, "202009")

        assert mock_driver_instance.find_element.call_count == 3
        assert mock_select_dropdown.call_count == 2
        find_mock_calls = mock_select_dropdown.mock_calls
        expected_call = [call.find_element(mock_driver_instance, mock_term_dropdown, "202009")]
        assert expected_call in find_mock_calls


def test_srape_course_options():
    with patch('selenium.webdriver.Chrome') as mock_driver:
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance

        mock_select_element = MagicMock()
        mock_select_element.tag_name = 'select'

        mock_option1 = MagicMock()
        mock_option1.get_attribute.return_value = "ACCS"
        mock_option2 = MagicMock()
        mock_option2.get_attribute.return_value = "ACCT"
        mock_option3 = MagicMock()
        mock_option3.get_attribute.return_value = "AERO"

        mock_select_element.find_elements.return_value = [mock_option1, mock_option2, mock_option3]
        mock_driver_instance.find_element.return_value = mock_select_element

        result = scrape_course_options(mock_driver_instance)

        assert isinstance(result, list)
        assert len(result) == 3
        assert result == ["ACCS", "ACCT", "AERO"]    


def test_select_options():
    with patch('selenium.webdriver.Chrome') as mock_driver, \
        patch(f'{FILE_PATH}.select_dropdown_by_value') as mock_select_dropdown:

        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance

        mock_subject_dropdown = MagicMock()
        mock_subject_dropdown.tag_name = 'select'
        mock_driver_instance.find_element.return_value = mock_subject_dropdown

        mock_option_all = MagicMock()
        mock_option_all.get_attribute.return_value = ""
        mock_option_accs = MagicMock()
        mock_option_accs.get_attribute.return_value = "ACCS"
        mock_option_acct = MagicMock()
        mock_option_acct.get_attribute.return_value = "ACCT"
        mock_subject_dropdown.find_elements.return_value = [mock_option_all, mock_option_accs, mock_option_acct]
        mock_driver_instance.find_element.return_value = mock_subject_dropdown
            
        sample_option = "ACCT"
        select_options(mock_driver_instance, sample_option)

        find_method_calls = mock_driver_instance.method_calls
        expected_call = [call.find_element(By.ID, "subj_id")]
        assert expected_call in find_method_calls
        assert mock_select_dropdown.call_count == 2
        find_mock_calls = mock_select_dropdown.mock_calls
        expected_call = [call.find_element(mock_subject_dropdown, sample_option, True)]
        assert expected_call in find_mock_calls


def test_parse():
    html_file_path = os.path.join(os.path.dirname(__file__), "..", "utils", "sysc_courses.html")
    with open(html_file_path,"r", encoding="utf8") as file: 
        html_content = file.read()

    mock_lst = []
    HREF_STR = "bwysched.p_display_course?wsea_code=EXT&term_code=202330&disp=20397083&crn=35539"
    HREF_STR2 =  "bwysched.p_display_course?wsea_code=EXT&term_code=202330&disp=20397083&crn=35540"
    HREF_STR3 = "bwysched.p_display_course?wsea_code=EXT&term_code=202330&disp=20397083&crn=35541"
    LINKED_COURSE_STR = "SYSC 2006 L10 or L2 or L3 or L4 or L5 or L6 or L8"  

    result_list = parse(html_content, mock_lst)

    assert len(result_list) > 0
    assert {"href": HREF_STR, "also_register": LINKED_COURSE_STR} in result_list
    assert {"href": HREF_STR2, "also_register": LINKED_COURSE_STR} in result_list
    assert {"href": HREF_STR3, "also_register": LINKED_COURSE_STR} in result_list


def test_parse_no_parent():
    error_case = '''
    <html>
        <body>
            <table>
                <a href="bwysched.p_display_course?wsea_code=EXT&amp;term_code=202330&amp;disp=20397083&amp;crn=35540" target="_blank">35540</a>
                <a href="bwysched.p_display_course?wsea_code=EXT&amp;term_code=202330&amp;disp=20397083&amp;crn=35541" target="_blank">35541</a>
            </table>
        </body>
    </html>
    '''
    mock_lst =[]
    result_list = parse(error_case, mock_lst)
    print(result_list)
    assert len(result_list) == 0

def test_click_btn():
    with patch('selenium.webdriver.Chrome') as mock_driver:
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance
        mock_element = MagicMock()
        mock_driver_instance.find_element.return_value = mock_element
        element_type = By.ID
        element_name = "test_button_id"

        click_btn(mock_driver_instance, element_type, element_name)

        mock_driver_instance.find_element.assert_called_once_with(element_type, element_name)
        mock_element.click.assert_called_once()

def test_select_undergrad():
    with patch('selenium.webdriver.Chrome') as mock_driver, \
        patch(f'{FILE_PATH}.select_dropdown_by_value') as mock_select_dropdown:
        mock_driver_instance = MagicMock()
        mock_driver.return_value = mock_driver_instance

        mock_course_level_dropdown = MagicMock()
        mock_course_level_dropdown.tag_name = 'select'
        mock_driver_instance.find_element.return_value = mock_course_level_dropdown

        mock_option_all = MagicMock()
        mock_option_all.get_attribute.return_value = ""
        mock_option_ug = MagicMock()
        mock_option_ug.get_attribute.return_value = "UG"
        mock_option_gr = MagicMock()
        mock_option_gr.get_attribute.return_value = "GR"
        mock_course_level_dropdown.find_elements.return_value = [mock_option_all, mock_option_ug, mock_option_gr]

        select_undergrad(mock_driver_instance)

        mock_driver_instance.find_element.assert_called_once_with(By.ID, "levl_id")
        mock_select_dropdown.assert_called_once_with(mock_driver_instance, mock_course_level_dropdown, "UG")

def test_select():
    with patch(f"{FILE_PATH}.Select") as mock_select:
        mock_select_instance = MagicMock()
        mock_select.return_value = mock_select_instance

        mock_course_level_dropdown = MagicMock()
        mock_course_level_dropdown.tag_name = 'select'

        mock_option_all = MagicMock()
        mock_option_all.get_attribute.return_value = ""
        mock_option_ug = MagicMock()
        mock_option_ug.get_attribute.return_value = "UG"
        mock_option_gr = MagicMock()
        mock_option_gr.get_attribute.return_value = "SYSC"
        select_dropdown_by_value(mock_course_level_dropdown, "UG")
        select_dropdown_by_value(mock_course_level_dropdown, "SYSC", True)

        assert mock_select.call_count == 2
