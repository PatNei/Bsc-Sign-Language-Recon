import { type ReactElement, useRef, useEffect } from "react";
import { createCamera, createHands } from "../utility/camera";
import type { Camera } from "@mediapipe/camera_utils";

type CanvasProps = {
  setLetterRecognizerResponse: (r: string) => void;
};
export default function Canvas({
  setLetterRecognizerResponse,
}: CanvasProps): ReactElement<CanvasProps> {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const cameraRef = useRef<Camera | null>(null);

  // biome-ignore lint/correctness/useExhaustiveDependencies: <explanation>
  useEffect(() => {
    if (!canvasRef.current || !videoRef.current) return;
    const canvasCtx = canvasRef.current.getContext("2d");
    cameraRef.current = createCamera(
      createHands(
        {
          shouldCaptureDynamicSign: true,
          setLetterRecognizerResponse,
        },
        { canvasCtx, canvas: canvasRef.current }
      ),
      videoRef.current
    );
    return () => {
      cameraRef.current = null;
    };
  }, []);

  return (
    <div className="w-full h-full flex justify-center">
      {/* biome-ignore lint/a11y/useMediaCaption: <explanation> */}
      <video hidden className="hidden" ref={videoRef} />
      <canvas className="the-canvas" ref={canvasRef} />
    </div>
  );
}
