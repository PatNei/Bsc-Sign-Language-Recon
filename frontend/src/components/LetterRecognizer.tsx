import { useState } from "react";
import Canvas from "./Canvas";

type Challenge = [letter: string, image: string];
const PATH = "/public/letterImages/";

const ALPHABET = "abcdefghijklmnopqrstuvwxyz".toUpperCase().split("");
const CHALLENGES: Challenge[] = ALPHABET.reduce(
  (prev: Challenge[], cur: string) => {
    prev.push([cur, PATH + cur.toLowerCase() + ".png"]);
    return prev;
  },
  []
);
console.log(CHALLENGES.length)

export default function LetterRecognizer() {
  const [response, setResponse] = useState<string>();
  const [boolski, setBoolski] = useState<boolean>(false);
  const [i, setI] = useState(0);
  const [ [letter, letterImg], setChallenge] = useState(CHALLENGES[i]);
  const [letterCounter, setLetterCounter] = useState(0);


  if(response === letter){
    if(!boolski) {
      setLetterCounter(letterCounter + 1)

      if (letterCounter >= 10) setBoolski(true);
    } 
  }

  const onNext = () => {
    setBoolski(false)
    setResponse("")
    const nextI = i + 1 
    if(nextI < CHALLENGES.length) setChallenge(CHALLENGES[nextI])
    setI(nextI)
    setLetterCounter(0);
  }

  if(i >= CHALLENGES.length) {
    return <div>
      "Well" done!
    </div>
  }

  return (
    <div className="w-full h-full flex flex-col items-center">
      <div>
        <img src={letterImg} alt="ASL letter A" className=" h-20 w-20" />
        <p>{letter}</p>
      </div>
      <Canvas onResults={setResponse} />
      <p className=" h-40 text-9xl">
        {boolski ? (
          <>
            "✅"
            <button onClick={onNext}>Click me</button>
          </>
        ) : (
          "❌FAILURE❌"
        )}
      </p>
    </div>
  );
}
