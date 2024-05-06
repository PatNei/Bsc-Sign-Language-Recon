import datetime
import logging
import os
from pathlib import Path


def setup_logging(path):
    # Setup Logging
    BASE_PATH = Path().cwd().joinpath("./logs")
    if not os.path.exists(BASE_PATH):
        os.mkdir(BASE_PATH)

    BASE_PATH = BASE_PATH.joinpath(path)
    if not os.path.exists(BASE_PATH):
        os.mkdir(BASE_PATH)
        
    CURRENT_DATE = datetime.datetime.now().strftime("%d-%m-%Y")
    BASE_PATH = BASE_PATH.joinpath(CURRENT_DATE)
    if not os.path.exists(BASE_PATH):
        os.mkdir(BASE_PATH)

    CURRENT_TIME = datetime.datetime.now().strftime("%d-%m-%Y(%H-%M-%S)")
    logging.basicConfig(filename=BASE_PATH.joinpath(f"{CURRENT_TIME}.log"),level=logging.INFO)
        