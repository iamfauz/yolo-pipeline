import cv2
from concurrent.futures import ThreadPoolExecutor, wait
import threading
from flask import Response, Flask, render_template
import argparse 

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
camera_id = 1
outputFrame = None
lock = threading.Lock()
 
# initialize a flask object
app = Flask(__name__)


# Global Camera Streams 
# Index will correspond to camera ID
camera_streams = []

class CameraStream:
    def __init__(self, id, url):
        self.id = id
        self.vcap = cv2.VideoCapture(url)

# Function thaat takes in frame and proccess frames
def process_frame(camera, frame):
    
    #TODO - Run Yolo model here
    
    # Right now displaying frame for testing purposes
    cv2.imshow(f'Camera{camera}', frame) 
    cv2.waitKey(1) 
    return frame


def start_proccesor():
    global outputFrame, lock

    executor = ThreadPoolExecutor(max_workers=3) 

   
    i=1
    # Read until video is completed
    while True:
        
        # Reading frames from each camera
        frames = []
        for i in range(len(camera_streams)):
            ret, frame = camera_streams[i].read()
            frames.append(frame)


        # Start Proccessing on each frames
        task_futures = []
        for i in range(len(frames)):
             task = executor.submit(process_frame, i, frames[i])
             task_futures.append(task)

        # Wait for all futures to complete
        wait(task_futures)

        

        with lock:
            if i<0:
                outputFrame = task_futures[0].result().copy()
            else:
                outputFrame = task_futures[1].result().copy()
        i=i*-1



@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")

def generate():
    # grab global references to the output frame and lock variables
    global outputFrame, lock
 
    # loop over frames from the output stream
    while True:
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if outputFrame is None:
                continue
 
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", outputFrame)
 
            # ensure the frame was successfully encoded
            if not flag:
                continue
 
        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + 
            bytearray(encodedImage) + b'\r\n')

@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':

    # Argument Parsing
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=False, default='192.168.70.145',
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=False, default=8000, 
        help="ephemeral port number of the server (1024 to 65535)")

    args = vars(ap.parse_args())

    # Init Capture objects from all camera streams
    vcap1 = cv2.VideoCapture("rtmp://62.113.210.250/medienasa-live/rbw_high")
    vcap2 = cv2.VideoCapture("rtmp://62.113.210.250/medienasa-live/rbw_high")
    #vcap2 = cv2.VideoCapture('rtsp://freja.hiof.no:1935/rtplive/_definst_/hessdalen03.stream')
    
    # Added the stream objects to global variable
    camera_streams.append(vcap1)
    camera_streams.append(vcap2)
    
    # Start Proccessor in different thread
    t = threading.Thread(target=start_proccesor)
    t.daemon = True
    t.start()
    
     # Start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)



