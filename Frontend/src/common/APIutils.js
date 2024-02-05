import axios from 'axios';
import { parseInputs, parseScheduleIntoEvents } from './utils'

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
            const noScheduleError = new Error('No schedules found that matches your criteria');
            noScheduleError.name = NO_SCHEDULES_ERROR;
            throw noScheduleError;
        } else {
            return parseScheduleIntoEvents(response.data.Schedules, inputs.term);
        }
    } catch (error) {
        throw error;
    }
}