import { useState } from "react";
import Canvas from "./Canvas";
import { CHALLENGES } from "../sequentialAlphabetChallenge";
import DynamicCanvas from "./DynamicCanvas";

export default function LetterRecognizer() {
  const [boolski, setBoolski] = useState<boolean>(false);
  const [i, setI] = useState(0);
  const [[letter, letterImg], setChallenge] = useState(CHALLENGES[i]);
  const [letterCounter, setLetterCounter] = useState(0);
  const [shouldCapture, setShouldCapture] = useState<boolean>(false);
  const [response, setResponse] = useState<string>("");
  const debugMode = false

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
      
        <div className="w-full h-full flex flex-col items-center">
          <div className="w-full flex flex-col items-center">
            <img src={letterImg} alt="ASL letter A" className=" h-20 w-20" />
            <p>{letter}</p>
          </div>
          {debugMode || "jz".includes(letter) ? (
            <DynamicCanvas setLetterRecognizerResponse={setResponse} />
          ) : (
            <Canvas setLetterRecognizerResponse={setResponse} />
          )}
          <p className=" h-40 text-7xl pt-2">
            {boolski && (
              <>
                "✅"
                <button type="button" onClick={onNext}>Next</button>
              </>
            )}
          </p>
        </div>
      {debugMode && (<>
      <button type="button" onClick={(event) => {
          event.preventDefault();
          setShouldCapture((prev) => !prev)
        }}>
        { shouldCapture ? "Disable" : "Enable"} camera
      </button>
      </>)}
    
    </div>
  );
}
