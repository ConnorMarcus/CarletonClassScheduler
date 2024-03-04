import React from 'react';
import '../styles/ErrorPage.css';

const ErrorPage = () => {
  return (
    <div className="error-container">
      <h1>Service Unavailable</h1>
      <p>The site is down. Please try again later.</p>
    </div>
  );
};

export default ErrorPage;