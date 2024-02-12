import json
import boto3
from datetime import datetime, timedelta
import urllib3
from bs4 import BeautifulSoup
from typing import Tuple

BASE_URL = "https://calendar.carleton.ca/academicyear"
HTTP = urllib3.PoolManager()
BUCKET_NAME = "carletonschedulingtool"
KEY_PATH = "web-scraping-stepfunction/terms_courses.json"

def lambda_handler(event: dict, context: dict) -> str:
    parser = get_parser()
    terms_courses_dict = get_terms_courses_dict()
    
    for term in terms_courses_dict.keys():
        name, year = term.split()
        term_search_str = f"{name.upper()} TERM {year}"
        term_tbody = parser.find("td", string=term_search_str).find_parent("tbody")

        if name == "Fall" or name == "Winter":
            break_lookup_str = f"{name} break"
            date = term_tbody.find(lambda tag: tag.name == "td" and break_lookup_str in tag.text).find_previous('td').text.strip()
            
            start_week, end_week, next_week = get_formatted_fall_or_winter_dates(date)

        else:
            start_lookup_str ="Last day of early summer classes"
            start_date = term_tbody.find(lambda tag: tag.name == "td" and start_lookup_str in tag.text).find_previous('td').text.strip()
            
            end_lookup_str = "Late summer classes begin"
            end_date = term_tbody.find(lambda tag: tag.name == "td" and end_lookup_str in tag.text).find_previous('td').text.strip()
            
            start_week, end_week, next_week = get_formatted_summer_dates(start_date, end_date)


        terms_courses_dict[term]["ReadingWeekStart"] = start_week
        terms_courses_dict[term]["ReadingWeekEnd"] = end_week
        terms_courses_dict[term]["ReadingWeekNext"] = next_week
        
    return write_terms_courses_to_s3(terms_courses_dict)


def get_parser() -> BeautifulSoup:
    '''
    Gets the bs4 html parser.

    Returns:
    BeautifulSoup: html parser object.
    '''
    req = HTTP.request("GET", BASE_URL)
    html = req.data.decode("utf-8")
    return BeautifulSoup(html, "html.parser")


def get_terms_courses_s3_object() -> object:
    '''
    Gets the terms courses s3 file object.

    Returns:
    S3 Object: The s3 file object.
    '''
    s3 = boto3.resource("s3")
    return s3.Object(BUCKET_NAME, KEY_PATH)
    

def get_terms_courses_dict() -> dict:
    '''
    Gets the list of classes from s3.
    
    Returns:
    dict: terms course dict.
    '''
    terms_courses_file = get_terms_courses_s3_object()
    return json.load(terms_courses_file.get()["Body"])


def get_formatted_fall_or_winter_dates(date_str: str) -> Tuple[str, str, str]:
    '''
    Formats fall or winter term reading week dates. 

    Parameters:
    date_str: The string of the data that is to be formattted.

    Returns:
    Tuple: the formatted date start, end and next dates.
    '''
    month_str, start_end_str, year_str = date_str.split()
    month = datetime.strptime(month_str, '%B').month
    start_day = int(start_end_str.split('-')[0])
    end_day = int(start_end_str.split('-')[1][:-1])
    year = int(year_str)

    start_date = (datetime(year, month, start_day) + timedelta(days=-2)).date().isoformat() 
    end_date =(datetime(year, month, end_day) + timedelta(days=3)).date().isoformat() 
    next_date = (datetime(year, month, end_day) + timedelta(days=10)).date().isoformat() 

    return start_date, end_date, next_date


def get_formatted_summer_dates(start_date: str, end_date: str) -> Tuple[str, str, str]:
    '''
    Formats the summer term reading week dates. 

    Parameters:
    start_date: The string start date that is to be formattted
    start_date: The string end date that is to be formattted

    Returns:
    Tuple: the formatted date start, end and next dates.
    '''
    parsed_format = "%B %d, %Y"
    formatted_format = "%Y-%m-%d"

    parsed_start_date = datetime.strptime(start_date, parsed_format)
    formatted_start_date = parsed_start_date.strftime(formatted_format)

    parsed_end_date = datetime.strptime(end_date, parsed_format)
    formatted_end_date = parsed_end_date.strftime(formatted_format)

    return formatted_start_date, formatted_end_date, formatted_end_date


def write_terms_courses_to_s3(updated_terms_courses: dict[str, str]) -> str:
    '''
    Writes updated terms courses file to S3.

    Parameters: 
    updated_terms_courses: dictionary of containing terms with courses and reading week dates.

    Returns:
    str: Message indicating the terms and courses file has been updated.
    '''
    terms_courses_file = get_terms_courses_s3_object()
    terms_courses_file.put(Body=(bytes(json.dumps(updated_terms_courses).encode("UTF-8"))))
    
    return {
        "Response": json.dumps("Reading week dates added to Terms and Course file!")
    }
