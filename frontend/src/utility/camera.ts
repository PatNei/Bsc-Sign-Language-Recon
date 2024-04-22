import { Camera } from "@mediapipe/camera_utils";
// import { Hands, ResultsListener } from "@mediapipe/hands";
import { Handedness, Hands, NormalizedLandmark } from "@mediapipe/hands";
import { type drawType, renderEverything } from "./draw";
import { onResult, type onResultType } from "./api";
import { HANDS_PATH } from "../constants/paths";

// resultFunction: ResultsListener
export const createHands = (
  props: Omit<onResultType, "multiHandLandmarks">,
  draw: drawType
) => {
  const hands = new Hands({
    locateFile: (file) => {
      //return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
      return `${HANDS_PATH}/${file}`; // TODO:  We need to load this as an environment variable as it is needed but not found when vite creates an executable
    },
  });
  hands.setOptions({
    maxNumHands: 3,
    modelComplexity: 1,
    minDetectionConfidence: 0.5,
    minTrackingConfidence: 0.5,
    selfieMode: true,
  });

  hands.onResults((result) => {
    renderEverything(result, draw);
    onResult({
      ...props,
      multiHandLandmarks: result.multiHandLandmarks.map(
        (e, i): [NormalizedLandmark[], Handedness] => [
          e,
          result.multiHandedness[i],
        ]
      ),
    });
  });
  return hands;
};

/** Wrapper function that creates a Camera from mediapipe with the config we want. */
export const createCamera = (hands: Hands, videoElement: HTMLVideoElement) => {
  const camera = new Camera(videoElement, {
    onFrame: async () => {
      await hands.send({ image: videoElement });
    },
    width: 1280,
    height: 720,
  });
  camera.start();
  return camera;
};
