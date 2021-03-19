import cv2
from concurrent.futures import ThreadPoolExecutor
import threading

# Function thaat takes in frame and proccess frames
def process_frame(camera, frame):
    
    # TODO - Run Yolo model here
    
    # Right now displaying frame for testing purposes
    cv2.imshow(f'Camera{camera}', frame) 
    cv2.waitKey(1) 


def start_proccesor():
    executor = ThreadPoolExecutor(max_workers=3) 

    # Init Capture objects from all camera streams
    vcap1 = cv2.VideoCapture("rtmp://62.113.210.250/medienasa-live/rbw_high")
    vcap2 = cv2.VideoCapture("rtmp://62.113.210.250/medienasa-live/rbw_high")

    # Read until video is completed
    while True:
        ret, frame1 = vcap1.read()
        ret, frame2 = vcap2.read()
        
        # Start Proccessing frames in different threads
        task1 = executor.submit(process_frame(1, frame1))
        task2 = executor.submit(process_frame(2, frame2))
       


if __name__ == '__main__':
       start_proccesor()
    
    



