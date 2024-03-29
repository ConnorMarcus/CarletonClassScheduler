import json
from typing import List, Tuple
from typing import Union
import boto3
import urllib3
from bs4 import BeautifulSoup
import concurrent.futures
import threading
from datetime import datetime

BUCKET_NAME = "carletonschedulingtool"
KEY_PATH = "web-scraping-stepfunction/"
BASE_URL = "https://central.carleton.ca/prod/"
TERM_START_MONTHS = ["May", "Sep", "Jan"]
EARLY_TERM_END_MONTHS = ["Jun", "Oct", "Feb"]
HTTP = urllib3.PoolManager()
LOCK = threading.Lock()
classes = {}

def lambda_handler(event: dict, context: object) -> str:
    # Get the hrefs list file from s3
    href_list_file = get_s3_object("href_list.json")
    hrefs = json.load(href_list_file.get()["Body"])
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        executor.map(get_data, hrefs)
    
    # Write the classes dict into s3
    classes_file = get_s3_object("classes.json")
    classes_file.put(Body=(bytes(json.dumps(classes).encode("UTF-8"))))

    return {
        "Response": json.dumps("classes JSON written to s3")
    }


def get_s3_object(filename: str) -> object:
    '''
    Gets the s3 file object where the href list and classes files are.
    
    Parameters:
    filename: The filename of the object to get.
    
    Returns
    S3 Object: The s3 file object.
    '''
    s3 = boto3.resource("s3")
    return s3.Object(BUCKET_NAME, KEY_PATH + filename)


def get_data(href_dict: dict) -> object:
    '''
    Gets the data of the course page by making a GET request to Carleton Public classes website.
    
    Parameters:
    href_dict: The href dict which contains the href and also register in string.
    '''
    
    url = href_dict["href"]
    req = HTTP.request("GET", BASE_URL + url)
    html = req.data.decode("utf-8")
    parse_data(BeautifulSoup(html, "html.parser"), href_dict["also_register"])


def parse_data(html: BeautifulSoup, also_register_str: str) -> None:
    '''
    Handles parsing the data of the html course page.

    Parameters:
    html: The html parser of course page.
    '''
    term =  " ".join(html.find("td", string="Registration Term:").find_next("td").text.strip().split(" ")[:2])
    crn = html.find("td", string="CRN:").find_next("td").text.strip()
    title = html.find("td", string="Long Title:").find_next("td").text.strip()
    status = html.find("u", string="Status:").parent.parent.parent.find_next("td").text.strip()
    subject_list = html.find("td", string="Subject:").find_next("td").text.strip().split(" ")
    course_description = html.find("td", string="Course Description:").find_next("td").text.strip()
    section_info = html.find("td", string="Section Information:").find_next("td").text.strip()
    
    subject_code = " ".join(subject_list[:2])
    section_id = subject_list[-1]

    preq = get_prerequisite(course_description)
    section_type = get_section_type(section_info)

    meeting_date_rows = html.find_all("table")[1].find_all("tr")
    instructor = get_instructor(meeting_date_rows[1].find_all("td"), len(meeting_date_rows[0].find_all("td")) - 1)
    meeting_dates = get_meeting_date_list(meeting_date_rows[1:])
    also_register_list = get_associated_sections(also_register_str)
    term_date_str = meeting_date_rows[1].find_all("td")[0].text.strip()
    term_duration = get_term_duration_str(term_date_str)
    start_date, end_date = get_formatted_term_dates(term_date_str)

    add_class(
        term=term, crn=crn, subject_code=subject_code, section_id=section_id, title=title, 
        preq=preq, status=status, section_type=section_type, instructor=instructor, 
        meeting_dates=meeting_dates, also_register_list=also_register_list, 
        term_duration=term_duration, start_date=start_date, end_date=end_date
    )


def add_class(**kwargs: dict) -> None:
    '''
    Adds a class to the shared classes dictionary.

    Parameters:
    **kwargs: Key value pairs of course data from parsing.
    '''
    key = f"{kwargs['subject_code']}-{kwargs['term']}"

    # Create section dict
    section_json = {
        "SectionID": kwargs["section_id"], "CRN": kwargs["crn"], 
        "Status": kwargs["status"], "SectionType": kwargs["section_type"], 
        "Instructor": kwargs["instructor"], "MeetingDates": kwargs["meeting_dates"],
        "TermDuration": kwargs["term_duration"], "AlsoRegister": kwargs["also_register_list"],
        "StartDate": kwargs["start_date"], "EndDate": kwargs["end_date"]
    }

    # Aquire lock to write into shared classes dict
    with LOCK:

        # Create new subject-term dict
        if key not in classes:
            classes[key] = {
                    "Subject": kwargs["subject_code"], "Term": kwargs["term"], 
                    "Title": kwargs["title"], "Prerequisite": kwargs["preq"], 
                    "LectureSections": [], "LabSections": []
                }

        # Add lecture/lab section to subject-term dict
        add_section_to_class(key, section_json)


def add_section_to_class(key: str, section: dict) -> None:
    '''
    Adds a Lecture/Lab section to a class with the key.

    Parameters:
    key: The string key of the class which the section is added to.
    section: The dict section to append to the Lecture or Lab sections. 
    '''
    section_id = section["SectionID"]

    if is_lecture_section(section_id):
        section_type = "LectureSections"

    else:
        section_type = "LabSections"
        week_schedule = get_lab_week_schedule(section["SectionID"])
        section["WeekSchedule"] = week_schedule

    classes[key][section_type].append(section)


