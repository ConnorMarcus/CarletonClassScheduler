from typing import List
from .model.section import Section
from .model.course import Course

# Note: filter sections (based on times, etc.) before passing to this function
# TODO: Add unit tests
def generateSchedules(courses: List[Course], currentSchedule: List[Section] = []) -> List[List[Section]]:
    if len(courses) == 0:
        return [currentSchedule[:]]

    res = []
    for lectureSection in courses[-1].lectureSections:
        if isSectionSchedulable(lectureSection, currentSchedule):
            currentSchedule.append(lectureSection)
          
            # Course has a lab/tutorial section
            # TODO: Is it possible for one lecture section to have a lab section but another doesn't?
            if courses[-1].labSections:
                for labSection in courses[-1].labSections:
                    if canTakeTogether(lectureSection, labSection) and isSectionSchedulable(labSection, currentSchedule):
                        currentSchedule.append(labSection)
                        schedules = generateSchedules(courses[:-1], currentSchedule)
                        res.extend(schedules)
                        currentSchedule.pop()
            
            # Course has no lab/tutorial section
            else:
                schedules = generateSchedules(courses[:-1], currentSchedule)
                res.extend(schedules)
            
            # remove lecture section from current schedule
            currentSchedule.pop()

    return res


def isSectionSchedulable(section: Section, currentSchedule: List[Section]) -> bool:
    '''
    Checks if time overlaps with any time in current schedule.
    Note that if the section has no meeting times, the function will return True.
    '''
    return all(
        not time1.doesDateOverlap(time2) 
        for time1 in section.times 
        for scheduledSection in currentSchedule 
        for time2 in scheduledSection.times
    )

def canTakeTogether(lectureSection: Section, labSection: Section) -> bool:
    '''
    Returns True if a Lecture and Lab section can be taken together,
    and False otherwise
    '''

    return labSection.sectionId in lectureSection.compatibleSectionIds