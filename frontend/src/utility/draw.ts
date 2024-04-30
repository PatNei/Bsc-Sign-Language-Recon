import {
	type NormalizedLandmark,
	drawConnectors,
	drawLandmarks,
} from "@mediapipe/drawing_utils";
import { HAND_CONNECTIONS } from "@mediapipe/hands";

const butXPad = 20;
const butYPad = 10;
const butWidth = 5;

interface result {
	image: CanvasImageSource;
	multiHandLandmarks: NormalizedLandmark[][];
}

export interface drawType {
	canvas: HTMLCanvasElement | null;
	canvasCtx: CanvasRenderingContext2D | null;
}

function drawCaptureCircle(
	ctx: CanvasRenderingContext2D,
	butX: number,
	butY: number,
) {
	ctx.beginPath();
	ctx.arc(butX, butY, butWidth, 0, 2 * Math.PI);
	ctx.fillStyle = "red";
	ctx.fill();
	ctx.stroke();
}

function calculateDistanceToButton(
	butX: number,
	butY: number,
	canvas: HTMLCanvasElement,
	NormalizedLandmarks?: NormalizedLandmark[],
) {
	if (!NormalizedLandmarks) return;
	const indexFinger = NormalizedLandmarks[7];
	const fingX = indexFinger.x * canvas.width;
	const fingY = indexFinger.y * canvas.height;
	const distX = Math.abs(butX - fingX + butWidth / 2);
	const distY = Math.abs(butY - fingY - butWidth / 2);
	console.log("ButX", butX);
	console.log("ButY", butY);
	console.log("distX", distX);
	console.log("distY", distY);
	console.log("fingX", fingX);
	console.log("fingY", fingY);
}

export async function renderEverything(
	result: result,
	{ canvas, canvasCtx }: drawType,
) {
	if (!canvas || !canvasCtx) return;
	// const oldPerf = performance.now()
	canvasCtx.save();
	canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
	canvasCtx.drawImage(result.image, 0, 0, canvas.width, canvas.height);
	for (let i = 0; i < result.multiHandLandmarks.length; i++) {
		drawConnectors(canvasCtx, result.multiHandLandmarks[i], HAND_CONNECTIONS, {
			color: "#00FF00",
			lineWidth: 1,
		});
		drawLandmarks(canvasCtx, result.multiHandLandmarks[i], {
			color: "#FF0000",
			lineWidth: 1,
			radius: 0.8,
		});
	}
	const butX = canvas.width - butXPad;
	drawCaptureCircle(canvasCtx, butX, butYPad);
	calculateDistanceToButton(
		butX,
		butYPad,
		canvas,
		result.multiHandLandmarks[0],
	);

	canvasCtx.restore();
	// canvasCtx.save();
	// canvasCtx.strokeText(`FPS: ${performance.now() - oldPerf}`, 10, 10)
	// canvasCtx.restore();
}
