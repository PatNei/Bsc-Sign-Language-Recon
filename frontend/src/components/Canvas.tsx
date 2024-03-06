import { ReactElement, useRef, useState, MutableRefObject, useEffect } from 'react';
import { createCamera } from "../utility/camera";
import { Camera } from '@mediapipe/camera_utils';
import { LandmarkDTO, onResult } from '../utility/api';

interface CanvasType {
  canvasRef: MutableRefObject<HTMLCanvasElement | null> | undefined;
  videoRef: MutableRefObject<HTMLVideoElement | null> | undefined;
  canvas: MutableRefObject<HTMLVideoElement | null> | undefined;
  videoElement: MutableRefObject<HTMLVideoElement | null> | undefined;
  canvasCtx: HTMLCanvasElement;
}


type CanvasProps = & {
  setLetterRecognizerResponse: ((r: string) => void);
  shouldCaptureDynamicSign: boolean;
}
export default function Canvas({ shouldCaptureDynamicSign, setLetterRecognizerResponse }: CanvasProps): ReactElement<CanvasProps> {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const [dynamicSignLandmarks, setDynamicSignLandmarks] = useState<LandmarkDTO[][]>([]);
  const [camera, setCamera] = useState<Camera | null>(null)

  useEffect(() => {
    if (!canvasRef.current || !videoRef.current) return
    const canvasCtx = canvasRef.current.getContext('2d')
    setCamera(createCamera(videoRef.current, { canvas: canvasRef.current, canvasCtx }, (result) => {

      onResult({
        multiHandLandmarks: result.multiHandLandmarks,
        dynamicSignLandmarks:
          dynamicSignLandmarks,
        shouldCaptureDynamicSign: shouldCaptureDynamicSign,
        setLetterRecognizerResponse: setLetterRecognizerResponse, setDynamicSignLandmarks: setDynamicSignLandmarks
      })
    }))
  }, [])

  return <div className="w-full h-full flex justify-center">
    <video className='hidden' ref={videoRef} />
    <canvas className='the-canvas' ref={canvasRef} />
  </div>
}
