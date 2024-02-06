import React, { ReactElement, useRef ,CanvasHTMLAttributes, useEffect} from 'react';
import './App.css';
import {drawConnectors, drawLandmarks} from '@mediapipe/drawing_utils';
import {HAND_CONNECTIONS, InputImage} from '@mediapipe/holistic';
import {Camera} from "@mediapipe/camera_utils";
import {Hands} from "@mediapipe/hands";
interface State{
  shouldCapture: boolean;
}

function onResults(results: { image: CanvasImageSource; multiHandLandmarks: any; }, canvas: HTMLCanvasElement ,canvasCtx: CanvasRenderingContext2D) {
  canvasCtx.save();
      canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
      canvasCtx.drawImage(
        results.image, 0, 0, canvas.width, canvas.height);
        if (results.multiHandLandmarks) {
          console.log(results.multiHandLandmarks)
          for (const landmarks of results.multiHandLandmarks) {
            drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS,
              {color: '#00FF00', lineWidth: 5});
              drawLandmarks(canvasCtx, landmarks, {color: '#FF0000', lineWidth: 2});
            }
          }
          canvasCtx.restore();
}

function Canvas(props?:CanvasHTMLAttributes<HTMLCanvasElement>) : ReactElement{
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
      const hands = new Hands({locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
      }});
          
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
        await hands.send({image: videoElement as unknown as InputImage});
      },
      width: 1280,
      height: 720
    });
    camera.start();
  }, []);
  return <div>
      <video hidden ref={videoRef} />
      <canvas className='the-canvas' ref={canvasRef} {...props}></canvas>
  </div>
  }

function App() {
  const [state, setState] = React.useState<State>({shouldCapture: false});
      
      return (
        <div className="App">
          <div className="container">
            <Canvas />
          </div>
          <button onClick={_ => setState({...state, shouldCapture: !state.shouldCapture})} >
            Hello
          </button>
        </div>
        );
}
      
      export default App;
      