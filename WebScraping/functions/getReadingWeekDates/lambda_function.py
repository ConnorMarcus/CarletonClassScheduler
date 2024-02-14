import json
import boto3
from datetime import datetime, timedelta
import urllib3
from bs4 import BeautifulSoup
from typing import Tuple, List

BASE_URL = "https://calendar.carleton.ca/academicyear"
HTTP = urllib3.PoolManager()
BUCKET_NAME = "carletonschedulingtool"
KEY_PATH = "web-scraping-stepfunction/"

def lambda_handler(event: dict, context: dict) -> str:
    parser = get_parser()
    terms_dict = {}
    terms = get_terms_from_class_dict(get_classes_dict())
    
    for term in terms:
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

        terms_dict[term] = {
            "ReadingWeekStart": start_week,
            "ReadingWeekEnd": end_week,
            "ReadingWeekNext": next_week
        }
        
    return write_terms_file_to_s3(terms_dict)


def get_parser() -> BeautifulSoup:
    '''
    Gets the bs4 html parser.

    Returns:
    BeautifulSoup: html parser object.
    '''
    req = HTTP.request("GET", BASE_URL)
    html = req.data.decode("utf-8")
    return BeautifulSoup(html, "html.parser")


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


def get_classes_dict() -> dict:
    '''
    Gets the dict of classes from s3.
    
    Returns:
    dict: terms course dict.
    '''
    classes_file = get_s3_object("classes.json")
    return json.load(classes_file.get()["Body"])


def get_terms_from_class_dict(classes_dict: dict) -> List:
    '''
    Gets the terms from a class dictionary.

    Parameters: 
    classes_dict: The dictionary used.

    Returns: 
    list: list of the terms obtained.
    '''
    term_lst = []
    for course in classes_dict:
        term = classes_dict[course]['Term']
        if not term in term_lst:
            term_lst.append(term)

    return term_lst


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


def write_terms_file_to_s3(terms_dict: dict) -> str:
    '''
    Writes terms file to S3.

    Parameters: 
    updated_terms_courses: dictionary of containing terms with courses and reading week dates.

    Returns:
    str: Message indicating the terms and courses file has been updated.
    '''
    terms_file = get_s3_object("terms.json")
    terms_file.put(Body=(bytes(json.dumps(terms_dict).encode("UTF-8"))))
    
    return {
        "Response": json.dumps("Terms JSON written to s3 with reading week dates!")
    }
