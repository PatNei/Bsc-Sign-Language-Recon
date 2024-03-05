import { Camera } from "@mediapipe/camera_utils";
import { NormalizedLandmark, drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { HAND_CONNECTIONS, Hands, ResultsListener } from "@mediapipe/hands";
import { APIPost } from "../api";

export interface LandmarkDTO {
    x: string;
    y: string;
    z: string;
  }

export const hands = (resultFunction: ResultsListener) => {
    const hands = new Hands({
    locateFile: (file) => {
      //return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
      return `/hands/${file}`;
    }
  })
  hands.setOptions({
    maxNumHands: 3,
    modelComplexity: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
    selfieMode:true
  })

  hands.onResults(resultFunction);
  return hands;
}

export interface camera3 {camera:Camera,isRunning:Boolean}

export const Camera2 = (videoElement: HTMLVideoElement,resultFunction: ResultsListener):camera3 => {
    const hands3 = hands(resultFunction)
    const camera = new Camera(videoElement, {
        onFrame: async () => {
          await hands3.send({ image: videoElement });
        },
        width: 1280,
        height: 720
      })
    return {camera:camera,isRunning:false};
}

interface result {
    image: CanvasImageSource
    multiHandLandmarks: NormalizedLandmark[][]
}

interface drawType { 
    results: result,
    canvas: HTMLCanvasElement | null, 
    canvasCtx:CanvasRenderingContext2D | null
}

export async function renderEverything({results,canvas,canvasCtx}:drawType) {
    if (!canvas || !canvasCtx) return;
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    canvasCtx.drawImage(results.image, 0, 0, canvas.width, canvas.height);
    for (const landmarks of results.multiHandLandmarks) {
      drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, { color: '#00FF00', lineWidth: 1 });
      drawLandmarks(canvasCtx, landmarks, { color: '#FF0000', lineWidth: 1, radius: 0.8 });
    }
    canvasCtx.restore();

    
}

interface onResultType {
    results:result
    useDynamicSign: boolean
    dynamicSignLandmarks: LandmarkDTO[][],
    setDynamicSignLandmarks: React.Dispatch<React.SetStateAction<LandmarkDTO[][]>>
    setLetterRecognizerResponse: ((r:string) => void)
}

export const onResult = async ({results,dynamicSignLandmarks,useDynamicSign,setLetterRecognizerResponse,setDynamicSignLandmarks}:onResultType) => {

    if (!useDynamicSign) {
        setDynamicSignLandmarks([]);
        return;
      }
      let min_frames_per_sign = 24;
      if (results.multiHandLandmarks && results.multiHandLandmarks.length > 0) {
        let resultsDTO = results.multiHandLandmarks.map(e => e.map((landmark) : LandmarkDTO => {
          return {
            x: landmark.x.toFixed(20),
            y: landmark.y.toFixed(20),
            z: landmark.z ? landmark.z.toFixed(20) : "0"
          }
        }));
        let landmarks = resultsDTO.length == 1 ? resultsDTO[0] : [];
        const data = dynamicSignLandmarks
        data.push(landmarks)
        setDynamicSignLandmarks(data)
        console.log(useDynamicSign)
        console.log(dynamicSignLandmarks)

        if (dynamicSignLandmarks.length == min_frames_per_sign){
          // const postState =  await APIPost(`dynamic_annotation`, dynamicSignLandmarks);
          // if (postState.response && !postState.error) {
          //   setLetterRecognizerResponse(postState.response);
          // }
          // else if (postState.error) console.log(postState.error)

          setDynamicSignLandmarks([]);
        }


      // let dynamic_sign = landmarks.slice(Math.max(landmarks.length - min_frames_per_sign, 0));
      

      // for (const landmarks of results.multiHandLandmarks) {
        // let landmarksDTO: LandmarkDTO[] = landmarks.map((landmark : NormalizedLandmark) : LandmarkDTO => {
        //   return {
        //     x: landmark.x.toFixed(20),
        //     y: landmark.y.toFixed(20),
        //     z: landmark.z ? landmark.z.toFixed(20) : "0"
        //   }
        // })

        // let postState = await APIPost(`annotation`, landmarksDTO);
        // if (postState.response && !postState.error) {
        //   if(props.onResults) props.onResults(postState.response);
        // }
        // else if (postState.error) console.log(postState.error)
}}