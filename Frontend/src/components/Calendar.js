import React, { useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import rrulePlugin from '@fullcalendar/rrule';
import { getCourseTime } from '../common/utils';
import { Box, Modal, MuiAlert, Snackbar } from '@mui/material';
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
        const eventDetails = { title, startTimeStr, endTimeStr, instructor, crn, status }
        setEventDetails(eventDetails);
        setOpenModal(true);
    };

    const handleCloseAlert = () => {
        setOpenAlert(false);
    };

    const handleCloseModal = () => {
        setOpenModal(false);
    }

    return (
        <div id="calendar" ref={ref}>
            <h2 id="calendar-title">{title}</h2>
            <button className="crn-btn" type="button" onClick={copyCRNsToClipboard}>Export CRNs</button>
            <p id="schedule-carrousel">
                <input className="prev-next-btn" type="button" disabled={scheduleCount === 0} onClick={handlePrevClick} value="prev"></input>
                <span id="schedule-count-text">Schedule {scheduleCount + 1}</span>
                <input className="prev-next-btn" type="button" disabled={scheduleCount === events.length - 1} onClick={handleNextClick} value="next"></input>
            </p>
            <FullCalendar
                plugins={[timeGridPlugin, rrulePlugin]}
                initialView="timeGridWeek"
                weekends={false}
                slotDuration="00:30:00"
                allDaySlot={false}
                slotMinTime={"8:00:00"}
                slotMaxTime={"21:00:00"}
                dayHeaderFormat={{ weekday: 'short' }}
                height="auto"
                initialDate={earliestStartDate(events)}
                events={events[scheduleCount]["sync"]}
                eventClick={handleEventClick}
                headerToolbar={{ end: 'prev,next' }}
            />
            <div className="async-courses">
                {events[scheduleCount]["async"].length !== 0 && (<p>Courses without assigned meeting times</p>)}
                {events[scheduleCount]["async"].length !== 0 && events[scheduleCount]["async"]?.map((course, index) => (
                    <span key={index}><b className="async-course-name">{course.title}</b> - {course.crn}</span>)).reduce((prev, curr) => [prev, ', ', curr])
                }
            </div>

            <Snackbar open={openAlert} autoHideDuration={5000} onClose={handleCloseAlert}>
                <MuiAlert onClose={handleCloseAlert} severity="info" style={{ fontSize: '1.25rem' }}>
                    {alertMessage}
                </MuiAlert>
            </Snackbar>

            <Modal
                open={openModal}
                onClose={handleCloseModal}
                aria-labelledby="modal-title"
                aria-describedby="modal-description"
            >
                <Box sx={{ color: 'black', position: 'absolute', top: '50%', left: '50%', transform: 'translate(-50%, -50%)', height: 'fit-content', width: 275, bgcolor: 'background.paper', border: '1px solid #BF122B', boxShadow: 24, p: 2, borderRadius: '10px', }}>
                    <h2 id="modal-title">{eventDetails?.title}</h2>
                    <p id="modal-description" style={{ textAlign: 'left' }}>
                        <b>Time: </b>{eventDetails?.startTimeStr} - {eventDetails?.endTimeStr}<br />
                        <b>Instructor: </b>{eventDetails?.instructor}<br />
                        <b>CRN: </b>{eventDetails?.crn}<br />
                        <b>Status: </b>{eventDetails?.status}
                    </p>
                </Box>
            </Modal>
        </div >
    );
});

export default Calendar;
