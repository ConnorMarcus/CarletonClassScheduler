import React, { useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import '../styles/CalendarComponent.css';


const MyCalendar = ({ title, events }) => {
    const [scheduleCount, setScheduleCount] = useState(0);

    const handlePrevClick = () => {
        setScheduleCount((prevCount) => prevCount - 1);
    };

    const handleNextClick = () => {
        setScheduleCount((prevCount) => prevCount + 1);
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
                headerToolbar={false} //Hide the previous/next week buttons, MAY ENABLE THEM LATER
                events={events[scheduleCount]}
            //eventColor="#BF122B"
            //eventBackgroundColor='#BF122B'
            />
        </div>
    );
};

export default MyCalendar;
