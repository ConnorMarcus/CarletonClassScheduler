// FormComponent.js
import React, { useState, useEffect } from 'react';
import Select from 'react-select';
import Box from '@mui/material/Box'
import Typography from '@mui/material/Typography';
import Grid from '@mui/material/Grid';
import Autocomplete from '@mui/material/Autocomplete';
import TextField from '@mui/material/TextField';
import '../styles/FormComponent.css';
import { ALL_ASYNC_COURSES_ERROR, fetchCourses, fetchSchedules, fetchTerms, NO_SCHEDULES_ERROR } from '../common/APIutils';

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
    extraDay1: '',
    betweenDay1Start: '',
    betweenDay1End: '',
    extraDay2: '',
    betweenDay2Start: '',
    betweenDay2End: '',
    extraDay3: '',
    betweenDay3Start: '',
    betweenDay3End: '',
    extraDay4: '',
    betweenDay4Start: '',
    betweenDay4End: '',
    extraDay5: '',
    betweenDay5Start: '',
    betweenDay5End: '',
};

const FormComponent = ({setDisplayCalendar, setTerm, setSchedules, setScheduleCount, setServerError}) => {
    const [inputValues, setInputValues] = useState(initialFormState);
    const [nonEmptyCoursesCount, setNoneEmptyCoursesCount] = useState(0);
    const [coursesList, setCoursesList] = useState({});
    const [termsAndReadingWeek, setTermsAndReadingWeek] = useState({});
    const [rows, setRows] = useState([{ id: 1 }]);
    const [rowCount, setRowCount] = useState(1);

    useEffect(() => {
        const getAllCourses = async (term) => {
            fetchCourses(term)
                .then((result) => {
                    if (result.Error) {
                        console.log("Failed to get courses: ", result.ErrorReason); // Maybe remove console logs when done development
                        setServerError(true);
                    } else {
                        setCoursesList(prev => ({
                            ...prev,
                            [term]: result.Courses || [],
                        }));
                    }
                }).catch((error) => {
                    console.error("Error getting courses: ", error.message) // Maybe remove console logs when done development
                    setServerError(true);
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
                    console.log("Failed to get terms: ", result.ErrorReason); // Maybe remove console logs when done development
                    setServerError(true);
                } else {
                    setTermsAndReadingWeek(result.Terms);
                }
            }).catch((error) => {
                console.error("Error getting terms: ", error.message); // Maybe remove console logs when done development
                setServerError(true);
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
        const selectedTerm = selectedOption ? selectedOption : '';

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
                } else if (key.includes("extraDay") || key.includes("betweenDay")) {
                    return true;
                }
                else {
                    return false;
                }
            }
        );

        if (isValidSubmission && nonEmptyCoursesCount > 0) {
            setScheduleCount(0);
            fetchSchedules(inputValues, termsAndReadingWeek).then((classes) => {
                setTerm(inputValues.term);
                setSchedules(classes);
                setDisplayCalendar(true);
            }).catch((error) => {
                handleClear();
                if (error.name === NO_SCHEDULES_ERROR || error.name === ALL_ASYNC_COURSES_ERROR) {
                    alert(error.message);
                } else {
                    console.error("Error generating schedules: ", error.message); // Maybe remove console logs when done development
                    setServerError(true);
                }
            });
        } else {
            const error_msg = inputValues.term !== '' ? 'Please select a course' : "Please enter the Term";
            alert(error_msg);
        }
    };

    const handleClear = () => {
        setDisplayCalendar(false);
        setSchedules([]);
    };

    const handleClearAll = () => {
        setInputValues(initialFormState);
        handleClear();
    }

    const handleClearOther = (filters = false) => {
        const inputValuesCopy = { ...inputValues }; // Create shallow copy of object so that we are not modifying the object directly
        for (const key in inputValuesCopy) {
            if (filters) {
                if (key === "preferredDayOff" || key === "noClassBefore" || key === "noClassAfter" || key.includes("extraDay") || key.includes("betweenDay")) {
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

    const addRow = () => {
        if (rowCount < 5) {
            const newRow = { id: rows.length + 1 };
            setRows([...rows, newRow]);
            setRowCount(rowCount + 1);
        }
    };

    const selectOptionsDaysOff = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
    const selectOptionsTerms = Object.keys(termsAndReadingWeek);
    const selectedTermCourses = coursesList[inputValues.term] || [];

    return  (
        <Box id="form-component" className="form-container" sx={{ background: 'white', boxShadow: '10'}}>
            <Grid container spacing={2} >
                <Grid item xs={12} sm={12} md={12} sx={{ textAlign: 'left'}}>
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                        Enter Your Schedule<span className="required-input"> *</span>
                    </Typography>
                </Grid>
                <Grid item xs={12} sm={12} md={12} sx={{ margin: '15px 0' }}>
                    <Autocomplete
                        id="term-select"
                        options={selectOptionsTerms}
                        value={inputValues.term || null} 
                        onChange={(_, selectedOption) => handleInputChange('term', selectedOption)}
                        renderInput={(params) => <TextField {...params} size="small" label="Term" />}
                        sx={{ width: '290px', '& .MuiInputBase-input': { height: '25px' } }}
                    />
                </Grid>
                {Object.keys(inputValues).slice(0, 9).map((inputName, index) => (
                    <Grid item key={index} xs={6} sm={6} md={4}>
                        <Autocomplete
                            id={`course-select-${index}`}
                            options={selectedTermCourses}
                            value={inputValues[inputName] || null}
                            onChange={(_, selectedOption) => handleInputChange(inputName, selectedOption)}
                            renderInput={(params) => <TextField {...params} size="small" label={`Course ${index + 1}`} />}
                            sx={{ width: '100%', '& .MuiInputBase-input': { height: '25px' } }}
                        />
                    </Grid>
                ))}
                <Grid item xs={12} sm={12} md={12} sx={{ textAlign: 'left' }}>
                    <Typography variant="h5" sx={{ marginTop: '15px', fontWeight: 'bold'}}>
                        Filters<span className='optional-input'> (opt.)</span>
                    </Typography>
                    <Typography variant="h6" sx={{ marginTop: '15px', fontWeight: 'bold', fontSize: '16px'}}>
                        Weekly
                    </Typography>
                </Grid>
                <Grid item xs={12} sm={12} md={12}>
                    <Autocomplete
                        id="preferred-day-Off-select"
                        options={selectOptionsDaysOff}
                        value={inputValues.preferredDayOff || null} 
                        onChange={(_, selectedOption) => handleInputChange('preferredDayOff', selectedOption)}
                        renderInput={(params) => <TextField {...params} size="small" label="Preferred Day Off" />}
                        sx={{ width: '290px', '& .MuiInputBase-input': { height: '25px' } }}
                    />
                </Grid>
            </Grid>
            {/* <div className="courses">
                <div className="term">
                    <label className='term-label'>Term<span className="required-input"> *</span></label>
                    <Select
                        value={{ value: inputValues.term, label: inputValues.term }}
                        onChange={(selectedOption) => handleInputChange('term', selectedOption)}
                        options={selectOptionsTerms}
                        className="select-input"
                    />
                </div>
                <h2 className="header">Courses<span className="required-input"> *</span></h2>
                <div className="grid-container">
                    {Object.keys(inputValues).slice(0, 9).map((inputName, index) => (
                        <Select
                            key={index}
                            value={{ value: inputValues[inputName], label: inputValues[inputName] }}
                            onChange={(selectedOption) => handleInputChange(inputName, selectedOption)}
                            options={selectedTermCourses.map(course => ({ value: course, label: course }))}
                            className="select-input"
                            maxMenuHeight={115}
                        />
                    ))}
                </div>
            </div> */}

            {/* <h2 className="Header">Filters<span className='optional-input'> (opt.)</span></h2>
            <h3 className="Header">Weekly</h3> */}
            <div className="filters">
                {/* <label className="day-off-label">Preferred Day Off</label>
                <Select
                    value={{ value: inputValues.preferredDayOff, label: inputValues.preferredDayOff }}
                    onChange={(selectedOption) => handleInputChange('preferredDayOff', selectedOption)}
                    options={selectOptionsDaysOff}
                    className="select-input"
                /> */}
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
            <div className="daily-filters">
                <div className="daily-filter-header">
                    <h3 className="Header">Daily</h3>
                    <button className="daily-filter-btn" onClick={addRow} disabled={rowCount === 5}>+</button>
                </div>
                <div className="filters-container">
                    {rows.map(row => (
                        <div key={row.id} className="filters-row">
                            <div className="filters-column">
                                <label className="day-off-label">Day</label>
                                <Select
                                    value={{ value: inputValues[`extraDay${row.id + 1}`], label: inputValues[`extraDay${row.id + 1}`] }}
                                    onChange={(selectedOption) => handleInputChange(`extraDay${row.id + 1}`, selectedOption)}
                                    options={selectOptionsDaysOff}
                                    className="select-input"
                                />
                            </div>
                            <div className="filters-column">
                                <label className="label">No class between</label>
                                <input
                                    type="time"
                                    value={inputValues[`betweenDay${row.id + 1}Start`]}
                                    onChange={(e) => handleTimeInputChange(`betweenDay${row.id + 1}Start`, e)}
                                    className="time-input"
                                />
                            </div>
                            <div className="filters-column">
                                <label className="label">and</label>
                                <input
                                    type="time"
                                    value={inputValues[`betweenDay${row.id + 1}End`]}
                                    onChange={(e) => handleTimeInputChange(`betweenDay${row.id + 1}End`, e)}
                                    className="time-input"
                                />
                            </div>
                        </div>
                    ))}
                </div>
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
        </Box>
    );
};

export default FormComponent;
