import { useState } from "react";
import Canvas from "./Canvas";
import { CHALLENGES } from "../sequentialAlphabetChallenge";

export default function Mirror() {
  const [response, setResponse] = useState<string>();

  const [letter, imgpath] = CHALLENGES.find(( [letter, _]) => letter === response) ?? ["",""]

  return (
    <div className="w-full h-full flex flex-col items-center">
      <Canvas setLetterRecognizerResponse={setResponse} />
      <div className="flex flex-row">
        <p className=" h-40 text-7xl pt-2">
            {response}
        </p>
        {letter && imgpath && <img src={imgpath} alt={`letter ${letter}`} className="h-20 w-20"/>}
      </div>

    </div>
  );
}
