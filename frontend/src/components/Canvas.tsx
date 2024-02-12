import { Camera } from "@mediapipe/camera_utils";
import { Hands } from "@mediapipe/hands";
import { ReactElement, useRef, CanvasHTMLAttributes, useEffect } from 'react';
import { drawConnectors, drawLandmarks, NormalizedLandmark } from '@mediapipe/drawing_utils';
import { HAND_CONNECTIONS, InputImage } from '@mediapipe/holistic';
import { APIPost } from "../api";

interface Landmark {
  x: string;
  y: string;
  z: string;
}

export default function Canvas(props?: CanvasHTMLAttributes<HTMLCanvasElement>): ReactElement {

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current ?? undefined;
    const videoElement = videoRef.current ?? undefined;
    const canvasCtx = canvas?.getContext('2d');
    if (canvasCtx === undefined || canvasCtx === null || canvas === undefined) {
      return;
    }
    if (videoElement === undefined) {
      return;
    }
    const hands = new Hands({
      locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
      }
    });

    hands.setOptions({
      maxNumHands: 2,
      modelComplexity: 1,
      minDetectionConfidence: 0.5,
      minTrackingConfidence: 0.5
    });

    hands.onResults((results) => {
      onResults(results, canvas, canvasCtx);
    });

    const camera = new Camera(videoElement, {
      onFrame: async () => {
        await hands.send({ image: videoElement as unknown as InputImage });
      },
      width: 1280,
      height: 720
    });
    camera.start();
  }, []);

  async function onResults(results: { image: CanvasImageSource; multiHandLandmarks: NormalizedLandmark[][]; }, canvas: HTMLCanvasElement, canvasCtx: CanvasRenderingContext2D) {
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    canvasCtx.drawImage(
      results.image, 0, 0, canvas.width, canvas.height);
    if (results.multiHandLandmarks) {
      for (const landmarks of results.multiHandLandmarks) {
        let newLandmarks: Landmark[] = []
        landmarks.forEach((element, i) => {
          newLandmarks[i] = {
            x: element.x.toFixed(),
            y: element.y.toFixed(),
            z: element.z ? element.z.toFixed() : "0"
          }
        });
        drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, { color: '#00FF00', lineWidth: 2 });
        drawLandmarks(canvasCtx, landmarks, { color: '#FF0000', lineWidth: 2 });
        let postState = await APIPost(`annotation`, newLandmarks);
        if (postState.response && !postState.error) console.log(postState.response)
        else if (postState.error) console.log(postState.error)
      }
    }
    canvasCtx.restore();
  }

  return <div>
    <video hidden ref={videoRef} />
    <canvas className='the-canvas' ref={canvasRef} {...props}></canvas>
  </div>
}