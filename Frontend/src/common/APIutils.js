import axios from 'axios';
import { parseInputs, parseScheduleIntoEvents } from './utils'

const TERMS_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/getTerms';
const COURSES_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/getCourses';
const SCHEDULES_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/generateSchedules';
export const NO_SCHEDULES_ERROR = 'NoSchedulesError';
export const ALL_ASYNC_COURSES_ERROR = 'AllAsyncCoursesError';

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

export const fetchSchedules = async (inputs, readingWeekDates) => {
    try {
        const formattedRequest = parseInputs(inputs);
        const response = await axios.post(SCHEDULES_URL, formattedRequest);
        const allAsync = response.data.Schedules.every(schedule => {
            return schedule.every(course => course.Times.length === 0)
        });
        if (response.data.Schedules.length === 0) {
            const noScheduleError = new Error('No schedules found that matches your criteria');
            noScheduleError.name = NO_SCHEDULES_ERROR;
            throw noScheduleError;
        } else if (allAsync) {
            const allAsyncCoursesError = new Error('All inputted courses were asynchronous');
            allAsyncCoursesError.name = ALL_ASYNC_COURSES_ERROR;
            throw allAsyncCoursesError;
        } else {
            return [parseScheduleIntoEvents(response.data.Schedules, inputs.term, readingWeekDates), response.data.ReachedScheduleLimit];
        }
    } catch (error) {
        throw error;
    }
}