import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { HAND_CONNECTIONS } from "@mediapipe/hands";
import { result } from "./Camera";

export interface drawType {
    canvas: HTMLCanvasElement | null,
    canvasCtx: CanvasRenderingContext2D | null
}

export async function renderEverything(result: result, { canvas, canvasCtx }: drawType) {
    if (!canvas || !canvasCtx) return;
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    canvasCtx.drawImage(result.image, 0, 0, canvas.width, canvas.height);

    for (const landmarks of result.multiHandLandmarks) {
        drawConnectors(canvasCtx, landmarks, HAND_CONNECTIONS, { color: '#00FF00', lineWidth: 1 });
        drawLandmarks(canvasCtx, landmarks, { color: '#FF0000', lineWidth: 1, radius: 0.8 });
    }

    canvasCtx.restore();


}