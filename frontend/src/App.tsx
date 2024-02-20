import React from 'react';
import './App.css';
import LetterRecognizer from './components/LetterRecognizer.tsx';


function App() {
  const [shouldCapture, setShouldCapture] = React.useState<boolean>(false);

  function handleClick(event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void {
    event.preventDefault();
    setShouldCapture(!shouldCapture)
  }

  return (
    <div className="App w-full h-full">
      
        {shouldCapture && <LetterRecognizer />}
        <button onClick={handleClick} >
            Hello
      </button>

    </div>
  );
}
      
      export default App;
      