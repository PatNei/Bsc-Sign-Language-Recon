import axios from "axios";
import type { NormalizedLandmark } from "@mediapipe/hands";

const baseURL = "http://localhost:8000/";
const min_frames_per_sign = 1512 / 3 / 21;

interface PostState {
  response: string | undefined;
  error: string | undefined;
}
export async function APIPost(url: string, body: unknown): Promise<PostState> {
  let state: PostState = {
    response: undefined,
    error: undefined,
  };
  try {
    const response = await axios.post<string>(baseURL + url, { data: body });
    state = { ...state, response: response.data };
    return state;
    // biome-ignore lint/suspicious/noExplicitAny: <explanation>
  } catch (error: any) {
    state = { ...state, error: error };
    return state;
  }
}

export interface LandmarkDTO {
  x: string;
  y: string;
  z: string;
}

export interface onResultType {
  multiHandLandmarks: NormalizedLandmark[][];
  dynamicSignLandmarks: LandmarkDTO[][];
  shouldCaptureDynamicSign: boolean;
  setDynamicSignLandmarks: React.Dispatch<
    React.SetStateAction<LandmarkDTO[][]>
  >;
  setLetterRecognizerResponse: (r: string) => void;
}

export const onResult = async ({
  multiHandLandmarks,
  dynamicSignLandmarks,
  shouldCaptureDynamicSign,
  setLetterRecognizerResponse,
  setDynamicSignLandmarks,
}: onResultType) => {
  if (!shouldCaptureDynamicSign) {
    setDynamicSignLandmarks([]);
    await gameLogicStaticSign(multiHandLandmarks, async (landmarkDTO) => {
      const postState = await APIPost("annotation", landmarkDTO);
      if (
        postState?.response &&
        !postState.error &&
        setLetterRecognizerResponse
      ) {
        setLetterRecognizerResponse(postState.response);
      }
      if (postState?.error) {
        console.log(postState.error);
      }
    });
  } else {
    await gameLogicDynamicSign(
      dynamicSignLandmarks,
      normalizedLandmarkToDTO(multiHandLandmarks[0]),
      setDynamicSignLandmarks,
      setLetterRecognizerResponse
    );
  }
};

function normalizedLandmarksToLandmarksDTO(
  multiHandLandmarks: NormalizedLandmark[][]
): LandmarkDTO[][] {
  return multiHandLandmarks.map(
    (landmarks: NormalizedLandmark[]): LandmarkDTO[] => {
      return normalizedLandmarkToDTO(landmarks);
    }
  );
}

function normalizedLandmarkToDTO(
  landmarks: NormalizedLandmark[]
): LandmarkDTO[] {
  if (!landmarks) return [];
  return landmarks.map((landmark: NormalizedLandmark): LandmarkDTO => {
    return {
      x: landmark.x.toFixed(20),
      y: landmark.y.toFixed(20),
      z: landmark.z ? landmark.z.toFixed(20) : "0",
    };
  });
}

async function gameLogicStaticSign(
  multiHandLandmarks: NormalizedLandmark[][],
  sendFunction: (landmarkDTO: LandmarkDTO[]) => Promise<void>
) {
  for (const landmarks of multiHandLandmarks) {
    await sendFunction(normalizedLandmarkToDTO(landmarks));
  }
}

async function gameLogicDynamicSign(
  dynamicSignLandmarks: LandmarkDTO[][],
  multiHandLandmarks: LandmarkDTO[],
  setDynamicSignLandmarks: React.Dispatch<
    React.SetStateAction<LandmarkDTO[][]>
  >,
  setLetterRecognizerResponse: (r: string) => void
) {
  if (!multiHandLandmarks || multiHandLandmarks.length === 0) return;

  setDynamicSignLandmarks((prevDynamicSignLandmarks) => {
    let res = prevDynamicSignLandmarks;
    res.push(multiHandLandmarks);
    return res;
  });

  if (dynamicSignLandmarks.length === min_frames_per_sign) {
    const postState = await APIPost("dynamic_annotation", dynamicSignLandmarks);
    if (postState?.response && !postState.error) {
      setLetterRecognizerResponse(postState.response);
    } else if (postState.error) console.log(postState.error);
    setDynamicSignLandmarks([]);
  }
}
