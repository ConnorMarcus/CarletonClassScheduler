from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from bs4 import BeautifulSoup
from unicodedata import normalize
from typing import List
import json
import boto3
import re   

PAGE_SOURCE = "https://central.carleton.ca/prod/bwysched.p_select_term?wsea_code=EXT"
CHROME_SERVICE_EXE_PATH = "/opt/chromedriver"
SEARCH_XPATH = r'//*[@id="ws_div"]/input'
CHANGE_TERM_BTN_XPATH = "/html/body/section/section/form/table/tbody/tr[5]/td/input[4]"
SEARCH_BTN_XPATH = "/html/body/section/section/form/table/tbody/tr[5]/td/input[1]"
RETURN_TO_SEARCH_XPATH = "/html/body/section/section/form/table/tbody/tr[5]/td/input[2]"
HREF_STR = "bwysched.p_display_course?"
LINKED_COURSE_STR = "https://carleton.ca/registrar/registration/terminology/"
BUCKET_NAME = "carletonschedulingtool"
KEY_PATH = "web-scraping-stepfunction/href_list.json"

def handler(event=None, context=None) -> str:
    '''
    AWS Lambda handler function for navigating through the external Carleton course
    registration page. This function creats a list of hrefs for each course for each
    term.

    Parameters: 
    - event: event that triggers the Lambda function. By default it is None.
    - context: the Lambda function execution context. By default it is None.

    Returns: 
    - str: A message indicating that handler has written the hrefs to the S3 bucket.
    '''
    driver = init()

    class_info = []

    wait = WebDriverWait(driver, 10)

    terms = scrape_terms(driver)
    
    for term in terms:

        select_terms(driver, term)

        options = scrape_course_options(driver)

        for option in options:

            if option == "":
                continue

            select_options(driver, option)

            wait.until(EC.presence_of_element_located((By.TAG_NAME, 'form')))

            # Grab course href and linked courses
            parse(driver.page_source, class_info)

            # When done, click on "Return to Search"
            click_btn(driver, By.NAME, "search_selected")

        # Select change term 
        click_btn(driver, By.XPATH, CHANGE_TERM_BTN_XPATH)

    s3 = boto3.resource("s3")
    href_list_file = s3.Object(BUCKET_NAME, KEY_PATH)
    href_list_file.put(Body=(bytes(json.dumps(class_info).encode("UTF-8"))))
    
    return "Href list written to S3"

def init() -> webdriver:
    '''
    Initializes the chrome webdriver with multiple options.

    Returns:
    - Webdriver Object: The chrome webdriver object.
    '''
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService(CHROME_SERVICE_EXE_PATH)

    options.binary_location = '/opt/chrome/chrome'
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-gpu")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-dev-tools")
    options.add_argument("--no-zygote")
    options.add_argument(f"--user-data-dir={mkdtemp()}")
    options.add_argument(f"--data-path={mkdtemp()}")
    options.add_argument(f"--disk-cache-dir={mkdtemp()}")
    options.add_argument("--remote-debugging-port=9222")

    driver = webdriver.Chrome(options=options, service=service)
    driver.get(PAGE_SOURCE)
    
    return driver

def scrape_terms(driver: webdriver) -> List:
    '''
    Scrapes the available terms from the Carleton Webpage.

    Parameters:
    - driver: The Chrome WebDriver object.

    Returns:
    - List: A list of term values obtained from the term dropdown on the webpage.
    '''
    # Find the term dropdown element and select it
    term_dropdown = (driver.find_element(By.NAME, "term_code"))
    return [term.get_attribute("value") for term in Select(term_dropdown).options]

def scrape_course_options(driver: webdriver) -> List:
    '''
    Scrapes the available course options from the Carleton Webpage.

    Parameters:
    - driver: The Chrome WebDriver object.

    Returns:
    - List: A list of course options obtained from the subject dropdown on the webpage.
    '''
    # Find the subject dropdown element and select it
    subject_dropdown = driver.find_element(By.ID, "subj_id")
    return [option.get_attribute("value") for option in Select(subject_dropdown).options]


def select_undergrad(driver: webdriver) -> None:
    '''
    Selects the Undergraduate course level on a webpage using the Chrome WebDriver.

    Parameters:
    - driver: The Chrome WebDriver object.
    '''
    # Find Course Level field and select Undergraduate 
    course_level = driver.find_element(By.ID, "levl_id")
    select_dropdown_by_value(driver, course_level, "UG")

    sleep(0.25)

def parse(html_page: BeautifulSoup, lst: List) -> List:
    '''
    Parses the course pages list using Beautiful soup and extracts "Also Register in information.

    Parameters:
    - html_page : The HTML content of the page to be parsed.
    - lst : The list to which the extracted information will be appended.

    Returns:
    - List: The updated list containing dictionaries with information about linked courses.
    '''
    soup = BeautifulSoup(html_page, "html.parser")
    anchors = soup.find_all("a", attrs={"href": re.compile(HREF_STR)}, string={re.compile("^\d+$")})

    for anchor in anchors:
        parent = anchor.find_parent("tr")
        if parent:
            bg_colour = parent.get("bgcolor")
            cur_tr = parent.find_next("tr")
            class_dict = {"href": anchor.get("href"), "also_register": ""}
            while bg_colour == cur_tr.get("bgcolor"):
                linked_course = cur_tr.find(attrs={"href": re.compile(LINKED_COURSE_STR)})
                if linked_course: 
                    linked_course_text = linked_course.parent.parent.text.split("Also Register in:")[-1].strip()
                    normalized_text = normalize("NFKD", linked_course_text)
                    class_dict["also_register"] = normalized_text
                    break

                cur_tr = cur_tr.find_next("tr")

            lst.append(class_dict)

    return lst

def click_btn(driver: webdriver, type: str, name: str) -> None:
    '''
    Cliks a button on the webpage. 

    Parameters: 
    - driver: The Chrome WebDriver object.
    - type: the string type of element (eg. By.ID, By.NAME).
    - name: the string value of the element.
    '''
    search_button = driver.find_element(type, name)
    search_button.click()

def select_terms(driver: webdriver, term: str) -> None:
    '''
    Select a specific term on the webpage. 

    Parameters: 
    - driver: The Chrome WebDriver object.
    - term: The string value of the term to be selected.
    '''
    term_dropdown = (driver.find_element(By.NAME, "term_code"))

    select_dropdown_by_value(driver, term_dropdown, term)

    Select(term_dropdown).select_by_value(term)

    # Click on "Proceed to search"
    click_btn(driver, By.XPATH, SEARCH_XPATH)

    select_undergrad(driver)

def select_options(driver: webdriver, option: str) -> None:
    '''
    Selects a specific course option from subject dropdown. 

    Parameters: 
    - driver: The Chrome WebDriver object.
    - option: The string course option
    '''
    # Find the subject dropdown element 
    subject_dropdown = driver.find_element(By.ID, "subj_id")

    select_undergrad(driver)

    select_dropdown_by_value(subject_dropdown, option, True)

    # Click on "Search"
    click_btn(driver, By.XPATH, SEARCH_BTN_XPATH)

def select_dropdown_by_value(element: object, value: str, is_subject=False) -> None:
    '''
    Creates a Select class object and selects a value given an element

    Parameters:
    - element: The WebElement object
    - value: string value that is to be selected
    - is_subject: is element a subject dropdown, set to False by default
    '''
    select_element = Select(element)

    if is_subject:
        select_element.deselect_by_visible_text("All Subjects")

    select_element.select_by_value(value)