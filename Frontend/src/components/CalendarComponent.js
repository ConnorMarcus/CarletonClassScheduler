import React, { useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import rrulePlugin from '@fullcalendar/rrule';
import '../styles/CalendarComponent.css';


const MyCalendar = ({ title, events, asyncCourses }) => {
    const [scheduleCount, setScheduleCount] = useState(0);

    const handlePrevClick = () => {
        setScheduleCount((prevCount) => prevCount - 1);
    };

    const handleNextClick = () => {
        setScheduleCount((prevCount) => prevCount + 1);
    };

    const earliestStartDate = (courses) => {
        let earliestDate = courses[0][0].startRecur;
        for (const schedule of courses) {
            for (const course of schedule) {
                const currDate = course.startRecur;
                if (currDate < earliestDate) {
                    earliestDate = currDate;
                }
            }
        }
        return earliestDate;
    };

    const copyCRNsToClipboard = () => {
        const courseCRNs = Array.from(new Set(events[scheduleCount].map(event => event.crn)));
        const asyncCourseCRNs = Array.from(new Set(asyncCourses[scheduleCount].map(event => event.crn)));
        const allCRNs = courseCRNs.concat(asyncCourseCRNs);
        const crnString = allCRNs.join(', ');
        navigator.clipboard.writeText(crnString)
            .then(() => {
                alert(`CRNs copied to clipboard: ${crnString}`);
            })
            .catch((error) => {
                console.error('Error copying to clipboard:', error);
            });
    };

    return (
        <div id="calendar">
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
                slotMaxTime={"23:00:00"}
                dayHeaderFormat={{ weekday: 'long' }}
                height="auto"
                initialDate={earliestStartDate(events)}
                events={events[scheduleCount]}
            />
            <div className="async-courses">
                {asyncCourses[scheduleCount].length !== 0 && (<p>Courses without assigned meeting times</p>)}
                {asyncCourses[scheduleCount]?.map((course, index) => (
                    <p key={index}><b>{course.title}</b></p>
                ))}
            </div>
        </div >
    );
};

export default MyCalendar;
