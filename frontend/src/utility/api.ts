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
  //   console.log(shouldCaptureDynamicSign);
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
    const newDynamicSignLandmarks = dynamicSignLandmarks.concat(
      normalizedLandmarkToLandmarkDTO(multiHandLandmarks)
    );
    setDynamicSignLandmarks(newDynamicSignLandmarks);
    console.log(dynamicSignLandmarks);
    await gameLogicDynamicSign(
      newDynamicSignLandmarks,
      multiHandLandmarks[0],
      setDynamicSignLandmarks,
      setLetterRecognizerResponse
    );

    // );
  }
};

function normalizedLandmarkToLandmarkDTO(
  multiHandLandmarks: NormalizedLandmark[][]
): LandmarkDTO[][] {
  return multiHandLandmarks.map(
    (landmarks: NormalizedLandmark[]): LandmarkDTO[] => {
      return landmarks.map((landmark: NormalizedLandmark): LandmarkDTO => {
        return {
          x: landmark.x.toFixed(20),
          y: landmark.y.toFixed(20),
          z: landmark.z ? landmark.z.toFixed(20) : "0",
        };
      });
    }
  );
}

async function gameLogicStaticSign(
  multiHandLandmarks: NormalizedLandmark[][],
  sendFunction: (landmarkDTO: LandmarkDTO[]) => Promise<void>
) {
  for (const landmarks of multiHandLandmarks) {
    const landmarksDTO: LandmarkDTO[] = landmarks.map(
      (landmark: NormalizedLandmark): LandmarkDTO => {
        return {
          x: landmark.x.toFixed(20),
          y: landmark.y.toFixed(20),
          z: landmark.z ? landmark.z.toFixed(20) : "0",
        };
      }
    );
    await sendFunction(landmarksDTO);
    // console.log(JSON.stringify(landmarksDTO));
  }
}

async function gameLogicDynamicSign(
  multiHandLandmarks: LandmarkDTO[][],
  dynamicSignLandmarks: LandmarkDTO[],
  setDynamicSignLandmarks: React.Dispatch<
    React.SetStateAction<LandmarkDTO[][]>
  >,
  setLetterRecognizerResponse: (r: string) => void
) {
  if (multiHandLandmarks && multiHandLandmarks.length > 0) {
    const resultsDTO = multiHandLandmarks.map((e) =>
      e.map((landmark): LandmarkDTO => {
        return {
          x: (+landmark.x).toFixed(20).toString(),
          y: (+landmark.y).toFixed(20).toString(),
          z: landmark.z ? (+landmark.z).toFixed(20).toString() : "0",
        };
      })
    );
    const landmarks = resultsDTO.length >= 1 ? resultsDTO[0] : [];
    const data = multiHandLandmarks;
    data.push(landmarks);

    if (landmarks.length === 0) return;

    if (dynamicSignLandmarks.length === min_frames_per_sign) {
      const postState = await APIPost(
        "dynamic_annotation",
        dynamicSignLandmarks
      );
      if (postState?.response && !postState.error) {
        setLetterRecognizerResponse(postState.response);
        console.log(postState.response);
      } else if (postState.error) console.log(postState.error);
    }

    setDynamicSignLandmarks([]);
    console.log("New iteration.");
    // let dynamic_sign = landmarks.slice(
    //   Math.max(landmarks.length - min_frames_per_sign, 0)
  }
}
