import { useState } from "react";
import Canvas from "./Canvas";
import { LetterChallenge, WordChallenge } from "../challenges";
import DynamicCanvas from "./DynamicCanvas";

interface props {
  challenges: LetterChallenge[] | WordChallenge[];
  dynamic: boolean;
}

export default function Recognizer({ challenges, dynamic }: props) {
  const [boolski, setBoolski] = useState<boolean>(false);
  const [i, setI] = useState(0);
  const [[sign, signSrc], setChallenge] = useState(challenges[i]);
  const [letterCounter, setLetterCounter] = useState(0);
  const [shouldCapture, setShouldCapture] = useState<boolean>(false);
  const [response, setResponse] = useState<string>("");

  if (response === sign) {
    if (!boolski) {
      setLetterCounter(letterCounter + 1);

      if (letterCounter >= 10) setBoolski(true);
    }
  }

  const onNext = () => {
    setBoolski(false);
    setResponse("");
    const nextI = i + 1;
    if (nextI < challenges.length) setChallenge(challenges[nextI]);
    setI(nextI);
    setLetterCounter(0);
  };

  if (i >= challenges.length) {
    return <div>"Well" done!</div>;
  }
  return (
    <div className="w-full h-full flex flex-col items-center">
      <div className="w-full h-full flex flex-col items-center">
        <div className="w-full flex flex-col items-center">
          {typeof signSrc === "string" ? (
            <img
              src={signSrc}
              alt={`ASL sign for ${sign}`}
              className=" h-20 w-20"
            />
          ) : (
            signSrc.map((clip, i) => (
              <iframe
                key={i}
                width="420"
                height="315"
                src={`https://www.youtube.com/embed/${
                  clip.split(":")[0]
                }?start=${Math.floor(
                  +clip.split(":")[1] / 1000
                )}&cc_load_policy=1`}
              ></iframe>
            ))
          )}
          <p>{sign}</p>
        </div>
        {shouldCapture &&
          (dynamic || "JZ".includes(sign) ? (
            <DynamicCanvas setLetterRecognizerResponse={setResponse} />
          ) : (
            <Canvas setLetterRecognizerResponse={setResponse} />
          ))}
        <p className=" h-40 text-7xl pt-2">
          {boolski && (
            <>
              "✅"
              <button type="button" onClick={onNext}>
                Next
              </button>
            </>
          )}
        </p>
      </div>
      <button type="button" onClick={() => setShouldCapture(!shouldCapture)}>
        {shouldCapture ? "Disable" : "Enable"} camera
      </button>
    </div>
  );
}
