import axios from "axios";
import { useState } from "react";
const baseURL = "http://localhost:8000/"

interface GetResponse {
    isGetLoading: boolean,
    isGetError: boolean,
    error: any,
    response: string | undefined,
    getData: (url: string, params: string) => void
}

export function useAPIGet(): GetResponse {
    interface State {
        isLoading: boolean,
        isError: boolean,
        response: string | undefined,
        error: any
    }
    const [state, setState] = useState<State>({
        isLoading: false,
        isError: false,
        response: undefined,
        error: undefined
    });
    async function getData(url: string, data: string) {
        try {
            // console.log(params)
            let response = await axios.get<string>(baseURL + url, { data: data });
            setState({ ...state, isLoading: false, isError: false, response: response.data });
        } catch (error: any) {
            setState({ ...state, isLoading: false, isError: true, error: error });
        } finally {
            setState({ ...state, isLoading: false });
        }
    }

    return {
        isGetLoading: state.isLoading,
        isGetError: state.isError,
        response: state.response,
        error: state.error,
        getData
    }
}