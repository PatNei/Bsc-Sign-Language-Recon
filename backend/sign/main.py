from fastapi import FastAPI
import numpy as np
from sign.landmarks import NormalizedLandmark, NormalizedLandmarks, NormalizedLandmarksDTO, NormalizedLandmarksSequence, NormalizedLandmarksSequenceDTO
from sign.recogniser import Recogniser
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from sign.trajectory import TrajectoryBuilder

    

app = FastAPI()
origins = [
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://0.0.0.0:3000",
    "http://localhost:8001",
    "*"
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
    landmarks:NormalizedLandmarks = NormalizedLandmarks(handedness=landmarks.handedness,data=[NormalizedLandmark(element) for element in landmarksDTO.data])
    return recogniser.get_annotation(landmarks)

@app.post("/dynamic_annotation")
def get_dynamic_annotation(landmarksDTO: NormalizedLandmarksSequenceDTO) -> str:
    return recogniser.get_dynamic_annotation(landmarksDTO)
    
if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
    
def dev():
    uvicorn.run("sign.main:app", host="localhost", port=8000, reload=True)
    
def prod():
    uvicorn.run("sign.main:app", host="0.0.0.0", port=8000)