// Formatting functions 

export const parseInputs = (inputs) => {
    const courses = [
        inputs.course1,
        inputs.course2,
        inputs.course3,
        inputs.course4,
        inputs.course5,
        inputs.course6,
        inputs.course7,
        inputs.course8,
        inputs.course9,
    ].filter(course => course.trim() !== '');

    // Only add non-empty filters
    const filters = {};
    if (inputs.noClassBefore) {
        filters.BeforeTime = inputs.noClassBefore;
    }
    if (inputs.noClassAfter) {
        filters.AfterTime = inputs.noClassAfter;
    }
    if (inputs.preferredDayOff) {
        filters.DayOfWeek = convertToDayShortForm(inputs.preferredDayOff);
    }

    const requestFormat = {
        Term: inputs.term,
        ...(Object.keys(filters).length > 0 ? { Filters: filters } : {}),
        Courses: courses.map(course => ({ SectionFilter: getCourseSection(course), Name: trimCourseSection(course) })),
    };

    return JSON.stringify(requestFormat, null, 5);
}

const readingWeekStartDate = "2024-02-19";
const readingWeekEndDate = "2024-02-23";


export const parseScheduleIntoEvents = (schedules) => {
    const events = [];
    const asyncEvents = [];
    schedules.forEach(schedule => {
        const eventsForCurrentSchedule = [];
        const asyncCoursesForCurrentSchedule = [];
        schedule.forEach(courseData => {
            const courseCode = courseData.CourseCode;
            const section = courseData.SectionID;
            const startDate = courseData.StartDate;
            const originalEndDate = new Date(courseData.EndDate);
            // Logic to increment end date by 1
            const updatedEndDate = new Date(originalEndDate);
            updatedEndDate.setDate(originalEndDate.getDate() + 1);
            const updatedEndDateStr = updatedEndDate.toISOString().split('T')[0];
            courseData.Times.forEach(time => {
                if (time.WeekSchedule === "Even Week" || time.WeekSchedule === "Odd Week") {
                    const biWeeklyEvent = {
                        title: `${courseCode}${section}`,
                        rrule: {
                            freq: "weekly",
                            interval: 2,
                            dtstart: `${startDate}T${time.StartTime}:00`,
                            until: `${updatedEndDateStr}`,
                            byweekday: [convertDayToInt(time.DayOfWeek) - 1],
                        },
                        duration: calculateTimeDifference(time.StartTime, time.EndTime),
                    };
                    eventsForCurrentSchedule.push(biWeeklyEvent);
                } else {
                    /*
                    For half term courses, the function calls to get the RW dates are 
                    useless because the start/end dates account RW already.
                    */
                    const fridayBeforeRW = getFridayBeforeReadingWeek(readingWeekStartDate).toISOString().split('T')[0];
                    // This event spans from start of term to before reading week
                    const event = {
                        title: `${courseCode}${section}`,
                        startTime: `${time.StartTime}:00`,
                        endTime: `${time.EndTime}:00`,
                        daysOfWeek: [convertDayToInt(time.DayOfWeek)],
                        startRecur: startDate,
                        endRecur: fridayBeforeRW//updatedEndDateStr, // exclusive so has to be +1
                    }
                    eventsForCurrentSchedule.push(event);
                    // This event spans from after reading week to end of term
                    const event2 = {
                        title: `${courseCode}${section}`,
                        startTime: `${time.StartTime}:00`,
                        endTime: `${time.EndTime}:00`,
                        daysOfWeek: [convertDayToInt(time.DayOfWeek)],
                        startRecur: getMondayAfterReadingWeek(readingWeekEndDate).toISOString().split('T')[0],
                        endRecur: updatedEndDateStr // exclusive so has to be +1
                    };
                    eventsForCurrentSchedule.push(event2)
                }
            });
            if (courseData.Times.length === 0) {
                asyncCoursesForCurrentSchedule.push(courseCode.concat(section))
            }
        });
        if (eventsForCurrentSchedule.length > 0) {
            assignColoursToEvents(eventsForCurrentSchedule, colours);
        }
        events.push(eventsForCurrentSchedule);
        asyncEvents.push(asyncCoursesForCurrentSchedule)
    });
    return [events, asyncEvents];
};

