import {
	type NormalizedLandmark,
	drawConnectors,
	drawLandmarks,
} from "@mediapipe/drawing_utils";
import { HAND_CONNECTIONS } from "@mediapipe/hands";

interface result {
	image: CanvasImageSource;
	multiHandLandmarks: NormalizedLandmark[][];
}

export interface drawType {
	canvas: HTMLCanvasElement | null;
	canvasCtx: CanvasRenderingContext2D | null;
}

function drawCaptureCircle(ctx: CanvasRenderingContext2D,width:number,height?:number) {
	ctx.beginPath();
	ctx.arc(width-20, 20, 5, 0, 2 * Math.PI);
    ctx.fillStyle = "red"
    ctx.fill()
	ctx.stroke();
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

	drawCaptureCircle(canvasCtx,canvas.width);

	canvasCtx.restore();
	// canvasCtx.save();
	// canvasCtx.strokeText(`FPS: ${performance.now() - oldPerf}`, 10, 10)
	// canvasCtx.restore();
}
