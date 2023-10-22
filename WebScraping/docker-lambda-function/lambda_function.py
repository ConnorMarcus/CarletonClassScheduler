from selenium import webdriver
from tempfile import mkdtemp
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import re


def handler(event=None, context=None):
    options = webdriver.ChromeOptions()
    service = webdriver.ChromeService("/opt/chromedriver")

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
    driver.implicitly_wait(5)
    driver.get("https://central.carleton.ca/prod/bwysched.p_select_term?wsea_code=EXT")

    hrefs = set()

    # Find the term dropdown element and select it
    term_dropdown = (driver.find_element(By.NAME,"term_code"))
    terms = [term.get_attribute("value") for term in Select(term_dropdown).options]

    for term in terms:

        term_dropdown = (driver.find_element(By.NAME,"term_code"))

        Select(term_dropdown).select_by_value(term)

        # Click on "Proceed to search"
        proceed_button = driver.find_element(By.XPATH, '//*[@id="ws_div"]/input')
        proceed_button.click()

        # Find the subject dropdown element and select it
        subject_dropdown = driver.find_element(By.ID, "subj_id")
        options = [option.get_attribute("value") for option in Select(subject_dropdown).options]


        for option in options:

            # Find the subject dropdown element 
            subject_dropdown = driver.find_element(By.ID, "subj_id")

            if option == "":
                continue

            Select(subject_dropdown).deselect_by_index(0)
            Select(subject_dropdown).select_by_value(option)

            # Click on "Search"
            search_button = driver.find_element(By.XPATH, "/html/body/section/section/form/table/tbody/tr[5]/td/input[1]")
            search_button.click()

            #Grab Neccessary Content HERE
            html_page = driver.page_source
            soup = BeautifulSoup(html_page, "html.parser")
            anchors = soup.find_all('a', attrs={'href': re.compile("bwysched.p_display_course?")})

            for anchor in anchors:
                hrefs.add(anchor.get("href"))

            # When done, click on "Return to Search"
            search_button = driver.find_element(By.NAME, "search_selected")
            search_button.click()


        # Select change term 
        change_term = driver.find_element(By.XPATH,"/html/body/section/section/form/table/tbody/tr[5]/td/input[4]")
        change_term.click()


    return {"hrefs": list(hrefs)}