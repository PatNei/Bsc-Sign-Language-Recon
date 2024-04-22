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

export interface LandmarkSequencesDTO {
  data: LandmarkSequenceDTO[];
}

export interface LandmarkSequenceDTO {
  data: LandmarksDTO[];
}

export interface LandmarksDTO {
  data: LandmarkDTO[];
  handedness: string;
}

export interface LandmarkDTO {
  x: string;
  y: string;
  z: string;
}

export interface onResultType {
  multiHandLandmarks: [NormalizedLandmark[], Handedness][];
  dynamicSignLandmarks: LandmarkSequencesDTO;
  shouldCaptureDynamicSign: boolean;
  setDynamicSignLandmarks: React.Dispatch<
    React.SetStateAction<LandmarkSequencesDTO>
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
    setDynamicSignLandmarks({ data: [] });
    let landmarksDTO = normalizedLandmarksToDTOs(multiHandLandmarks);
    landmarksDTO.data.forEach(async (landmarkDTO, i) => {
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
    setDynamicSignLandmarks(
      await gameLogicDynamicSign(
        dynamicSignLandmarks,
        normalizedLandmarksToDTOs(multiHandLandmarks),
        setLetterRecognizerResponse
      )
    );
  }
};

function normalizedLandmarksToDTOs(
  landmarks: [NormalizedLandmark[], Handedness][]
): LandmarkSequenceDTO {
  return {
    data: landmarks.map((e) => {
      return normalizedLandmarkToDTO(e[0], e[1]);
    }),
  };
}

function normalizedLandmarkSequenceToDTOs(
  landmarks: [NormalizedLandmark[], Handedness][][]
): LandmarksDTO[][] {
  return landmarks.map((e): LandmarksDTO[] => {
    return e.map((landmarks): LandmarksDTO => {
      return normalizedLandmarkToDTO(landmarks[0], landmarks[1]);
    });
  });
}

function normalizedLandmarkToDTO(
  landmarks: NormalizedLandmark[],
  hand: Handedness
): LandmarksDTO {
  if (!landmarks || !hand) return { data: [], handedness: "" };
  return {
    data: landmarks.map((landmark: NormalizedLandmark): LandmarkDTO => {
      return {
        x: landmark.x.toFixed(20),
        y: landmark.y.toFixed(20),
        z: landmark.z ? landmark.z.toFixed(20) : "0",
      };
    }),
    handedness: hand.label,
  };
}

let i = 0;
async function gameLogicDynamicSign(
  dynamicSignLandmarks: LandmarkSequencesDTO,
  multiHandLandmarks: LandmarkSequenceDTO,
  setLetterRecognizerResponse: (r: string) => void
): Promise<LandmarkSequencesDTO> {
  console.log(i);
  if (!multiHandLandmarks || multiHandLandmarks.data.length === 0)
    return dynamicSignLandmarks;
  if (i >= min_frames_per_sign) {
    console.log(`LENGTH: ${dynamicSignLandmarks.data.length}`);
    const postState = await APIPost("dynamic_annotation", dynamicSignLandmarks);
    if (postState?.response && !postState.error) {
      console.log(postState.response);
      setLetterRecognizerResponse(postState.response);
    } else if (postState.error) {
      console.log(postState.error);
    }
    i = 0;
    return { data: [] };
  } else {
    dynamicSignLandmarks.data.concat(multiHandLandmarks);
    i++;
    return dynamicSignLandmarks;
  }
}
