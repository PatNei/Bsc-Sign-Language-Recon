import os
import cv2 as cv

dir_path = 'dynamic_signs/frames'
min_frame_len = 4

def capture_dynamic_sign(sign_name: str):
    path = f'{dir_path}/{sign_name}'

    if not os.path.isdir(path):
        os.makedirs(path)

    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
        
    capturing = False
    i=0
    j=0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            continue

        cv.imshow('frame', frame)
        if cv.waitKey(33) == ord('c'):
            if not capturing:
                j=0
            file_path = f'{path}/{i}_{j}.png'
            cv.imwrite(file_path, frame)
            print(f'Writing {file_path}')
            if not capturing:
                i+=1
            capturing = True
            j+=1
        else:
            capturing = False    
        
        if cv.waitKey(33) == ord('q'):
            break
        
    cap.release()
    cv.destroyAllWindows()
    
def clean_dynamic_sign_dir(sign_name: str):
    path = f'{dir_path}/{sign_name}'
    images = os.listdir(path)
    group = {}
    for image in images:
        split = image.split("_")
        i = split[0]
        if i not in group:
            group[i] = []
        group[i].append(image)

    for k, v in group.items():
        print(f'{k}: {v}')
        if len(v) <= min_frame_len:
            for image in v:
                os.remove(f'{path}/{image}')
    
capture_dynamic_sign('test')
clean_dynamic_sign_dir('test')