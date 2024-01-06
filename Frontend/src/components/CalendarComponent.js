import React, { useState } from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import '../styles/CalendarComponent.css';
import { convertToDate } from '../requests';


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
            <p>
                <input type="button" disabled={scheduleCount === 0} onClick={handlePrevClick} value="prev"></input>
                Schedule {scheduleCount+1}
                <input type="button" disabled={scheduleCount === events.length-1} onClick={handleNextClick} value="next"></input>
            </p>
            <FullCalendar
                plugins={[timeGridPlugin]}
                initialView="timeGridWeek"
                weekends={false}
                slotDuration="00:30:00"
                allDaySlot={false}
                slotMinTime={"8:00:00"}
                slotMaxTime={"23:00:00"}
                dayHeaderFormat={{ weekday: 'short' }}
                height="auto"
                headerToolbar={false} //Hide the previous/next week buttons, MAY ENABLE THEM LATER
                events={events[scheduleCount]}
                eventColor="#BF122B"
                eventBackgroundColor='#BF122B'
            />
        </div>
    );
};

export default MyCalendar;
