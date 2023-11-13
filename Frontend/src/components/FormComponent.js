// FormComponent.js
import React, { useState } from 'react';
import Select from 'react-select';
import '../styles/FormComponent.css';

const fruitsList = ["Apple", "Banana", "Mango", "Chocolate", "Pineapple", "Berry", "Orange"];
const daysOffList = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];


const initialFormState = {
    input1: '',
    input2: '',
    input3: '',
    input4: '',
    input5: '',
    input6: '',
    preferredDayOff: '',
    noClassBefore: '',
    noClassAfter: '',
};

const FormComponent = () => {
    const [inputValues, setInputValues] = useState({
        input1: '',
        input2: '',
        input3: '',
        input4: '',
        input5: '',
        input6: '',
        preferredDayOff: '',
        noClassBefore: '',
        noClassAfter: '',
    });

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
                key === "preferredDayOff" || key === "noClassBefore" || key === "noClassAfter" || fruitsList.includes(value)
        );

        if (isValidSubmission) {
            // Add your logic here for handling the form submission
            console.log("Form submitted with values:", inputValues);
        } else {
            alert("Invalid submission. Please enter valid values.");
        }
    };

    const handleClear = () => {
        setInputValues(initialFormState);
    };


    const selectOptionsFruits = fruitsList.map(fruit => ({ value: fruit, label: fruit }));
    const selectOptionsDaysOff = daysOffList.map(day => ({ value: day, label: day }));

    return (
        <div className="form-container">
            <h2 className="header">Courses</h2>
            <div className="courses">
                <div className="grid-container">
                    {Object.keys(inputValues).slice(0, 6).map((inputName, index) => (
                        <Select
                            key={index}
                            value={{ value: inputValues[inputName], label: inputValues[inputName] }}
                            onChange={(selectedOption) => handleInputChange(inputName, selectedOption)}
                            options={selectOptionsFruits}
                            className="select-input"
                        />
                    ))}
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
