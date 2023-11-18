import React from 'react';
import FullCalendar from '@fullcalendar/react';
import timeGridPlugin from '@fullcalendar/timegrid';
import '../styles/CalendarComponent.css';

const MyCalendar = ({ title, events }) => {
    return (
        <div id="calendar">
            <h2 id="calendar-title">{title}</h2>
            <FullCalendar
                plugins={[timeGridPlugin]}
                initialView="timeGridWeek"
                weekends={false}
                slotDuration="00:30:00"
                allDaySlot={false}
                slotMinTime={"8:00:00"}
                slotMaxTime={"23:00:00"}
                height="auto"
                headerToolbar={false} //Hide the previous/next week buttons, MAY ENABLE THEM LATER
                events={events}
                eventColor="#BF122B"
                eventBackgroundColor='#BF122B'
            />
        </div>
    );
};

export default MyCalendar;
