// FormComponent.js
import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import '../styles/FormComponent.css';
import Calendar from './CalendarComponent'
import { fetchCourses, fetchSchedules, fetchTerms } from '../requests';

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

    const handleSubmit = async (event) => {
        event.preventDefault();
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
            const classes = await fetchSchedules(inputValues);
            if (classes.error) {
                alert(classes.error)
            } else {
                console.log("classes are: ", classes);
                setEvents(classes);
                setIsFormSubmitted(true);
            }
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

    const selectOptionsDaysOff = daysOffList.map(day => ({ value: day, label: day }));
    const selectOptionsTerms = termsList.map(day => ({ value: day, label: day }));
    const selectedTermCourses = coursesList[inputValues.term] || [];

    return isFormSubmitted ? (
        <div className="schedule-view">
            <button id="back-to-form" type="button" onClick={() => setIsFormSubmitted(false)}>Back to Form</button>
            <Calendar title={inputValues.term} events={events} />
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
