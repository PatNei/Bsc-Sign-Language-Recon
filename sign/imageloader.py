import cv2 as cv
from PIL import Image
import os

import numpy as np

class LabelledImage:
    def __init__(self, label, data) -> None:
        self.data = data
        self.label = label

    def __str__(self):
        return "<< " + self.label + ": \n\t" + str(self.data)[:50] + " >>\n"

def load_images_from_directory(base_path, amount = 50) -> list[LabelledImage]:
    lablledImages = []

    for subdir,_,files in os.walk(base_path):
        if subdir == base_path:
            continue
        
        label = subdir.replace(base_path, '')
        data = []
        
        for idx, file_name in enumerate(files):
            if idx >= amount:
                continue
                
            imgPath = subdir + '/' + file_name
            img = np.asarray(Image.open(imgPath))
            data.append(img)

        lablledImages.append( LabelledImage(label, data) )
    
    return lablledImages