def is_lecture_section(section_id) -> bool:
    '''
    Checks if section is a lecture.

    Parameters:
    section_id: The string section id.

    Returns:
    bool: True if lecture section (otherwise lab section).
    '''
    return len(section_id) == 1


def has_keyword_in_text(keyword: Union[str, List[str]], text: str) -> bool:
    '''
    Checks whether a keyword is a text.

    Parameters:
    keyword: The string keyword to check for.
    text: The string text to look for the keyword in.

    Returns:
    bool: True if keyword present otherwise False.
    '''
    if type(keyword) == list:
        for word in keyword:
            if word in text:
                return True

        return False

    return keyword in text


def get_prerequisite(description: str) -> str:
    '''
    Gets the prerequisite string.

    Parameters:
    description: The string course description containing the prerequisite string.

    Returns:
    str: The parsed prerequisite string or empty string (when no prerequisite(s)).
    '''
    keyword = "Prerequisite(s): "

    if has_keyword_in_text(keyword, description):
        # Need replace \u00a0 (aka &nbsp) from text if present
        return description.split(keyword)[-1].replace('\u00a0', " ")

    return ""


def get_section_type(section_info: str) -> str:
    '''
    Gets the section type of a Lecture or Lab section.

    Parameters:
    section_info: The string section information containing type.

    Returns:
    str: 'In person' or 'Online' (depending on type).
    '''
    return "In person" if has_keyword_in_text("IN-PERSON", section_info) else "Online"


def get_instructor(td_list: List[BeautifulSoup], index: int):
    '''
    Gets the instructor of a Lecture or Lab section.

    Parameters:
    td_list: The list of <td> elements where the instructor string is.
    index: The index of the instructor td.

    Returns:
    str: The instructor of the section or empty string (when no instructor). 
    '''
    try:
        return td_list[index].text.strip().split(" (Primary)")[0]

    except IndexError:
        return ""


def get_meeting_date_list(rows: List[BeautifulSoup]) -> List[dict]:
    '''
    Gets the list of meeting dates of a Lecture or Lab section.

    Parameters:
    rows: The list of <tr> elements of the meeting dates.

    Returns:
    List[dict]: A list of dicts of the meeting dates.
    '''
    meeting_list = []

    for row in rows:
        # Get the days and time string
        td_list = row.find_all("td")
        days_str = td_list[1].text.strip()
        time_str = td_list[2].text.strip()

        # When both strings are NOT NONE
        if days_str and time_str:
            days_list = days_str.split(" ")
            time_list = time_str.split(" - ")
            start_time, end_time = time_list[0], time_list[-1]

            # Loop over days and create separate meeting dicts
            for day in days_list:
                meeting_dict = {"DayOfWeek": day, "StartTime": start_time, "EndTime": end_time}

                # Restrict duplicate meeting dicts (Edge case)
                if meeting_dict not in meeting_list:
                    meeting_list.append(meeting_dict)

    return meeting_list


def get_associated_sections(also_register_str: str) -> List[List[str]]:
    '''
    Gets the list of associated sections based on the also_register_str.

    Parameters:
    also_register_str: The also register string of section.

    Returns:
    List[List[str]]: The list of associated sections.
    '''
    also_register_sections = []
    
    if not also_register_str:
        return also_register_sections

    for string in also_register_str.split("and"):
        split_or_list = string.split("or")
        sections_list = [split_or_list[i].strip().split(" ")[-1] for i in range(len(split_or_list))]
        also_register_sections.append(sections_list)

    return also_register_sections


def get_term_duration_str(term_date: str) -> str:
    '''
    Gets the term duration_str based on the term_date.

    Parameters:
    term_date: The term date string of the section.

    Returns:
    str: Term duration string of the section.
    '''

    if has_keyword_in_text(TERM_START_MONTHS, term_date):

        if has_keyword_in_text(EARLY_TERM_END_MONTHS, term_date):
            return "Early Term"
        
        return "Full Term"
    
    return "Late Term"


def get_lab_week_schedule(section_id: str) -> str:
    '''
    Gets the week schedule for a lab section.

    Parameters:
    section_id: The string lab section id.

    Returns:
    str: Week schedule string for the section.
    '''
    if section_id[-1] == "O":
        return "Odd Week"

    elif section_id[-1] == "E":
        return "Even Week"

    else:
        return "Every Week"

    
def get_formatted_term_dates(term_date: str) -> Tuple[str, str]:
    '''
    Gets the formatted start and end dates.

    Parameters:
    term_date: The term date string of the section.

    Returns:
    Tuple(str, str): A tuple of the start and end dates.
    '''
    # Check if the term date string is not empty
    if term_date:
        parsed_format = "%b %d, %Y"
        formatted_format = "%Y-%m-%d"

        date_list = term_date.split(" to ")
        parsed_start_date = datetime.strptime(date_list[0], parsed_format)
        parsed_end_date = datetime.strptime(date_list[-1], parsed_format)

        formatted_start_date = parsed_start_date.strftime(formatted_format)
        formatted_end_date = parsed_end_date.strftime(formatted_format)

        return formatted_start_date, formatted_end_date

    return "", ""