import React, { useState, useRef, useEffect } from 'react';
import { Calendar, ErrorPage, Footer, Form, LandingPage } from './components'

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

  const displayCalendarComponent = () => (displayCalendar ? <Calendar title={term} events={schedules} scheduleCount={scheduleCount} setScheduleCount={setScheduleCount} ref={calendarRef} /> : null);

  if (serverError) {
    return <ErrorPage />
  }

  return (
    <div>
      <LandingPage />
      <Form setDisplayCalendar={setDisplayCalendar} setTerm={setTerm} setSchedules={setSchedules} setScheduleCount={setScheduleCount} setServerError={setServerError} />
      {displayCalendarComponent()}
      <Footer />
    </div>
  );
};

export default App;
