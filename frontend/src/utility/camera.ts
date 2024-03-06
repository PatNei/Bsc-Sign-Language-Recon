import { Camera } from "@mediapipe/camera_utils";
import { NormalizedLandmark } from "@mediapipe/drawing_utils";
import { Hands, ResultsListener } from "@mediapipe/hands";
import { drawType, renderEverything } from "./draw";

const createHands = (resultFunction: ResultsListener) => {
  const hands = new Hands({
    locateFile: (file) => {
      //return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
      return `/hands/${file}`; // TODO:  We need to load this as an environment variable as it is needed but not found when vite creates an executable
    }
  })
  hands.setOptions({
    maxNumHands: 3,
    modelComplexity: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
    selfieMode: true
  })

  hands.onResults(resultFunction);
  return hands;
}

/** Wrapper function that creates a Camera from mediapipe with the config we want. */
export const createCamera = (videoElement: HTMLVideoElement, { canvas, canvasCtx }: drawType, resultFunction: ResultsListener) => {
  const hands = createHands((result) => {
    renderEverything(result, { canvas, canvasCtx })
    //resultFunction(result)
  })
  const camera = new Camera(videoElement, {
    onFrame: async () => {
      await hands.send({ image: videoElement });
    },
    width: 1280,
    height: 720
  })
  camera.start()
  return camera
}


