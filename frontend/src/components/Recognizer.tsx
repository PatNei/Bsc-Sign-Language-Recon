import { useState } from "react";
import Canvas from "./Canvas";
import { LetterChallenge, WordChallenge } from "../challenges";
import DynamicCanvas from "./DynamicCanvas";
import { JSX } from "react/jsx-runtime";

interface props {
  challenges: LetterChallenge[] | WordChallenge[];
  dynamic: boolean;
}

export default function Recognizer({ challenges, dynamic }: props) {
  const [boolski, setBoolski] = useState<boolean>(false);
  const [i, setI] = useState(0);
  const [[sign, signSrc], setChallenge] = useState(challenges[i]);
  const [key, setKey] = useState(0);
  const [srcIndex, setSrcIndex] = useState(0);
  const [letterCounter, setLetterCounter] = useState(0);
  const [shouldCapture, setShouldCapture] = useState<boolean>(false);
  const [response, setResponse] = useState<string>("");
  const [currentSrc, setCurrentSrc] = useState<JSX.Element>(
    <iframe
      className="pb-2"
      width="420"
      height="315"
      src={`https://www.youtube.com/embed/${
        signSrc[0].split(":")[0]
      }?start=${Math.floor(
        +signSrc[0].split(":")[1] / 1000
      )}&cc_load_policy=1&autoplay=1&end=${
        Math.floor(+signSrc[0].split(":")[1] / 1000) + 1
      }&loop=1&fs=0&iv_load_policy=3`}
    />
  );

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
            <div className="grid grid-cols-1">
              {currentSrc}
              <div className="flex justify-evenly">
                <div>
                  <button
                    className={
                      signSrc.length > 1
                        ? "bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                        : "bg-blue-500 text-white font-bold py-2 px-4 rounded opacity-50 cursor-not-allowed"
                    }
                    type="button"
                    disabled={signSrc.length <= 1}
                    onClick={(_) => {
                      let newSrcIndex = (srcIndex + 1) % signSrc.length;
                      setCurrentSrc((_) => (
                        <iframe
                          key={0}
                          className="pb-2"
                          width="420"
                          height="315"
                          src={`https://www.youtube.com/embed/${
                            signSrc[newSrcIndex].split(":")[0]
                          }?start=${Math.floor(
                            +signSrc[newSrcIndex].split(":")[1] / 1000
                          )}&cc_load_policy=1&autoplay=1&end=${
                            Math.floor(
                              +signSrc[newSrcIndex].split(":")[1] / 1000
                            ) + 1
                          }&loop=1&fs=0&iv_load_policy=3`}
                        />
                      ));
                      setSrcIndex(newSrcIndex);
                      setKey(0);
                    }}
                  >
                    {signSrc.length > 1
                      ? `Next Clip (${srcIndex + 1}/${signSrc.length})`
                      : "This is all we have"}
                  </button>
                </div>
                <div>
                  <button
                    onClick={(_) => {
                      setCurrentSrc((_) => (
                        <iframe
                          key={key + 1}
                          className="pb-2"
                          width="420"
                          height="315"
                          src={`https://www.youtube.com/embed/${
                            signSrc[srcIndex].split(":")[0]
                          }?start=${Math.floor(
                            +signSrc[srcIndex].split(":")[1] / 1000
                          )}&cc_load_policy=1&autoplay=1&end=${
                            Math.floor(
                              +signSrc[srcIndex].split(":")[1] / 1000
                            ) + 1
                          }&loop=1&fs=0&iv_load_policy=3`}
                        />
                      ));
                      setKey((i) => i + 1);
                    }}
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                    type="button"
                  >
                    ↺
                  </button>
                </div>
              </div>
            </div>
          )}
          <p className="pt-2">{`${sign[0].toUpperCase()}${sign.slice(1)}`}</p>
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
      <button
        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
        type="button"
        onClick={(_) => setShouldCapture(!shouldCapture)}
      >
        {shouldCapture ? "Disable" : "Enable"} camera
      </button>
    </div>
  );
}
