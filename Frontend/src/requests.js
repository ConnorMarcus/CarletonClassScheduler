import axios from 'axios';

const TERMS_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/getTerms';
const COURSES_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/getCourses';
const SCHEDULES_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/generateSchedules';
const TEST_URL = 'http://localhost:5001/test'

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
        console.log("Request: ", formattedRequest);
        const response = await axios.post(SCHEDULES_URL, formattedRequest);
        if (response.data.Schedules.length === 0) {
            return { error: 'No schedules found that matches your criteria' };
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

const winter24_week1 = {
    'Mon': '2024-01-08',
    'Tue': '2024-01-09',
    'Wed': '2024-01-10',
    'Thu': '2024-01-11',
    'Fri': '2024-01-12'
}

const fall23_week1 = {
    'Mon': '2023-09-11',
    'Tue': '2023-09-12',
    'Wed': '2023-09-13',
    'Thu': '2023-09-14',
    'Fri': '2023-09-15'
}

const summer23_week1 = {
    'Mon': '2023-05-08',
    'Tue': '2023-05-09',
    'Wed': '2023-05-10',
    'Thu': '2023-05-11',
    'Fri': '2023-05-12'
}

export const convertToDate = (term, dayOfTheWeek) => {
    if (term === "Fall 2023") {
        return fall23_week1[dayOfTheWeek];
    }

    if (term === "Summer 2023") {
        return summer23_week1[dayOfTheWeek];
    }

    if (term === "Winter 2024") {
        return winter24_week1[dayOfTheWeek];
    }
};

const convertDayToInt = (dayOfTheWeek) => {
    if (dayOfTheWeek === '') {
        return '';
    }
    const dayMappings = {
        Mon: 1,
        Tue: 2,
        Wed: 3,
        Thu: 4,
        Fri: 5
    }
    return dayMappings[dayOfTheWeek];
};

export const parseScheduleIntoEvents = (schedules) => {
    const events = [];
    schedules.forEach(schedule => {
        const eventsForCurrentSchedule = [];
        schedule.forEach(courseData => {
            const courseCode = courseData.CourseCode;
            const section = courseData.SectionID;
            courseData.Times.forEach(time => {
                const event = {
                    title: `${courseCode}${section}`,
                    startTime: `${time.StartTime}:00`,
                    endTime: `${time.EndTime}:00`,
                    daysOfWeek: [convertDayToInt(time.DayOfWeek)],
                }
                eventsForCurrentSchedule.push(event);
            });
        });
        events.push(eventsForCurrentSchedule);
    });
    return events;
};