const convertToDayShortForm = (day) => {
    if (day === '') {
        return '';
    }
    const dayMappings = {
        Monday: 'Mon',
        Tuesday: 'Tue',
        Wednesday: 'Wed',
        Thursday: 'Thu',
        Friday: 'Fri'
    }
    return dayMappings[day];
}

const getCourseSection = (course) => {
    if (course !== '') {
        const section = course.slice(-1)
        if (isNaN(section)) {
            return section;
        }
    }
    return;
}

const trimCourseSection = (course) => {
    if (isNaN(course.slice(-1))) {
        return course.slice(0, -1).trim();
    }
    return course;
};

const convertDayToInt = (dayOfTheWeek) => {
    if (dayOfTheWeek === '') {
        return -1;
    }
    const dayMappings = {
        Sun: 0,
        Mon: 1,
        Tue: 2,
        Wed: 3,
        Thu: 4,
        Fri: 5,
        Sat: 6
    }
    return dayMappings[dayOfTheWeek];
};

const colours = [
    "#003B49",
    "#1D4289",
    "#BF122B",
    "#DC582A",
    "#007A78",
    "#1B365D",
    "#5D3754",
    "#41B6E6",
    "#FFC845"
];

const assignColoursToEvents = (events, colours) => {
    const colourMapping = {};

    const getPrefix = title => {
        const matches = title.match(/([a-zA-Z]+\s\d{4})/);
        return matches ? matches[1] : title;
    };

    let colourIndex = 0;
    events.forEach(event => {
        const commonPrefix = getPrefix(event.title);
        if (colourMapping.hasOwnProperty(commonPrefix)) {
            event.color = colourMapping[commonPrefix];
        }
        else {
            event.color = colours[colourIndex]
            colourMapping[commonPrefix] = event.color;
            colourIndex += 1;
        }
    });
}

const calculateTimeDifference = (start, end) => {
    const [startHours, startMinutes] = start.split(':').map(Number);
    const [endHours, endMinutes] = end.split(':').map(Number);
    const startTimeInMinutes = startHours * 60 + startMinutes;
    const endTimeInMinutes = endHours * 60 + endMinutes;
    let timeDifferenceInMinutes = endTimeInMinutes - startTimeInMinutes;
    const hours = Math.floor(timeDifferenceInMinutes / 60);
    const minutes = timeDifferenceInMinutes % 60;
    const result = `${String(hours).padStart(2, '0')}:${String(minutes).padStart(2, '0')}`;
    return result;
};

const getFridayBeforeReadingWeek = (beginning) => {
    const specifiedDate = new Date(beginning);
    const dayOfWeek = specifiedDate.getDay();
    const daysToSubtract = (dayOfWeek + 7 - 5) % 7;
    const fridayBeforeDate = new Date(specifiedDate);
    fridayBeforeDate.setDate(specifiedDate.getDate() - daysToSubtract);
    return fridayBeforeDate;
};

const getMondayAfterReadingWeek = (beginning) => {
    const specifiedDate = new Date(beginning);
    const dayOfWeek = specifiedDate.getDay();
    const daysToAdd = (dayOfWeek === 0) ? 1 : 8 - dayOfWeek;
    const mondayAfterDate = new Date(specifiedDate);
    mondayAfterDate.setDate(specifiedDate.getDate() + daysToAdd - 1);
    /* 
    -1 because the GMT date is correct, but when you do .toISOString().split('T')[0]
    I guese because of the time (hours) conversion it goes to the next day 
    */
    return mondayAfterDate;
};

//console.log(getFridayBeforeReadingWeek(readingWeekStartDate).toISOString().split('T')[0]);
console.log(getMondayAfterReadingWeek(readingWeekEndDate).toISOString().split('T')[0]);