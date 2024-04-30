import { type ReactElement, useRef, useEffect, useState } from "react";
import { createCamera, createHands } from "../utility/camera";
import type { Camera } from "@mediapipe/camera_utils";
import Countdown from "react-countdown";

type CanvasProps = {
	setLetterRecognizerResponse: (r: string) => void;
};

export default function Canvas({
	setLetterRecognizerResponse,
}: CanvasProps): ReactElement<CanvasProps> {
	const canvasRef = useRef<HTMLCanvasElement>(null);
	const videoRef = useRef<HTMLVideoElement>(null);
	const cameraRef = useRef<Camera | null>(null);
	const countdownRef = useRef<Countdown | null>(null);

	// biome-ignore lint/correctness/useExhaustiveDependencies: <explanation>
	useEffect(() => {
		if (!canvasRef.current || !videoRef.current) return;
		const canvasCtx = canvasRef.current.getContext("2d");
		cameraRef.current = createCamera(
			createHands(
				{
					shouldCaptureDynamicSign: true,
					setLetterRecognizerResponse,
					countdownRef,
				},
				{ canvasCtx, canvas: canvasRef.current },
			),
			videoRef.current,
		);

		return () => {
			cameraRef.current = null;
		};
	}, [countdownRef]);

	return (
		<>
			<div className="w-1200px h-480px flex justify-center">
				{/* biome-ignore lint/a11y/useMediaCaption: <explanation> */}
				<video hidden className="hidden" ref={videoRef} />
				<canvas className="the-canvas" ref={canvasRef} />
			</div>
			<div className="pt-2">
				<Countdown
					autoStart={false}
					renderer={(props) => {
						return (
							<button
								className="min-w-40 bg-red-600 hover:bg-red-500 text-white font-bold py-2 px-4 rounded"
								onClick={(e) => {
									e.preventDefault();
									countdownRef.current?.api?.start();
								}}
							>
								{props.seconds === 3
									? "Click to start"
									: props.completed
										? "Sign now"
										: props.seconds}
							</button>
						);
					}}
					date={Date.now() + 3000}
					ref={countdownRef}
				/>
			</div>
		</>
	);
}
