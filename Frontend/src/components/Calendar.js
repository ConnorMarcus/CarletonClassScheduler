import React, { useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import rrulePlugin from '@fullcalendar/rrule';
import { getCourseTime } from '../common/utils';
import { createTheme, responsiveFontSizes, ThemeProvider } from '@mui/material/styles';
import { Alert, Box,  Button,  Modal, Snackbar, Typography } from '@mui/material';
import { ArrowBackIos, ArrowForwardIos, ContentCopy } from '@mui/icons-material';
import useMediaQuery from '@mui/material/useMediaQuery';
import '../styles/Calendar.css';


const Calendar = React.forwardRef(({ title, events, scheduleCount, setScheduleCount }, ref) => {
    const [openAlert, setOpenAlert] = useState(false);
    const [openModal, setOpenModal] = useState(false);
    const [alertMessage, setAlertMessage] = useState('');
    const [eventDetails, setEventDetails] = useState(null);

    const handlePrevClick = () => {
        setScheduleCount((prevCount) => prevCount - 1);
    };

    const handleNextClick = () => {
        setScheduleCount((prevCount) => prevCount + 1);
    };

    const earliestStartDate = (courses) => {
        let earliestDate = courses[0]["sync"][0].startRecur;
        for (const schedule of courses) {
            const obj = schedule["sync"];
            for (const course of obj) {
                const currDate = course.startRecur;
                if (currDate < earliestDate) {
                    earliestDate = currDate;
                }
            }
        }
        return earliestDate;
    };

    const copyCRNsToClipboard = () => {
        let courseCRNs;
        const syncCourseCRNs = Array.from(new Set(events[scheduleCount]["sync"].map(event => event.crn)));
        const syncStr = syncCourseCRNs.join(', ');
        const asyncCourseCRNs = Array.from(new Set(events[scheduleCount]["async"].map(event => event.crn)));
        let asyncStr;
        if (asyncCourseCRNs.length !== 0) {
            asyncStr = asyncCourseCRNs.join(', ');
            courseCRNs = `${syncStr}, ${asyncStr}`;
        } else {
            courseCRNs = syncStr;
        }
        navigator.clipboard.writeText(courseCRNs)
            .then(() => {
                setAlertMessage("CRNs copied to clipboard");
                setOpenAlert(true);
            })
            .catch((error) => {
                console.error('Error copying to clipboard:', error);
            });
    };

    const handleEventClick = (event) => {
        const title = event["event"]["_def"]["title"];
        const crn = event["event"]["_def"]["extendedProps"]["crn"];
        const instructor = event["event"]["_def"]["extendedProps"]["instructor"];
        const status = event["event"]["_def"]["extendedProps"]["status"];
        const name = event["event"]["_def"]["extendedProps"]["name"];
        const prereq = event["event"]["_def"]["extendedProps"]["prereq"];

        let startTimeStr, endTimeStr;

        // Biweekly labs have rrule and dates are stored differently
        if (event["event"]["_def"]["recurringDef"]["typeData"].hasOwnProperty("rruleSet")) {
            const duration = event["event"]["_def"]["recurringDef"]["duration"]["milliseconds"];
            const startTimeDateStr = event["event"]["_def"]["recurringDef"]["typeData"]["rruleSet"]["_rrule"][0]["options"]["dtstart"];
            let date = new Date(startTimeDateStr);
            startTimeStr = `${date.getUTCHours()}:${date.getUTCMinutes().toString().padStart(2, '0')}`;
            date = new Date(date.getTime() + duration);
            endTimeStr = `${date.getUTCHours()}:${date.getUTCMinutes().toString().padStart(2, '0')}`;
        } else {
            const startTimeMsec = event["event"]["_def"]["recurringDef"]["typeData"]["startTime"]["milliseconds"];
            const endTimeMsec = event["event"]["_def"]["recurringDef"]["typeData"]["endTime"]["milliseconds"];
            startTimeStr = getCourseTime(startTimeMsec);
            endTimeStr = getCourseTime(endTimeMsec);
        }
        const eventDetails = { title, startTimeStr, endTimeStr, instructor, crn, status, name, prereq }
        setEventDetails(eventDetails);
        setOpenModal(true);
    };

    const handleCloseAlert = () => {
        setOpenAlert(false);
    };

    const handleCloseModal = () => {
        setOpenModal(false);
    }

    // Handle responsiveness
    const theme = responsiveFontSizes(createTheme());
    const isSmallScreen = useMediaQuery(theme.breakpoints.down('sm'));
    const dayHeaderFormat = isSmallScreen ? { weekday: 'short' } : { weekday: 'long' };
    const responsiveMargin = isSmallScreen ? '0' : '25px';
    const responsivePadding = isSmallScreen ? '0 10px 0 10px' : '0 40px 20px 40px;';

    return (
        <ThemeProvider theme={theme}>
            <Box id="calendar" ref={ref} sx={{ boxShadow: '10', margin: responsiveMargin, padding: responsivePadding }}>
                <Typography variant='h4' sx={{ fontWeight: 'bold', marginY: '30px' }}>
                    Schedules for {title}
                </Typography>
                <Box display="flex" justifyContent="center" alignItems="center" sx={{ margin: '20px 0' }}>
                    <Button
                        variant="contained"
                        sx={{
                            background: '#BF122B',
                            paddingY: '8px',
                            color: 'white',
                            '&:hover': {
                                background: '#BF122B',
                            },
                            '&:disabled': {
                                background: '#BF122B',
                                color: 'white',
                                opacity: '50%'
                            }
                        }}
                        size="small"
                        onClick={handlePrevClick}
                        disabled={scheduleCount === 0}
                        startIcon={<ArrowBackIos />}
                    >
                        prev
                    </Button>
                    <Typography variant='h6' sx={{ paddingX: '15px' }}>
                        {scheduleCount + 1} of {events.length}
                    </Typography>
                    <Button
                        variant="contained"
                        sx={{
                            background: '#BF122B',
                            paddingY: '8px',
                            color: 'white',
                            '&:hover': {
                                background: '#BF122B',
                            },
                            '&:disabled': {
                                background: '#BF122B',
                                color: 'white',
                                opacity: '50%'
                            }
                        }}
                        size="small"
                        onClick={handleNextClick}
                        disabled={scheduleCount === events.length - 1}
                        endIcon={<ArrowForwardIos />}
                    >
                        Next
                    </Button>
                </Box>
                <FullCalendar
                    plugins={[timeGridPlugin, rrulePlugin]}
                    initialView="timeGridWeek"
                    weekends={false}
                    slotDuration="00:30:00"
                    allDaySlot={false}
                    slotMinTime={"8:00:00"}
                    slotMaxTime={"21:00:00"}
                    dayHeaderFormat={dayHeaderFormat}
                    height="auto"
                    initialDate={earliestStartDate(events)}
                    events={events[scheduleCount]["sync"]}
                    eventClick={handleEventClick}
                    headerToolbar={{ end: 'prev,next' }}
                />
                <Box className="async-courses" display="flex" justifyContent="space-between" alignItems="center">
                    <Box sx={{ textAlign: 'left' }}>
                        {events[scheduleCount]["async"].length !== 0 && (
                            <Typography variant="body1" sx={{ marginTop: '20px', marginBottom: '5px' }}>Courses without assigned meeting times</Typography>
                        )}
                        {events[scheduleCount]["async"].length !== 0 && (
                            <Typography variant="body1">
                                {events[scheduleCount]["async"]?.map((course, index) => (
                                    <React.Fragment key={index}>
                                        {index > 0 && ', '}
                                        <b className="async-course-name">{course.title}</b> - {course.crn}
                                    </React.Fragment>
                                ))}
                            </Typography>
                        )}
                    </Box>
                    <Button
                        variant="contained"
                        sx={{
                            background: '#BF122B',
                            color: 'white',
                            '&:hover': {
                                background: '#BF122B',
                            },
                            marginTop: '20px'
                        }}
                        size="medium"
                        onClick={copyCRNsToClipboard}
                        startIcon={<ContentCopy />}
                    >
                        Export CRNs
                    </Button>
                </Box>

                <Snackbar open={openAlert} autoHideDuration={5000} onClose={handleCloseAlert}>
                    <Alert onClose={handleCloseAlert} severity="info" style={{ fontSize: '1.25rem' }}>
                        {alertMessage}
                    </Alert>
                </Snackbar>

                <Modal
                    open={openModal}
                    onClose={handleCloseModal}
                    aria-labelledby="modal-title"
                    aria-describedby="modal-description"
                >
                    <Box sx={{ color: 'black', position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', height: 'fit-content', width: 275, bgcolor: 'background.paper', border: '1px solid #BF122B', boxShadow: 24, p: 2, borderRadius: '10px', }}>
                        <h2 id="modal-title">{eventDetails?.title}</h2>
                        <h3>{eventDetails?.name}</h3>
                        <p id="modal-description" style={{ textAlign: 'left' }}>
                            <b>Time: </b>{eventDetails?.startTimeStr} - {eventDetails?.endTimeStr}<br />
                            <b>Instructor: </b>{eventDetails?.instructor}<br />
                            <b>CRN: </b>{eventDetails?.crn}<br />
                            <b>Status: </b>{eventDetails?.status}<br />
                            {eventDetails?.prereq && <><b>Prerequisites: </b>{eventDetails?.prereq}<br /></>}
                        </p>
                    </Box>
                </Modal>
            </Box >
        </ThemeProvider>
    );
});

export default Calendar;
