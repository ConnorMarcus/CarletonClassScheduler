from enum import Enum

class WeekSchedule(Enum):
    '''
    Specifies if a class/lab occurs every week, on even weeks only, or on odd weeks only.
    '''
    
    EVEN_WEEK = "Even Week"
    ODD_WEEK = "Odd Week"
    EVERY_WEEK = "Every Week"