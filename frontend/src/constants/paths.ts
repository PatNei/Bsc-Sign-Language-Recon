export const IS_PROD = import.meta.env.MODE === "Production"
export const HANDS_PATH = (() => {
    const hands_path = import.meta.env.VITE_HANDS_PATH
    if (hands_path) return hands_path
    return "/Hands"
})()