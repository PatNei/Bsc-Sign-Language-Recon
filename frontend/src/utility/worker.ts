import { result } from "./camera";

export interface LandmarkDTO {
    x: string;
    y: string;
    z: string;
}

interface onResultType {
    dynamicSignLandmarks: LandmarkDTO[][],
    shouldCaptureDynamicSign: boolean
    setDynamicSignLandmarks: React.Dispatch<React.SetStateAction<LandmarkDTO[][]>>
    setLetterRecognizerResponse: ((r: string) => void)
}

export const onResult = async (result: result, { dynamicSignLandmarks, shouldCaptureDynamicSign, setLetterRecognizerResponse, setDynamicSignLandmarks }: onResultType) => {

    if (!shouldCaptureDynamicSign) {
        setDynamicSignLandmarks([]);
        return;
    }
    let min_frames_per_sign = 24;
    if (result.multiHandLandmarks && result.multiHandLandmarks.length > 0) {
        let resultsDTO = result.multiHandLandmarks.map(e => e.map((landmark): LandmarkDTO => {
            return {
                x: landmark.x.toFixed(20),
                y: landmark.y.toFixed(20),
                z: landmark.z ? landmark.z.toFixed(20) : "0"
            }
        }));
        let landmarks = resultsDTO.length == 1 ? resultsDTO[0] : [];
        const data = dynamicSignLandmarks
        data.push(landmarks)
        setDynamicSignLandmarks(data)
        console.log(shouldCaptureDynamicSign)
        console.log(dynamicSignLandmarks)

        if (dynamicSignLandmarks.length == min_frames_per_sign) {
            // const postState =  await APIPost(`dynamic_annotation`, dynamicSignLandmarks);
            // if (postState.response && !postState.error) {
            //   setLetterRecognizerResponse(postState.response);
            // }
            // else if (postState.error) console.log(postState.error)

            setDynamicSignLandmarks([]);
        }


        // let dynamic_sign = landmarks.slice(Math.max(landmarks.length - min_frames_per_sign, 0));


        // for (const landmarks of results.multiHandLandmarks) {
        // let landmarksDTO: LandmarkDTO[] = landmarks.map((landmark : NormalizedLandmark) : LandmarkDTO => {
        //   return {
        //     x: landmark.x.toFixed(20),
        //     y: landmark.y.toFixed(20),
        //     z: landmark.z ? landmark.z.toFixed(20) : "0"
        //   }
        // })

        // let postState = await APIPost(`annotation`, landmarksDTO);
        // if (postState.response && !postState.error) {
        //   if(props.onResults) props.onResults(postState.response);
        // }
        // else if (postState.error) console.log(postState.error)
    }
}