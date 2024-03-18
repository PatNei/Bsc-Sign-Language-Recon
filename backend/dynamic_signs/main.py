import os
import sys
import cv2 as cv

dir_path = 'dynamic_signs/frames'


def capture_dynamic_sign(sign_name: str, dir_path: str = dir_path):
    path = f'{dir_path}/{sign_name}'

    if not os.path.isdir(path):
        os.makedirs(path)

    cap = cv.VideoCapture(0)
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
        
    capturing = False
    i=max([int(file_name[0]) for file_name in os.listdir(path)])+1 if len(os.listdir(path)) > 0 else 0
    j=0
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            continue

        cv.imshow('frame', cv.flip(frame, cv.ROTATE_180))
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
    
def clean_dynamic_sign_dir(sign_name: str, dir_path:str = dir_path, min_frame_len = 4):
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

if __name__ == '__main__':
    args = sys.argv[1:]
    if len(args) < 1:
        print("<usage> \n\t\"gesture-name\" \n\t-test")
        exit(1)
    gesture_name = args[0].upper()
    if len(args) > 2 and args[1].upper() == "-test".upper():
        dir_path = "dynamic_signs/test"
        capture_dynamic_sign(gesture_name, dir_path=dir_path)
        clean_dynamic_sign_dir(gesture_name, dir_path=dir_path)
    else:
        capture_dynamic_sign(gesture_name)
        clean_dynamic_sign_dir(gesture_name)