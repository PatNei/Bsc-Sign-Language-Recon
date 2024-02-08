from fastapi import FastAPI
from pydantic import BaseModel
from recogniser.recogniser import Recogniser
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

recogniser = Recogniser()

class NormalizedLandmark(BaseModel):
    x: float
    y: float
    z: float | None = None
    visibility: float | None = None

# class NormalizedLandmarks(BaseModel): list[NormalizedLandmark]

@app.get("/hello")
def read_root():
    return {"Hello": "World"}


@app.get("/annotation")
def get_annotation(landmarks: list[NormalizedLandmark]) -> str:
    print(landmarks)
    return {"response": recogniser.get_annotation(landmarks), "landmarks": landmarks}