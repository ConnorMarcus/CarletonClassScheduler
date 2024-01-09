import axios from 'axios';

const TERMS_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/getTerms';
const COURSES_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/getCourses';
const SCHEDULES_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/generateSchedules';
export const NO_SCHEDULES_ERROR = 'NoSchedulesError';

export const fetchTerms = async () => {
    try {
        const response = await axios.get(TERMS_URL);
        return response.data;

    } catch (error) {
        throw error;
    }
}

export const fetchCourses = async (term) => {
    try {
        const response = await axios.get(`${COURSES_URL}?Term=${encodeURIComponent(term)}`);
        return response.data;
    } catch (error) {
        throw error;
    }
}

export const fetchSchedules = async (inputs) => {
    try {
        const formattedRequest = parseInputs(inputs);
        const response = await axios.post(SCHEDULES_URL, formattedRequest);
        if (response.data.Schedules.length === 0) {
            throw { name: NO_SCHEDULES_ERROR, message: 'No schedules found that matches your criteria' };
        } else {
            return parseScheduleIntoEvents(response.data.Schedules);
        }
    } catch (error) {
        throw error;
    }
}

// Formatting functions 

const parseInputs = (inputs) => {
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
        /*
        ...(inputs.noClassBefore || inputs.noClassAfter || inputs.preferredDayOff ?
            {
                Filters: {
                    BeforeTime: inputs.noClassBefore,
                    AfterTime: inputs.noClassAfter,
                    DayOfWeek: convertToDayShortForm(inputs.preferredDayOff),
                }
            }
            : {}
        ),
        */
        Courses: courses.map(course => ({ SectionFilter: getCourseSection(course), Name: trimCourseSection(course) })),
    };

    return JSON.stringify(requestFormat, null, 5);
}

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

/* If date is in format 'Jan 8, 24' coverts it to 2024-01-08
const convertDateStr = dateString => {

    var dateObject = new Date(dateString);

    var year = dateObject.getFullYear();
    var month = (dateObject.getMonth() + 1).toString().padStart(2, '0'); // Months are 0-based
    var day = dateObject.getDate().toString().padStart(2, '0');
    return year + "-" + month + "-" + day;
};
*/

export const parseScheduleIntoEvents = (schedules) => {
    const events = [];
    const asyncEvents = [];
    schedules.forEach(schedule => {
        const eventsForCurrentSchedule = [];
        const asyncCoursesForCurrentSchedule = [];
        schedule.forEach(courseData => {
            const courseCode = courseData.CourseCode;
            const section = courseData.SectionID;
            courseData.Times.forEach(time => {
                const event = {
                    title: `${courseCode}${section}`,
                    startTime: `${time.StartTime}:00`,
                    endTime: `${time.EndTime}:00`,
                    daysOfWeek: [convertDayToInt(time.DayOfWeek)],
                    //startRecur: convertDateStr('Jan 08, 2024'),
                    //endRecur: convertDateStr('Apr 15, 2024'),
                    // will eventually be like this --> startRecur: time.StartDate,
                }
                eventsForCurrentSchedule.push(event);
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