import threading
from concurrent.futures import ThreadPoolExecutor, wait
import cv2


DEFUALT_CAMERA_ID = 1

# Class the handles all streaming related tasks
class StreamManager:
    def __init__(self, urls):
        self.stream_urls = urls
        self.lock = threading.Lock()
        self.current_camera_id = DEFUALT_CAMERA_ID
        self.camera_streams = get_cap_objects_from_urls(urls)

    # Runs a proccssor function on each frame and return the results
    def proccess_frames(self, executor, frames, process_func):
        # Start Proccessing on each frames
        task_futures = []
        for i in range(len(frames)):
            task = executor.submit(process_func, i, frames[i])
            task_futures.append(task)

        # Wait for all futures to complete
        wait(task_futures)
            
        # Create results array 
        results = []
        for i in range(len(task_futures)): 
            results.append(task_futures[i].result())
        return results
        
    # Method that return the latest frames from all camera streams
    def get_latest_frames(self):
        camera_streams = self.camera_streams
        # Reading frames from each camera
        frames = []
        for i in range(len(camera_streams)):
            ret, frame = camera_streams[i].read()
            frames.append(frame)
        return frames


    # Method to switch current camera id
    def switch_camera(self, id):
        with self.lock:
            self.current_camera_id = id

    def generate_stream_from_camera_id(self):
        camera_streams_urls = self.stream_urls
        
        vcap = get_cap_objects_from_urls(camera_streams_urls)

        while True:
            # wait until the lock is acquired
            with self.lock:
                
                ret, output_frame = vcap[self.current_camera_id].read() 
                
            if output_frame is None:
                continue

            # Encode the frame in JPEG format
            (flag, encoded_image) = cv2.imencode(".jpg", output_frame.copy())

            # Ensure the frame was successfully encoded
            if not flag:
                continue
    
            # yield the output frame in the byte format
            yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
                bytearray(encoded_image) + b'\r\n')


def get_cap_objects_from_urls(urls):
    vcaps = []
    for i in range(len(urls)):
        vcaps.append(cv2.VideoCapture(urls[i]))
    return vcaps