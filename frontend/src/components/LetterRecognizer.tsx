import { useState } from "react";
import Canvas from "./Canvas";
import { CHALLENGES } from "../sequentialAlphabetChallenge";

export default function LetterRecognizer() {
  const [boolski, setBoolski] = useState<boolean>(false);
  const [i, setI] = useState(0);
  const [[letter, letterImg], setChallenge] = useState(CHALLENGES[i]);
  const [letterCounter, setLetterCounter] = useState(0);
  const [shouldCapture, setShouldCapture] = useState<boolean>(false);
  const [response, setResponse] = useState<string>("");
  const [shouldCaptureDynamicSign, setShouldCaptureDynamicSign] = useState<boolean>(false);

  function handleClick(event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void {
    event.preventDefault();
    setShouldCapture(prev => !prev);
  }

  if (response === letter) {
    if (!boolski) {
      setLetterCounter(letterCounter + 1);

      if (letterCounter >= 10) setBoolski(true);
    }
  }

  const onNext = () => {
    setBoolski(false);
    setResponse("");
    const nextI = i + 1;
    if (nextI < CHALLENGES.length) setChallenge(CHALLENGES[nextI]);
    setI(nextI);
    setLetterCounter(0);
  };

  if (i >= CHALLENGES.length) {
    return <div>"Well" done!</div>;
  }
  return (
    <div className="w-full h-full flex flex-col items-center">
      {shouldCapture && (
        <div className="w-full h-full flex flex-col items-center">
          <div className="w-full flex flex-col items-center">
            <img src={letterImg} alt="ASL letter A" className=" h-20 w-20" />
            <p>{letter}</p>
          </div>
          <Canvas setLetterRecognizerResponse={setResponse} shouldCaptureDynamicSign={shouldCaptureDynamicSign} />
          <p className=" h-40 text-7xl pt-2">
            {boolski && (
              <>
                "✅"
                <button onClick={onNext}>Next</button>
              </>
            )}
          </p>
        </div>
      )}
      <button onClick={handleClick}>{shouldCapture ? "Disable" : "Enable"} camera</button>
      <button onClick={handleShouldCaptureDynamicSignClick}>{/* {shouldCaptureDynamicSign ? "Don't " : ""}Capture Dynamic Sign */}Hej</button>
    </div>
  );

  function handleShouldCaptureDynamicSignClick(event: React.MouseEvent<HTMLButtonElement, MouseEvent>): void {
    event.preventDefault();
    setShouldCaptureDynamicSign(!shouldCaptureDynamicSign);
  }
}
