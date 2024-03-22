import React, { useState, useEffect } from 'react';
import { Alert, Autocomplete, Button, Grid, Snackbar, TextField, Typography, Box, CircularProgress } from '@mui/material';
import { Add, Clear, Done, Remove } from '@mui/icons-material';
import { ALL_ASYNC_COURSES_ERROR, fetchCourses, fetchSchedules, fetchTerms, NO_SCHEDULES_ERROR } from '../common/APIutils';
import '../styles/Form.css';

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

const Form = ({ setDisplayCalendar, setTerm, setSchedules, setScheduleCount, setServerError }) => {
    const [inputValues, setInputValues] = useState(initialFormState);
    const [nonEmptyCoursesCount, setNoneEmptyCoursesCount] = useState(0);
    const [coursesList, setCoursesList] = useState({});
    const [termsAndReadingWeek, setTermsAndReadingWeek] = useState({});
    const [rows, setRows] = useState([{ id: 1 }]);
    const [rowCount, setRowCount] = useState(1);
    const [open, setOpen] = useState(false);
    const [alertMessage, setAlertMessage] = useState('');
    const [alertSeverity, setAlertSeverity] = useState('error');
    const [isLoading, setIsLoading] = useState(false);

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
        setDisplayCalendar(false);
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
        setIsLoading(true);
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
            fetchSchedules(inputValues, termsAndReadingWeek).then((results) => {
                const classes = results[0];
                const reachedScheduleLimit = results[1];
                setTerm(inputValues.term);
                setSchedules(classes);
                setDisplayCalendar(true);
                setIsLoading(false);
                if (reachedScheduleLimit) {
                    setAlertMessage("There are more than 25 results. Narrow your search to see more");
                    setAlertSeverity("info");
                    setOpen(true);
                }
            }).catch((error) => {
                setIsLoading(false);
                handleClear();
                if (error.name === NO_SCHEDULES_ERROR || error.name === ALL_ASYNC_COURSES_ERROR) {
                    setAlertMessage(error.message);
                    setOpen(true);
                } else {
                    console.error("Error generating schedules: ", error.message); // Maybe remove console logs when done development
                    setServerError(true);
                }
            });
        } else {
            const error_msg = inputValues.term !== '' ? 'Please select a course' : "Please enter the Term";
            setAlertMessage(error_msg);
            setOpen(true);
            setIsLoading(false);
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

    const addRow = () => {
        if (rowCount < 5) {
            const newRow = { id: rows.length + 1 };
            setRows([...rows, newRow]);
            setRowCount(rowCount + 1);
        }
    };

    const removeRow = () => {
        if (rowCount > 1) {
            const inputValuesCopy = { ...inputValues };
            inputValuesCopy[`extraDay${rowCount}`] = '';
            inputValuesCopy[`betweenDay${rowCount}Start`] = '';
            inputValuesCopy[`betweenDay${rowCount}End`] = '';
            setInputValues(inputValuesCopy);
            setRows(rows.slice(0, -1));
            setRowCount(rowCount - 1);
        }
    };

    const handleCloseAlert = () => {
        setOpen(false);
        setAlertSeverity('error');
    };

    const selectOptionsDaysOff = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"];
    const selectOptionsTerms = Object.keys(termsAndReadingWeek);
    const selectedTermCourses = coursesList[inputValues.term] || [];

    return (
        <Box id="form-component" className="form-container" sx={{ background: 'white', boxShadow: '10' }}>
            <Grid container spacing={2} >
                <Grid item xs={12} sx={{ textAlign: 'center' }}>
                    <Typography variant="h5" sx={{ fontWeight: 'bold' }}>
                        Build your Schedule
                    </Typography>
                </Grid>
                <Grid item xs={12} sx={{ margin: '15px 0' }}>
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
                    <Grid item key={index} xs={10} sm={6} md={4}>
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
                <Grid item xs={12} sx={{ textAlign: 'left' }}>
                    <Typography variant="h5" sx={{ marginTop: '20px', marginBottom: '10px', fontWeight: 'bold', textAlign: 'left' }}>
                        Filters<span className='optional-input'> (opt.)</span>
                    </Typography>
                    <Typography variant="h6" sx={{ fontWeight: 'bold', fontSize: '18px' }}>
                        Weekly
                    </Typography>
                </Grid>
                <Grid item xs={12} md={4}>
                    <Autocomplete
                        id="preferred-day-Off-select"
                        options={selectOptionsDaysOff}
                        value={inputValues.preferredDayOff || null}
                        onChange={(_, selectedOption) => handleInputChange('preferredDayOff', selectedOption)}
                        renderInput={(params) => <TextField {...params} size="small" label="Preferred Day Off" />}
                        sx={{ width: '100%', '& .MuiInputBase-input': { height: '25px' } }}
                    />
                </Grid>
                <Grid item xs={6} md={4}>
                    <TextField
                        id="no-class-before-input"
                        label="No Class Before"
                        type="time"
                        size='small'
                        value={inputValues.noClassBefore}
                        onChange={(e) => handleTimeInputChange('noClassBefore', e)}
                        InputLabelProps={{
                            shrink: true,
                        }}
                        inputProps={{
                            sx: { height: '25px' },
                        }}
                        sx={{ width: '100%' }}
                    />
                </Grid>
                <Grid item xs={6} md={4}>
                    <TextField
                        id="no-class-after-input"
                        label="No Class After"
                        type="time"
                        size='small'
                        value={inputValues.noClassAfter}
                        onChange={(e) => handleTimeInputChange('noClassAfter', e)}
                        InputLabelProps={{
                            shrink: true,
                        }}
                        inputProps={{
                            sx: { height: '25px' },
                        }}
                        sx={{ width: '100%' }}
                    />
                </Grid>
                <Grid item xs={12} sx={{ textAlign: 'left' }} display="flex" alignItems="center" justifyContent="space-between">
                    <Typography variant="h6" sx={{ marginTop: '10px', fontWeight: 'bold', fontSize: '18px' }}>
                        Daily
                    </Typography>
                </Grid>
                {rows.map(row => (
                    <React.Fragment key={row.id}>
                        <Grid item xs={12} md={4}>
                            <Autocomplete
                                options={selectOptionsDaysOff}
                                value={inputValues[`extraDay${row.id}`] || null}
                                onChange={(_, selectedOption) => handleInputChange(`extraDay${row.id}`, selectedOption)}
                                renderInput={(params) => <TextField {...params} size="small" label="Day" />}
                                sx={{ width: '100%', '& .MuiInputBase-input': { height: '25px' } }}
                            />
                        </Grid>
                        <Grid item xs={6} md={4}>
                            <TextField
                                label="No Class Between"
                                type="time"
                                size='small'
                                value={inputValues[`betweenDay${row.id}Start`]}
                                onChange={(e) => handleTimeInputChange(`betweenDay${row.id}Start`, e)}
                                InputLabelProps={{
                                    shrink: true,
                                }}
                                inputProps={{
                                    sx: { height: '25px' },
                                }}
                                sx={{ width: '100%' }}
                            />
                        </Grid>
                        <Grid item xs={6} md={4}>
                            <TextField
                                label="And"
                                type="time"
                                size='small'
                                value={inputValues[`betweenDay${row.id}End`]}
                                onChange={(e) => handleTimeInputChange(`betweenDay${row.id}End`, e)}
                                InputLabelProps={{
                                    shrink: true,
                                }}
                                inputProps={{
                                    sx: { height: '25px' },
                                }}
                                sx={{ width: '100%' }}
                            />
                        </Grid>
                    </React.Fragment>
                ))}
                <Grid item xs={12} >
                    <Button
                        variant="outlined"
                        sx={{
                            borderColor: '#BF122B',
                            color: '#BF122B',
                            transition: 'opacity 0.3s ease-in-out',
                            marginRight: '20px',
                            '&:hover': {
                                opacity: '0.7',
                                borderColor: '#BF122B',
                            },
                        }}
                        size="small"
                        onClick={addRow}
                        disabled={rowCount === 5}
                        startIcon={<Add />}
                        id="add-button"
                    >
                        Add
                    </Button>
                    <Button
                        variant="outlined"
                        sx={{
                            borderColor: 'black',
                            color: 'black',
                            transition: 'opacity 0.3s ease-in-out',
                            '&:hover': {
                                opacity: '0.7',
                                borderColor: 'black',
                            },
                        }}
                        size="small"
                        onClick={removeRow}
                        disabled={rowCount === 1}
                        startIcon={<Remove />}
                        id="remove-button"
                    >
                        Remove
                    </Button>
                </Grid>
                {isLoading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', marginTop: '20px', alignItems: 'center', width: '100%' }}>
                        <CircularProgress color='inherit' />
                    </Box>
                ) : (
                    <>
                        <Grid item xs={12} sx={{ marginTop: '30px' }}>
                            <Button
                                variant="contained"
                                sx={{
                                    background: '#BF122B',
                                    fontSize: '15px',
                                    paddingRight: '15px',
                                    paddingLeft: '15px',
                                    marginRight: '20px',
                                    '&:hover': {
                                        background: '#BF122B'
                                    },
                                }}
                                size="small"
                                onClick={handleSubmit}
                                startIcon={<Done />}
                                id="build-button"
                            >
                                Build
                            </Button>
                            <Button
                                variant="contained"
                                sx={{
                                    background: 'black',
                                    fontSize: '15px',
                                    paddingRight: '15px',
                                    paddingLeft: '15px',
                                    '&:hover': {
                                        background: 'black'
                                    },
                                }}
                                size="small"
                                onClick={handleClearAll}
                                startIcon={<Clear />}
                                id="clear-button"
                            >
                                Clear All
                            </Button>
                        </Grid>
                    </>
                )}
            </Grid>
            <Snackbar open={open} autoHideDuration={5000} onClose={handleCloseAlert}>
                <Alert onClose={handleCloseAlert} severity={alertSeverity} style={{ fontSize: '1.25rem', textAlign: 'left' }}>
                    {alertMessage}
                </Alert>
            </Snackbar>
        </Box >
    );
};

export default Form;
