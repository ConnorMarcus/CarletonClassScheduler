// FormComponent.js
import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import '../styles/FormComponent.css';
import Calendar from './CalendarComponent'
import { fetchCourses, fetchTerms } from '../requests';

//const coursesList = ["SYSC 4001", "SYSC 3303B", "SYSC 4106", "COMP 3005", "ECOR 4995A", "SYSC 4120C", "SYSC 4907"];
const daysOffList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];


const initialFormState = {
    course1: '',
    course2: '',
    course3: '',
    course4: '',
    course5: '',
    course6: '',
    course7: '',
    course8: '',
    course9: '',
    term: '',
    preferredDayOff: '',
    noClassBefore: '',
    noClassAfter: '',
};

const FormComponent = () => {

    const [inputValues, setInputValues] = useState(initialFormState);
    const [isFormSubmitted, setIsFormSubmitted] = useState(false);
    const [events, setEvents] = useState([]);
    const [nonEmptyCoursesCount, setNoneEmptyCoursesCount] = useState(0);
    const [termsList, setTermsList] = useState([]);
    const [coursesList, setCoursesList] = useState({});

    useEffect(() => {
        const getAllCourses = async (term) => {
            try {
                fetchCourses(term)
                    .then((result) => {
                        if (result.Error) {
                            console.error("Error getting couress", result.ErrorReason);
                        } else {
                            setCoursesList(prev => ({
                                ...prev,
                                [term]: result.Courses || [],
                            }));
                        }
                    });
            } catch (error) {
                console.error("Catch error getting courses", error);
            }
        };

        termsList.forEach(term => {
            getAllCourses(term);
        });

    }, [termsList]);

    useEffect(() => {
        fetchTerms()
            .then((result) => {
                if (result.Error) {
                    console.error('Error:', result.ErrorReason);
                } else {
                    setTermsList(result.Terms);
                }
            }).catch((error) => {
                console.error("Catching error", error);
            })
    }, []);

    //This is to check that user didn't leave all courses blank
    useEffect(() => {
        const count = Object.entries(inputValues)
            .filter(([key, value]) => /^course\d+$/.test(key) && value && value.trim() !== '')
            .length;
        setNoneEmptyCoursesCount(count);
    }, [inputValues]);

    const handleInputChange = (inputName, selectedOption) => {
        const selectedTerm = selectedOption ? selectedOption.value : '';

        /*
        setInputValues({
            ...inputValues,
            [inputName]: selectedOption ? selectedOption.value : '', // handle null selectedOption for time inputs
        });
        */

        setInputValues({
            ...inputValues,
            [inputName]: selectedTerm,
        });

        setCoursesList(prev => ({
            ...prev,
            [selectedTerm]: prev[selectedTerm] || [],
        }))
    };

    const handleTimeInputChange = (inputName, event) => {
        setInputValues({
            ...inputValues,
            [inputName]: event.target.value,
        });
    };

    // Make function async when I add logic for API call: '= async (event) => {...}
    const handleSubmit = (event) => {
        event.preventDefault();

        // Validate if all input values are part of the corresponding list before submission
        const isValidSubmission = Object.entries(inputValues).every(
            ([key, value]) => {
                if (termsList.includes(value)) {
                    return true;
                } else if (key.includes("course") || key === "preferredDayOff" || key === "noClassBefore" || key === "noClassAfter") {
                    return true;
                } else {
                    console.log(key, value)
                    return false;
                }
            }
        );

        //As long as the term is included and at least one course is non-empty
        if (isValidSubmission && nonEmptyCoursesCount > 0) {
            /*
            try {
                const request = await fetch('URL TO API', {
                    method = 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(inputValues), // likely have to manipulate the data first to fit the endpoints
                });
                if (!request.ok) {
                    const error_msg = 'Request failed with status: ' + request.statusText;
                    console.log(error_msg)
                    throw new Error(error_msg);
                }
    
                const response = await request.json();
                //setEvents(request); //Likely have to parse it first to desired format
                //setIfFormSubmitted(true); 
            } catch (error) {
                console.error(error);
                alert("something went wrong")
            }
            */

            const classes = [
                {
                    title: 'SYSC 4001 A',
                    start: '2023-11-15T10:05:00',
                    end: '2023-11-15T11:35:00'
                },
                {
                    title: 'SYSC 4001 A',
                    start: '2023-11-17T10:05:00',
                    end: '2023-11-17T11:35:00'
                },
                {
                    title: 'SYSC 3303B',
                    start: '2023-11-16T08:35:00',
                    end: '2023-11-16T09:55:00'
                },
                {
                    title: 'SYSC 3303B',
                    start: '2023-11-14T08:35:00',
                    end: '2023-11-14T09:55:00'
                },
                {
                    title: 'SYSC 4120 C',
                    start: '2023-11-14T011:35:00',
                    end: '2023-11-14T12:55:00'
                },
                {
                    title: 'SYSC 4120 C',
                    start: '2023-11-16T11:35:00',
                    end: '2023-11-16T12:55:00'
                },

                {
                    title: 'ECOR 4995 A',
                    start: '2023-11-17T18:05:00',
                    end: '2023-11-17T20:55:00'
                },
                {
                    title: 'COMP 3005',
                    start: '2023-11-15T14:35:00',
                    end: '2023-11-15T16:25:00'
                },
                {
                    title: 'COMP 3005',
                    start: '2023-11-17T14:35:00',
                    end: '2023-11-17T16:25:00'
                },
                {
                    title: 'ECOR 1041',
                    start: '2023-11-20T14:35:00',
                    end: '2023-11-20T16:25:00'
                },
                {
                    title: 'ECOR 1042',
                    start: '2023-11-20T14:35:00',
                    end: '2023-11-20T16:25:00'
                },
                {
                    title: 'TEST',
                    start: 'MondayT14:35:00',
                    end: 'MondayT16:25:00'
                }
            ];

            setEvents(classes);
            setIsFormSubmitted(true);

        } else {
            const error_msg = nonEmptyCoursesCount === 0 ? 'Please select a course' : "Please enter the Term";
            alert(error_msg);
        }
    };

    const handleClear = () => {
        setInputValues(initialFormState);
        setIsFormSubmitted(false);
        setEvents([]);
    };


    //const selectOptionsCourses = coursesList.map(course => ({ value: course, label: course }));
    const selectOptionsDaysOff = daysOffList.map(day => ({ value: day, label: day }));
    const selectOptionsTerms = termsList.map(day => ({ value: day, label: day }));
    const selectedTermCourses = coursesList[inputValues.term] || [];

    return isFormSubmitted ? (
        <div className="schedule-view">
            <button id="back-to-form" type="button" onClick={() => setIsFormSubmitted(false)}>Back to Form</button>
            <Calendar title={"Fall 23"} events={events} />
        </div>
    ) : (
        <div className="form-container">

            <div className="courses">
                <div className="term">
                    <label className='term-label'>Term<span className="required-input"> *</span></label>
                    <Select
                        value={{ value: inputValues.term, label: inputValues.term }}
                        onChange={(selectedOption) => handleInputChange('term', selectedOption)}
                        options={selectOptionsTerms}
                        className="select-input"
                    />
                </div>
                <h2 className="header">Courses</h2>
                <div className="grid-container">
                    {Object.keys(inputValues).slice(0, 9).map((inputName, index) => (
                        <Select
                            key={index}
                            value={{ value: inputValues[inputName], label: inputValues[inputName] }}
                            onChange={(selectedOption) => handleInputChange(inputName, selectedOption)}
                            options={selectedTermCourses.map(course => ({ value: course, label: course }))}
                            //options={selectOptionsCourses}
                            className="select-input"
                            maxMenuHeight={115}
                        />
                    ))}
                </div>
            </div>
            <h2 className="Header">Filter<span className='optional-input'> (opt.)</span></h2>
            <div className="filters">
                <label className="day-off-label">Preferred Day Off</label>
                <Select
                    value={{ value: inputValues.preferredDayOff, label: inputValues.preferredDayOff }}
                    onChange={(selectedOption) => handleInputChange('preferredDayOff', selectedOption)}
                    options={selectOptionsDaysOff}
                    className="select-input"
                />
                <label className="label">No Class Before</label>
                <input
                    type="time"
                    value={inputValues.noClassBefore}
                    onChange={(e) => handleTimeInputChange('noClassBefore', e)}
                    className="time-input"
                />
                <label className="label">No Class After</label>
                <input
                    type="time"
                    value={inputValues.noClassAfter}
                    onChange={(e) => handleTimeInputChange('noClassAfter', e)}
                    className="time-input"
                />
            </div>
            <div className="button-container">
                <button type="submit" onClick={handleSubmit} className="submit-button">
                    Submit
                </button>
                <button type="button" onClick={handleClear} className="clear-button">
                    Clear
                </button>
            </div>
        </div>
    );
};

export default FormComponent;
