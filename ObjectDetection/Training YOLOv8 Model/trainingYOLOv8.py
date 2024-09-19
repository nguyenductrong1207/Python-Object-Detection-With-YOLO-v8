from ultralytics import YOLO
import os
HOMEDIR = 'C:\\......'
os.chdir(HOMEDIR)

model = YOLO(HOMEDIR + '\\yolov8x.pt', task='runs')
results = model.train(data=r'C:\......data.yaml', epochs = 1000, imgsz=192 , device=0)