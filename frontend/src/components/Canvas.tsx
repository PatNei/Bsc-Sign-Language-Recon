import { Camera } from "@mediapipe/camera_utils";
import { Hands, NormalizedLandmark } from "@mediapipe/hands";
import { ReactElement, useRef, CanvasHTMLAttributes, useEffect } from 'react';
import { drawConnectors, drawLandmarks } from '@mediapipe/drawing_utils';
import { HAND_CONNECTIONS, InputImage } from '@mediapipe/holistic';
import { useAPIPost } from "../api";

interface Landmark {
  x: string;
  y: string;
  z: string;
}

export default function Canvas(props?: CanvasHTMLAttributes<HTMLCanvasElement>): ReactElement {

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const apiGet = useAPIPost();

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
      // console.log(results.multiHandLandmarks)
      for (const landmarks of results.multiHandLandmarks) {
        let newLandmarks: Landmark[] = []
        landmarks.forEach((element, i) => {
          newLandmarks[i] = {
            x: element.x.toFixed(8),
            y: element.y.toFixed(8),
            z: element.z.toFixed(8)
          }
        });
        // console.log(JSON.stringify(newLandmarks))
        await apiGet.postData(`annotation`, newLandmarks);
        if (apiGet.response && !apiGet.error) console.log(apiGet.response)
        else if (apiGet.error) console.log(apiGet.error)
        // try {
        //   // let annotation = await getAnnotations(landmarks)
        //   // console.log(JSON.stringify(annotation))
        // } catch (error) {
        //   // console.log(error);
        // }
        drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS,
          { color: '#00FF00', lineWidth: 2 });
        drawLandmarks(canvasCtx, landmarks, { color: '#FF0000', lineWidth: 2 });
      }
    }
    canvasCtx.restore();
  }

  return <div>
    <video hidden ref={videoRef} />
    <canvas className='the-canvas' ref={canvasRef} {...props}></canvas>
  </div>
}