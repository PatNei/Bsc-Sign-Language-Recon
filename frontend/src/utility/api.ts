import axios from "axios";
import type { Handedness, NormalizedLandmark } from "@mediapipe/hands";

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
  console.log(body);
  try {
    const response = await axios.post<string>(baseURL + url, body);
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
  multiHandLandmarks: [NormalizedLandmark[], Handedness][];
  dynamicSignLandmarks: [NormalizedLandmark[], Handedness][];
  shouldCaptureDynamicSign: boolean;
  setDynamicSignLandmarks: React.Dispatch<
    React.SetStateAction<[NormalizedLandmark[], Handedness][]>
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
    await gameLogicStaticSign(
      normalizedLandmarksToDTOs(multiHandLandmarks),
      async (landmarkDTOs) => {
        landmarkDTOs.forEach(async (landmarkDTO) => {
          const postState = await APIPost("annotation", {
            data: landmarkDTO[0],
            handedness: landmarkDTO[1],
          });
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
      }
    );
  } else {
    await gameLogicDynamicSign(
      dynamicSignLandmarks,
      dynamicSignLandmarks,
      setDynamicSignLandmarks,
      setLetterRecognizerResponse
    );
  }
};

function normalizedLandmarksToDTOs(
  landmarks: [NormalizedLandmark[], Handedness][]
): [LandmarkDTO[], string][] {
  return landmarks.map((e) => {
    return normalizedLandmarkToDTO(e[0], e[1]);
  });
}

function normalizedLandmarkToDTO(
  landmarks: NormalizedLandmark[],
  hand: Handedness
): [LandmarkDTO[], string] {
  if (!landmarks || !hand) return [[], ""];
  return [
    landmarks.map((landmark: NormalizedLandmark): LandmarkDTO => {
      return {
        x: landmark.x.toFixed(20),
        y: landmark.y.toFixed(20),
        z: landmark.z ? landmark.z.toFixed(20) : "0",
      };
    }),
    hand.label,
  ];
}

async function gameLogicStaticSign(
  multiHandLandmarks: [LandmarkDTO[], string][],
  sendFunction: (landmarkDTO: [LandmarkDTO[], string][]) => Promise<void>
) {
  await sendFunction(multiHandLandmarks);
}

async function gameLogicDynamicSign(
  dynamicSignLandmarks: [NormalizedLandmark[], Handedness][],
  multiHandLandmarks: [NormalizedLandmark[], Handedness][],
  setDynamicSignLandmarks: React.Dispatch<
    React.SetStateAction<[NormalizedLandmark[], Handedness][]>
  >,
  setLetterRecognizerResponse: (r: string) => void
) {
  if (!multiHandLandmarks || multiHandLandmarks.length === 0) return;

  setDynamicSignLandmarks((prevDynamicSignLandmarks) => {
    let res = prevDynamicSignLandmarks;
    res.concat(multiHandLandmarks);
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
