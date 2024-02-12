// FormComponent.js
import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import '../styles/FormComponent.css';
import Calendar from './CalendarComponent'
import { ALL_ASYNC_COURSES_ERROR, fetchCourses, fetchSchedules, fetchTerms, NO_SCHEDULES_ERROR } from '../common/APIutils';

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
    const [asyncEvents, setAsyncEvents] = useState([]);
    const [nonEmptyCoursesCount, setNoneEmptyCoursesCount] = useState(0);
    const [coursesList, setCoursesList] = useState({});
    const [termsAndReadingWeek, setTermsAndReadingWeek] = useState({});

    useEffect(() => {
        const getAllCourses = async (term) => {
            fetchCourses(term)
                .then((result) => {
                    if (result.Error) {
                        console.log("Failed to get courses: ", result.ErrorReason);
                    } else {
                        setCoursesList(prev => ({
                            ...prev,
                            [term]: result.Courses || [],
                        }));
                    }
                }).catch((error) => {
                    console.error("Error getting courses: ", error.message)
                });
        };

        Object.keys(termsAndReadingWeek).forEach(term => {
            getAllCourses(term);
        });

    }, [termsAndReadingWeek]);

    useEffect(() => {
        fetchTerms()
            .then((result) => {
                if (result.Error) {
                    console.log("Failed to get terms: ", result.ErrorReason);
                } else {
                    setTermsAndReadingWeek(result.Terms);
                }
            }).catch((error) => {
                console.error("Error getting terms: ", error.message);
            })
    }, []);

    //This is to check that user didn't leave all courses blank
    useEffect(() => {
        const count = Object.entries(inputValues)
            .filter(([key, value]) => /^course\d+$/.test(key) && value && value.trim() !== '')
            .length;
        setNoneEmptyCoursesCount(count);
    }, [inputValues]);

    useEffect(() => {
        const clearCourseValues = () => {
            setInputValues((prevInputValues) => {
                const newInputValues = { ...prevInputValues };
                Object.keys(newInputValues)
                    .filter((key) => /^course\d+$/.test(key))
                    .forEach((courseKey) => {
                        newInputValues[courseKey] = '';
                    });
                return newInputValues;
            });
        };
        // Clear course values when the term changes
        clearCourseValues();

    }, [inputValues.term]);

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
                if (Object.keys(termsAndReadingWeek).includes(value)) {
                    return true;
                } else if (key.includes("course") || key === "preferredDayOff" || key === "noClassBefore" || key === "noClassAfter") {
                    return true;
                } else {
                    return false;
                }
            }
        );

        if (isValidSubmission && nonEmptyCoursesCount > 0) {
            fetchSchedules(inputValues, termsAndReadingWeek).then((classes) => {
                setEvents(classes[0]);
                setAsyncEvents(classes[1])
                setIsFormSubmitted(true);
            }).catch((error) => {
                if (error.name === NO_SCHEDULES_ERROR || error.name === ALL_ASYNC_COURSES_ERROR) {
                    alert(error.message);
                } else {
                    console.error("Error generating schedules: ", error.message);
                }
            });
        } else {
            const error_msg = nonEmptyCoursesCount === 0 ? 'Please select a course' : "Please enter the Term";
            alert(error_msg);
        }
    };

    const handleClear = () => {
        setIsFormSubmitted(false);
        setEvents([]);
        setAsyncEvents([]);
    };

    const handleClearAll = () => {
        setInputValues(initialFormState);
        handleClear();
    }

    const handleClearOther = (filters = false) => {
        const inputValuesCopy = inputValues;
        for (const key in inputValuesCopy) {
            if (filters) {
                if (key === "preferredDayOff" || key === "noClassBefore" || key === "noClassAfter") {
                    inputValuesCopy[key] = '';
                }
            } else {
                if (key.startsWith("course")) {
                    inputValuesCopy[key] = '';
                }
            }
        }
        setInputValues(inputValuesCopy);
        handleClear();
    };

    const selectOptionsDaysOff = daysOffList.map(day => ({ value: day, label: day }));
    const selectOptionsTerms = Object.keys(termsAndReadingWeek).map(day => ({ value: day, label: day }));
    const selectedTermCourses = coursesList[inputValues.term] || [];

    return isFormSubmitted ? (
        <div className="schedule-view">
            <button id="back-to-form" type="button" onClick={() => setIsFormSubmitted(false)}>Back to Form</button>
            <Calendar title={inputValues.term} events={events} asyncCourses={asyncEvents} />
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
                <button type="button" onClick={handleClearAll} className="clear-all-button">
                    Clear All
                </button>
                <button type="button" onClick={() => handleClearOther()} className="clear-courses-button">
                    Clear Courses
                </button>
                <button type="button" onClick={() => handleClearOther(true)} className="clear-filters-button">
                    Clear Filters
                </button>
            </div>
        </div >
    );
};

export default FormComponent;
