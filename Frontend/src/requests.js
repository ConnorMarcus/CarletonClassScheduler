import axios from 'axios';

const TERMS_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/getTerms';
const COURSES_URL = 'https://kw6n873e4f.execute-api.us-east-1.amazonaws.com/Prod/getCourses';
//const COURSES_URL = 'http://localhost:5001/test'

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