import { NormalizedLandmark } from "@mediapipe/drawing_utils";
import axios from "axios";
import { useState } from "react";
const baseURL = "http://127.0.0.1:8000"
const annotationEndpoint = "annotations"

interface GetResponse {
    isGetLoading: boolean,
    isGetError: boolean,
    getData: <TParams, TResponse>(url: string, params: TParams, withCredentials:boolean) => Promise<TResponse>
}

const generateRequest = <T>(method:"GET" | "POST" | "DELETE" | "PUT",data:T) => {
    let request = {
        method: method,
        headers: {
            'Content-Type':'application/json'
        },
        body: JSON.stringify(data)
    }
    return request
} 

export async function getAnnotations(landmarks:NormalizedLandmark[]) {
    let request = generateRequest('GET',landmarks);
    let response = await fetch(`${baseURL}/${annotationEndpoint}`, request)
    console.log(response)

}

export function useAPIGet(): GetResponse {
    interface State {
        isLoading: boolean,
        isError: boolean
    }
    const [state, setState] = useState<State>({
        isLoading: false,
        isError: false,
    });
    async function getData<TParams,TResponse>(url: string, params: TParams): Promise<TResponse> {
        try {
            // console.log(params)
            let response = await axios.get<TResponse>(baseURL + url, { data: params });
            setState({ isLoading: false, isError: false });
            return response.data;
        } catch (error) {
            setState({ isLoading: false, isError: true });
            throw error;
        } finally {
            setState({ ...state, isLoading: false });
        }
    }

    return {
        isGetLoading: state.isLoading,
        isGetError: state.isError,
        getData
    }
}