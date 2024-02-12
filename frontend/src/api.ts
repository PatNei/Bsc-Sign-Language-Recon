import axios from "axios";
import { useState } from "react";
const baseURL = "http://localhost:8000/"

interface GetResponse {
    response: string | undefined,
    error: string | undefined,
    postData: (url: string, body: any) => Promise<void>
}

export function useAPIPost(): GetResponse {
    interface State {
        response: string | undefined,
        error: string | undefined
    }
    const [state, setState] = useState<State>({
        response: undefined,
        error: undefined
    });
    async function postData(url: string, body: any) {
        try {
            let response = await axios.post<string>(baseURL + url, { data: body });
            setState({ ...state, response: response.data });
        } catch (error: any) {
            setState({ ...state, error: error });
        }
    }

    return {
        response: state.response,
        error: state.error,
        postData: postData
    }
}