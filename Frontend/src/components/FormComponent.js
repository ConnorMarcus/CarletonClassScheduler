// FormComponent.js
import React, { useState } from 'react';
import Select from 'react-select';
import '../styles/FormComponent.css';
import Calendar from './CalendarComponent'

const coursesList = ["SYSC 4001", "SYSC 3303B", "SYSC 4106", "COMP 3005", "ECOR 4995A", "SYSC 4120C", "SYSC 4907"];
const daysOffList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
const termsList = ["Fall 2023", "Winter 2024", "Summer 2024"];


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
    const [isFormSubmitted, setIsFormSubmitted] = useState(false)
    const [events, setEvents] = useState([])

    const handleInputChange = (inputName, selectedOption) => {
        setInputValues({
            ...inputValues,
            [inputName]: selectedOption ? selectedOption.value : '', // handle null selectedOption for time inputs
        });
    };

    const handleTimeInputChange = (inputName, event) => {
        setInputValues({
            ...inputValues,
            [inputName]: event.target.value,
        });
    };

    const handleSubmit = (event) => {
        event.preventDefault();

        // Validate if all input values are part of the corresponding list before submission
        const isValidSubmission = Object.entries(inputValues).every(
            ([key, value]) =>
                key === "preferredDayOff" || key === "term" || key === "noClassBefore" || key === "noClassAfter" || coursesList.includes(value)
        );

        if (isValidSubmission) {
            // Add your logic here for handling the form submission
            console.log("Form submitted with values:", inputValues);

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
                }
            ]

            setEvents(classes);
            console.log(events)
            setIsFormSubmitted(true);


        } else {
            alert("Invalid submission. Please enter valid values.");
        }
    };

    const handleClear = () => {
        setInputValues(initialFormState);
        setIsFormSubmitted(false);
    };


    const selectOptionsCourses = coursesList.map(course => ({ value: course, label: course }));
    const selectOptionsDaysOff = daysOffList.map(day => ({ value: day, label: day }));
    const selectOptionsTerms = termsList.map(day => ({ value: day, label: day }));

    return isFormSubmitted ? (
        <div class="schedule-view">
            <button id="back-to-form" type="button" onClick={() => setIsFormSubmitted(false)}>Back to Form</button>
            <Calendar title={"Fall 23"} events={events} />
        </div>
    ) : (
        <div className="form-container">
            <h2 className="header">Courses</h2>
            <div className="courses">
                <div className="grid-container">
                    {Object.keys(inputValues).slice(0, 9).map((inputName, index) => (
                        <Select
                            key={index}
                            value={{ value: inputValues[inputName], label: inputValues[inputName] }}
                            onChange={(selectedOption) => handleInputChange(inputName, selectedOption)}
                            options={selectOptionsCourses}
                            className="select-input"
                        />
                    ))}
                </div>
                <div class="term">
                    <label className='term-label'>Term</label>
                    <Select
                        value={{ value: inputValues.term, label: inputValues.term }}
                        onChange={(selectedOption) => handleInputChange('term', selectedOption)}
                        options={selectOptionsTerms}
                        className="select-input"
                        placeholder="Select Term"
                    />
                </div>
            </div>
            <h2 className="Header">Filters</h2>
            <div className="filters">
                <label className="day-off-label">Preferred Day Off</label>
                <Select
                    value={{ value: inputValues.preferredDayOff, label: inputValues.preferredDayOff }}
                    onChange={(selectedOption) => handleInputChange('preferredDayOff', selectedOption)}
                    options={selectOptionsDaysOff}
                    className="select-input"
                    placeholder="Select Day"
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
