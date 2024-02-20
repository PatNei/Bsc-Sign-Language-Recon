import axios from "axios";

const baseURL = import.meta.env.VITE_baseURL + "/"

interface PostState {
    response: string | undefined,
    error: string | undefined
}
export async function APIPost(url: string, body: any): Promise<PostState> {
    let state: PostState = {
        response: undefined,
        error: undefined
    };

    try {
        let response = await axios.post<string>(baseURL + url, { data: body });
        state = { ...state, response: response.data };
    } catch (error: any) {
        state = { ...state, error: error };
    } finally {
        return state
    }
}