import { useEffect, useState } from "react";
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

export default function LetterRecognizer() {
  const [response, setResponse] = useState<string>();
  const [boolski, setBoolski] = useState<boolean>(false);
  const [i, setI] = useState(0);
  const [ [letter, letterImg], setChallenge] = useState(CHALLENGES[i]);
  

  //const [letter, letterImg] = [0]
  
  if(response === letter){
    console.log("good job bozo")
    if(!boolski) setBoolski(true);
  }

  const onNext = () => {
    setBoolski(false)
    setResponse("")
    const nextI = i + 1 
    setChallenge(CHALLENGES[nextI])
    setI(nextI)
  }

  console.log(boolski)
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
