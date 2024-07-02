import React from 'react';
import Mouse from 'Mouse';
import SomeComponent from './SomeComponent';
import withLogger from './withLogger';

const SomeComponentWithLogger = withLogger(SomeComponent);

function App() {
  return (
    <div className="container">
      <h1>Advanced React Patterns</h1>
      <h2>Render Props Example</h2>
      <Mouse render={({ x, y }) => (
        <p>The mouse position is ({x}, {y})</p>
      )}/>
      <h2>Higher-Order Components Example</h2>
      <SomeComponentWithLogger />
    </div>
  );
}

export default App;
