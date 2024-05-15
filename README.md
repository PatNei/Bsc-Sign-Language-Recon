# Sign language Recognition

## Data

From here:
Kaggle ASL Alphabet: https://www.kaggle.com/datasets/grassknoted/asl-alphabet

Kaggle Sign Language Videos \[J & Z\]: https://www.kaggle.com/datasets/signnteam/asl-sign-language-alphabet-videos-j-z

Youtube ID's for scraper: https://github.com/google-research/google-research/tree/master/youtube_asl

## Training
We have provided helper scripts to train the static and dynamic models
- Instructions on how to train the dynamic model can be found by running running `poetry run train_dynamic_model --help`
- Training the static model can be done with `poetry run train_static_model` will start training the static svc model immediately

these scripts will output a log file containing various statistics about the model, it will also output a confusion matrix as a .png

## Prerequisites

- [PyEnchant prerequisites listed here](https://pyenchant.github.io/pyenchant/install.html)
- We recommend managing Python dependencies with [python-poetry](https://python-poetry.org/). Optionally run `pip install -r requirements.txt` before running the backend
- [Node.js](https://nodejs.org/)

## Running the backend

The backend can be started with the Poetry dependency management tool Poetry. With poetry installed, run `poetry install` followed by `poetry run prod` from within the backend directory

We supply a pre-trained random forest model. In order to use the file you have to unzip it and change the `DYNAMIC_MODEL_PATH` found in `backend/sign/CONST.py` to the correct path

the same applies to the static model with the `STATIC_MODEL_PATH` instead

## Running the frontend

The frontend can be ran using npm. From within the frontend directory run commands `npm i` followed by `npm run prod`
The frontend can be accessed through your browser at http://localhost:5002
