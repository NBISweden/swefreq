import React, { Component } from 'react';
import logo from './logo.svg';
import './App.css';
import DatasetCard from './DatasetCard';

const dummyDataset = {
    fullName: 'Dummy dataset long name',
    hasImage: false,
    shortName: 'ShortName',
    future: false,
    version: {
        description: "This is a <em>description</em> of the dataset",
        availableFrom: '2018-06-20',
    },
};

const dummyFutureDataset = {
    fullName: 'Dummy future dataset',
    hasImage: false,
    shortName: 'ShortName',
    future: true,
    version: {
        description: "This is a <em>description</em> of the dataset",
        availableFrom: '2019-06-20',
    },
};

class App extends Component {
  render() {
    return (
      <div className="App">
        <header className="App-header">
          <img src={logo} className="App-logo" alt="logo" />
          <h1 className="App-title">Welcome to React</h1>
        </header>
        <p className="App-intro">
          To get started, edit <code>src/App.js</code> and save to reload.
        </p>
         <DatasetCard dataset={dummyDataset} />
         <DatasetCard dataset={dummyFutureDataset} />
      </div>
    );
  }
}

export default App;
