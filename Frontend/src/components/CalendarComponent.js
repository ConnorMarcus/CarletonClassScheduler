import React, { useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
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

    return (
        <div id="calendar">
            <h2 id="calendar-title">{title}</h2>
            <p id="schedule-carrousel">
                <input className="prev-next-btn" type="button" disabled={scheduleCount === 0} onClick={handlePrevClick} value="prev"></input>
                <span id="schedule-count-text">Schedule {scheduleCount + 1}</span>
                <input className="prev-next-btn" type="button" disabled={scheduleCount === events.length - 1} onClick={handleNextClick} value="next"></input>
            </p>
            <FullCalendar
                plugins={[timeGridPlugin]}
                initialView="timeGridWeek"
                weekends={false}
                slotDuration="00:30:00"
                allDaySlot={false}
                slotMinTime={"8:00:00"}
                slotMaxTime={"23:00:00"}
                dayHeaderFormat={{ weekday: 'long' }}
                height="auto"
                initialDate={earliestStartDate(events)}
                //headerToolbar={false} //Remove this to enable cycling between weeks
                events={events[scheduleCount]}
            //eventColor="#BF122B"
            //eventBackgroundColor='#BF122B'
            />
            <div className="async-courses">
                {asyncCourses[scheduleCount].length !== 0 && (<p>Courses without assigned meeting times</p>)}
                {asyncCourses[scheduleCount]?.map((course, index) => (
                    <p key={index}><b>{course}</b></p>
                ))}
            </div>
        </div>
    );
};

export default MyCalendar;
