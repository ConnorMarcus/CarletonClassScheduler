from typing import List
from .model.section import Section
from .model.course import Course

# Note: filter sections (based on times, etc.) before passing to this function
# TODO: Add unit tests
def generate_schedules(courses: List[Course], current_schedule: List[Section] = []) -> List[List[Section]]:
    if len(courses) == 0:
        return [current_schedule[:]]

    res = []
    for lecture_section in courses[-1].lecture_sections:
        if is_section_schedulable(lecture_section, current_schedule):
            current_schedule.append(lecture_section)
          
            # Course has a lab/tutorial section
            # TODO: Is it possible for one lecture section to have a lab section but another doesn't?
            if courses[-1].lab_sections:
                for lab_section in courses[-1].lab_sections:
                    if can_take_together(lecture_section, lab_section) and is_section_schedulable(lab_section, current_schedule):
                        current_schedule.append(lab_section)
                        schedules = generate_schedules(courses[:-1], current_schedule)
                        res.extend(schedules)
                        current_schedule.pop()
            
            # Course has no lab/tutorial section
            else:
                schedules = generate_schedules(courses[:-1], current_schedule)
                res.extend(schedules)
            
            # remove lecture section from current schedule
            current_schedule.pop()

    return res


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

def can_take_together(lecture_section: Section, lab_section: Section) -> bool:
    '''
    Returns True if a Lecture and Lab section can be taken together,
    and False otherwise
    '''

    return lab_section.section_id in lecture_section.related_section_ids