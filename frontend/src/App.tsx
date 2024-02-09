import React from 'react';
import './App.css';
import Canvas from './components/Canvas.tsx';


function App() {
  const [shouldCapture, setShouldCapture] = React.useState<boolean>(false);

  function handleClick(event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void {
    event.preventDefault();
    setShouldCapture(!shouldCapture)
  }

  return (
    <div className="App">
      <div className="container">
        {shouldCapture && <Canvas />}
        <button onClick={handleClick} >
            Hello
      </button>
      </div>
    </div>
  );
}
      
      export default App;
      