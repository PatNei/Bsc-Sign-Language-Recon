import { NormalizedLandmark, drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { HAND_CONNECTIONS } from "@mediapipe/hands";

interface result {
    image: CanvasImageSource
    multiHandLandmarks: NormalizedLandmark[][]
}

export interface drawType {
    canvas: HTMLCanvasElement | null,
    canvasCtx: CanvasRenderingContext2D | null
}

export async function renderEverything(result: result, { canvas, canvasCtx }: drawType) {
    if (!canvas || !canvasCtx) return;
    // const oldPerf = performance.now()
    canvasCtx.save();
    canvasCtx.clearRect(0, 0, canvas.width, canvas.height);
    canvasCtx.drawImage(result.image, 0, 0, canvas.width, canvas.height);
    for (var i = 0; i < result.multiHandLandmarks.length; i++) {
        drawConnectors(canvasCtx, result.multiHandLandmarks[i], HAND_CONNECTIONS, { color: '#00FF00', lineWidth: 1 });
        drawLandmarks(canvasCtx, result.multiHandLandmarks[i], { color: '#FF0000', lineWidth: 1, radius: 0.8 });
    }
    canvasCtx.restore();
    // canvasCtx.save();
    // canvasCtx.strokeText(`FPS: ${performance.now() - oldPerf}`, 10, 10)
    // canvasCtx.restore();


}