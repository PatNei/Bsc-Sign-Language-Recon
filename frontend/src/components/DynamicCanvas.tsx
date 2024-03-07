import { ReactElement, useRef, useState, MutableRefObject, useEffect } from 'react';
import { createCamera, createHands } from "../utility/camera";
import { Camera } from '@mediapipe/camera_utils';
import { LandmarkDTO } from '../utility/api';

type CanvasProps = & {
  setLetterRecognizerResponse: ((r: string) => void);
}
export default function Canvas({ setLetterRecognizerResponse }: CanvasProps): ReactElement<CanvasProps> {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [dynamicSignLandmarks, setDynamicSignLandmarks] = useState<LandmarkDTO[][]>([]);
  const cameraRef = useRef<Camera | null>(null)

  useEffect(() => {
    if (!canvasRef.current || !videoRef.current) return
    const canvasCtx = canvasRef.current.getContext('2d')
    cameraRef.current = createCamera(createHands({dynamicSignLandmarks, shouldCaptureDynamicSign: true, setDynamicSignLandmarks, setLetterRecognizerResponse}, {canvasCtx, canvas: canvasRef.current}), videoRef.current)
    return () => {cameraRef.current = null;}
  }, [])

  return <div className="w-full h-full flex justify-center">
    <video hidden className="hidden" ref={videoRef} />
    <canvas className='the-canvas' ref={canvasRef} />
  </div>
}
