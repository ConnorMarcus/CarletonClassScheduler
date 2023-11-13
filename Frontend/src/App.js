import React from 'react';
import FormComponent from './components/FormComponent';

/*
function App() {
  return (
    <div className="App">
      <header className="App-header">
        <img src={logo} className="App-logo" alt="logo" />
        <p>
          Edit <code>src/App.js</code> and save to reload.
        </p>
        <a
          className="App-link"
          href="https://reactjs.org"
          target="_blank"
          rel="noopener noreferrer"
        >
          Learn React
        </a>
      </header>
    </div>
  );
}
*/

const App = () => {
  return (
    <div>
      <h1>Carleton University Schedular</h1>
      <FormComponent />
    </div>
  );
};

export default App;
