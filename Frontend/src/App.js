import React, { useState, useRef, useEffect } from 'react';
import LandingPageComponent from './components/LandingPageComponent';
import FormComponent from './components/FormComponent';
import CalendarComponent from './components/CalendarComponent';

const App = () => {
  const [displayCalendar, setDisplayCalendar] = useState(false);
  const [term, setTerm] = useState('');
  const [schedules, setSchedules] = useState([]);
  const [scheduleCount, setScheduleCount] = useState(0);
  const calendarRef = useRef();
  
  useEffect(() => {
    if (displayCalendar && calendarRef.current) {
      calendarRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });

  const displayCalendarComponent = () => (displayCalendar ? <CalendarComponent title={term} events={schedules} scheduleCount={scheduleCount} setScheduleCount={setScheduleCount} ref={calendarRef}/> : null);

  return (
    <div>
      <LandingPageComponent />
      <FormComponent setDisplayCalendar={setDisplayCalendar} setTerm={setTerm} setSchedules={setSchedules} setScheduleCount={setScheduleCount}/>
      {displayCalendarComponent()}
    </div>
  );
};

export default App;
