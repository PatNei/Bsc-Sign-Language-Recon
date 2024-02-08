import axios from "axios";
import { useState } from "react";
const baseURL = "http://127.0.0.1:8000/"

interface GetResponse {
    isGetLoading: boolean,
    isGetError: boolean,
    getData: <TParams, TResponse>(url: string, params: TParams) => Promise<TResponse>
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
    async function getData<TParams, TResponse>(url: string, params: TParams): Promise<TResponse> {
        try {
            // console.log(params)
            let response = await axios.get<TResponse>(baseURL + url, { data: params });
            console.log(response.data)
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