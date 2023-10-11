from typing import List
from model.section import Section
from model.course import Course
from model.date import Date
from model.dayOfWeek import DayOfWeek

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

    # TODO: implement whether a given lab and lecture section can be taken together
    return True

if __name__=="__main__":
    d1 = Date(DayOfWeek.MONDAY, "11:00", "12:00")
    d2 = Date(DayOfWeek.WEDNESDAY, "11:00", "12:00")
    d3 = Date(DayOfWeek.WEDNESDAY, "12:00", "13:00")
    section1A = Section("1A", "1234", "Prof. Jones", [d1, d2], "")
    section1LA = Section("1LA", "321", "Prof. Jones", [d3], "")
    course1 = Course("SYSC 4001", "", "Fall 2023", "", [section1A], [section1LA])

    d4 = Date(DayOfWeek.TUESDAY, "11:00", "12:00")
    d5 = Date(DayOfWeek.THURSDAY, "11:00", "12:00")
    d6 = Date(DayOfWeek.MONDAY, "09:00", "10:00")
    d7 = Date(DayOfWeek.WEDNESDAY, "09:00", "10:00")
    section2A = Section("2A", "567", "Prof. Jones", [d4, d5], "")
    section2B = Section("2B", "567", "Prof. Jones", [d6, d7], "")
    course2 = Course("SYSC 4120", "", "Fall 2023", "", [section2A, section2B], [])

    print(generateSchedules([course1, course2]))