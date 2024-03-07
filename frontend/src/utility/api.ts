import axios from "axios";
import { NormalizedLandmark } from "@mediapipe/hands";

const baseURL = "http://localhost:8000/";

interface PostState {
  response: string | undefined;
  error: string | undefined;
}
export async function APIPost(url: string, body: any): Promise<PostState> {
  let state: PostState = {
    response: undefined,
    error: undefined,
  };
  try {
    let response = await axios.post<string>(baseURL + url, { data: body });
    state = { ...state, response: response.data };
  } catch (error: any) {
    state = { ...state, error: error };
  } finally {
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
  // console.log(shouldCaptureDynamicSign);
  if (!shouldCaptureDynamicSign) {
    setDynamicSignLandmarks([]);

    for (const landmarks of multiHandLandmarks) {
      let landmarksDTO: LandmarkDTO[] = landmarks.map(
        (landmark: NormalizedLandmark): LandmarkDTO => {
          return {
            x: landmark.x.toFixed(20),
            y: landmark.y.toFixed(20),
            z: landmark.z ? landmark.z.toFixed(20) : "0",
          };
        }
      );

      // console.log(JSON.stringify(landmarksDTO));

      let postState = await APIPost(`annotation`, landmarksDTO);
      if (postState.response && !postState.error) {
        if (setLetterRecognizerResponse)
          setLetterRecognizerResponse(postState.response);
      } else if (postState.error) {
        console.log(postState.error);
      }
    }
  } else {
    let min_frames_per_sign = 24;
    if (multiHandLandmarks && multiHandLandmarks.length > 0) {
      let resultsDTO = multiHandLandmarks.map((e) =>
        e.map((landmark): LandmarkDTO => {
          return {
            x: landmark.x.toFixed(20),
            y: landmark.y.toFixed(20),
            z: landmark.z ? landmark.z.toFixed(20) : "0",
          };
        })
      );
      let landmarks = resultsDTO.length == 1 ? resultsDTO[0] : [];
      const data = dynamicSignLandmarks;
      data.push(landmarks);
      setDynamicSignLandmarks(data);
      // console.log(dynamicSignLandmarks);

      if (dynamicSignLandmarks.length == min_frames_per_sign) {
        const postState = await APIPost(
          `dynamic_annotation`,
          dynamicSignLandmarks
        );
        if (postState.response && !postState.error) {
          setLetterRecognizerResponse(postState.response!);
        } else if (postState.error) console.log(postState.error);
      } else {
        setDynamicSignLandmarks([]);
      }

      // let dynamic_sign = landmarks.slice(
      //   Math.max(landmarks.length - min_frames_per_sign, 0)
      // );
    }
  }
};
