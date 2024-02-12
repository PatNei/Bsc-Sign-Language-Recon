import axios from "axios";
const baseURL = "http://localhost:8000/"

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