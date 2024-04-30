import { type ReactElement, useRef, useState, useEffect } from "react";
import { createCamera, createHands } from "../utility/camera";
import type { Camera } from "@mediapipe/camera_utils";
import type { LandmarkDTO } from "../utility/api";

type CanvasProps = {
	setLetterRecognizerResponse: (r: string) => void;
};
export default function Canvas({
	setLetterRecognizerResponse,
}: CanvasProps): ReactElement<CanvasProps> {
	const canvasRef = useRef<HTMLCanvasElement>(null);
	const videoRef = useRef<HTMLVideoElement>(null);
	const [dynamicSignLandmarks, setDynamicSignLandmarks] = useState<
		LandmarkDTO[][]
	>([]);
	const cameraRef = useRef<Camera | null>(null);

	// biome-ignore lint/correctness/useExhaustiveDependencies: <explanation>
	useEffect(() => {
		if (!canvasRef.current || !videoRef.current) return;
		const canvasCtx = canvasRef.current.getContext("2d");
		cameraRef.current = createCamera(
			createHands(
				{
					dynamicSignLandmarks,
					shouldCaptureDynamicSign: false,
					setDynamicSignLandmarks,
					setLetterRecognizerResponse,
				},
				{ canvasCtx, canvas: canvasRef.current },
			),
			videoRef.current,
		);
		return () => {
			cameraRef.current = null;
		};
	}, []);

	return (
		<div className="max-w-[720px] max-h-[480px] flex justify-center">
			{/* biome-ignore lint/a11y/useMediaCaption: <explanation> */}
			<video hidden className="hidden" ref={videoRef} />
			<canvas height={240} width={480} className="the-canvas" ref={canvasRef} />
		</div>
	);
}
