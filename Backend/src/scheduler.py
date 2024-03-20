from typing import Iterable, List, Tuple
from .model.section import Section
from .model.course import Course
import itertools

MAX_SCHEDULES = 25 # Maximum number of schedules to generate (to avoid overwhelming the user)

# Note: filter sections (based on times, etc.) before passing to this function
def generate_schedules(courses: List[Course], current_schedule: List[Section] = []) -> Tuple[List[List[Section]], bool]:
    if len(courses) == 0:
        return [current_schedule[:]], False

    res = []
    for lecture_section in courses[-1].lecture_sections:
        if is_section_schedulable(lecture_section, current_schedule):
            current_schedule.append(lecture_section)
          
            # lecture section has related sections (e.g. labs) that must be taken 
            if lecture_section.related_section_ids:
                related_section_combinations = get_related_section_combinations(courses[-1], lecture_section)
                for related_sections in related_section_combinations:
                    # Must check to make sure that all related sections exists (i.e. none were filtered out)
                    if None not in related_sections and not do_section_times_overlap(related_sections) and are_sections_schedulable(related_sections, current_schedule):
                        current_schedule.extend(related_sections)
                        schedules, _ = generate_schedules(courses[:-1], current_schedule)
                        res.extend(schedules)
                        for _ in range(len(related_sections)):
                            current_schedule.pop()
            
            # There are no related sections
            else:
                schedules, _ = generate_schedules(courses[:-1], current_schedule)
                res.extend(schedules)
            
            # remove lecture section from current schedule
            current_schedule.pop()

        if len(res) >= MAX_SCHEDULES: # Limit number of schedule results
            return res, True

    return res, False


def is_section_schedulable(section: Section, current_schedule: List[Section]) -> bool:
    '''
    Checks if time overlaps with any time in current schedule.
    Note that if the section has no meeting times, the function will return True.
    '''
    return all(
        not time1.does_date_overlap(time2) 
        for time1 in section.times 
        for scheduled_section in current_schedule 
        for time2 in scheduled_section.times
    )

def are_sections_schedulable(sections: Iterable[Section], current_schedule: List[Section]) -> bool:
    '''
    Checks if a list of sections is schedulable given the current schedule.
    '''
    for section in sections:
        if not is_section_schedulable(section, current_schedule):
            return False
        
    return True

def do_section_times_overlap(sections: List[Section]) -> bool:
    '''
    Checks if a list of Sections have overlapping times.
    '''
    for i in range(len(sections)):
        for j in range(i+1, len(sections)):
            is_schedulable = all(
                not time1.does_date_overlap(time2) 
                for time1 in sections[i].times 
                for time2 in sections[j].times
            )
            if not is_schedulable:
                return True
            
    return False

def can_take_together(lecture_section: Section, lab_section: Section) -> bool:
    '''
    Returns True if a Lecture and Lab section can be taken together,
    and False otherwise
    '''
    for related_sections in lecture_section.related_section_ids:
        if lab_section.section_id in related_sections:
            return True
    
    return False


def get_related_section_combinations(course: Course, lecture_section: Section) -> List[List[Section]]:
    '''
    Gets a list combinations of "related sections" for a given lecture section.
    '''

    if course is None or lecture_section is None or not lecture_section.related_section_ids:
        raise ValueError("Parameters course and lecture_section cannot be None. Also lecture_section must not be empty.")

    related_section_id_combinations = list(itertools.product(*lecture_section.related_section_ids))
    return [[course.get_lab_section(section_id) for section_id in combination] for combination in related_section_id_combinations]