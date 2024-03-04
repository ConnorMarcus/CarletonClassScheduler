import React, { useState, useRef, useEffect } from 'react';
import LandingPageComponent from './components/LandingPageComponent';
import FormComponent from './components/FormComponent';
import CalendarComponent from './components/CalendarComponent';
import ErrorPage from './components/ErrorPage';

const App = () => {
  const [displayCalendar, setDisplayCalendar] = useState(false);
  const [term, setTerm] = useState('');
  const [schedules, setSchedules] = useState([]);
  const [scheduleCount, setScheduleCount] = useState(0);
  const [serverError, setServerError] = useState(false);
  const calendarRef = useRef();
  
  useEffect(() => {
    if (displayCalendar && calendarRef.current) {
      calendarRef.current.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
  });

  const displayCalendarComponent = () => (displayCalendar ? <CalendarComponent title={term} events={schedules} scheduleCount={scheduleCount} setScheduleCount={setScheduleCount} ref={calendarRef}/> : null);

  if (serverError) {
    return <ErrorPage />
  }

  return (
    <div>
      <LandingPageComponent />
      <FormComponent setDisplayCalendar={setDisplayCalendar} setTerm={setTerm} setSchedules={setSchedules} setScheduleCount={setScheduleCount} setServerError={setServerError}/>
      {displayCalendarComponent()}
    </div>
  );
};

export default App;
