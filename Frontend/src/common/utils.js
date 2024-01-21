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
                    const event = {
                        title: `${courseCode}${section}`,
                        startTime: `${time.StartTime}:00`,
                        endTime: `${time.EndTime}:00`,
                        daysOfWeek: [convertDayToInt(time.DayOfWeek)],
                        startRecur: startDate,
                        endRecur: updatedEndDateStr, // exclusive so has to be +1
                    }
                    eventsForCurrentSchedule.push(event);
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

    colours.forEach((colour, idx) => {
        const title = events[idx % events.length].title;
        const commonPrefix = getPrefix(title);
        colourMapping[commonPrefix] = colour;
    });

    events.forEach(event => {
        const commonPrefix = getPrefix(event.title);
        if (colourMapping.hasOwnProperty(commonPrefix)) {
            event.color = colourMapping[commonPrefix];
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