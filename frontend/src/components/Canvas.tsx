import { ReactElement, useRef, useState, MutableRefObject } from 'react';
import { Camera2, LandmarkDTO, camera3, renderEverything,onResult } from "./Camera";

interface CanvasType{
  canvasRef: MutableRefObject<HTMLCanvasElement | null> | undefined;
  videoRef: MutableRefObject<HTMLVideoElement | null> | undefined;
  canvas: MutableRefObject<HTMLVideoElement | null> | undefined;
  videoElement: MutableRefObject<HTMLVideoElement | null> | undefined;
  canvasCtx: HTMLCanvasElement;
}


type CanvasProps = & {
  setLetterRecognizerResponse: ((r:string) => void);
  shouldCaptureDynamicSign: boolean;
}
export default function Canvas({shouldCaptureDynamicSign,setLetterRecognizerResponse}: CanvasProps): ReactElement<CanvasProps> {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [dynamicSignLandmarks, setDynamicSignLandmarks] = useState<LandmarkDTO[][]>([]);
  const [camera,setCamera] = useState<camera3 | null>(null)
  if (!camera && videoRef.current != null && canvasRef.current != null) {
    const canvasCtx = canvasRef.current.getContext('2d')
    setCamera(Camera2(videoRef.current,(results) => {
      renderEverything({results: results,canvas:canvasRef.current,canvasCtx: canvasCtx})
      onResult({
        results: results,
        dynamicSignLandmarks: 
        dynamicSignLandmarks,
        useDynamicSign:shouldCaptureDynamicSign,
        setLetterRecognizerResponse: setLetterRecognizerResponse,setDynamicSignLandmarks:setDynamicSignLandmarks
      })
    }))
  }
  if (camera && !camera.isRunning) {
    camera.camera.start();
    setCamera({...camera,isRunning:true})
  }
  return <div className="w-full h-full flex justify-center">
    <video hidden ref={videoRef} />
    <canvas className='the-canvas' ref={canvasRef}/>
  </div>
}
