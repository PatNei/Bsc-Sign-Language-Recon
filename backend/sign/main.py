from fastapi import FastAPI
from sign.keypoint_classifier import NormalizedLandmark, NormalizedLandmarks, NormalizedLandmarksDTO
from sign.recogniser import Recogniser
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

app = FastAPI()
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recogniser = Recogniser()

@app.get("/hello")
def read_root():
    return {"Hello": "World"}


@app.post("/annotation")
def get_annotation(landmarksDTO: NormalizedLandmarksDTO) -> str:
    landmarks : NormalizedLandmarks = NormalizedLandmarks([ NormalizedLandmark(element) for element in landmarksDTO.data ])
    return recogniser.get_annotation(landmarks)
    
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)