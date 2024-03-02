import '../styles/LandingPageComponent.css';

const LandingPageComponent = () => {
    return (
        <div className="landing-page">
          <h1>Welcome to the Carleton University<br/>Student Scheduler Tool!</h1>
          <span className="button-wrapper">
            <a href="#form-component" className="button">Build Your Schedule</a>
             {/* This link to the documentation */}
            <a href="https://carleton.ca/" className="button">Need Assistance?</a>
          </span>
        </div>
    );
};

export default LandingPageComponent;