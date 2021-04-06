import cv2
from concurrent.futures import ThreadPoolExecutor, wait
import threading
from flask import Response, Flask, render_template
import argparse 
from stream_manager import StreamManager
import time

# initialize the output frame and a lock used to ensure thread-safe
# exchanges of the output frames (useful when multiple browsers/tabs are viewing the stream)
camera_id = 1
lock = threading.Lock()
 
# Initialize a flask object
app = Flask(__name__)

# Init Stream Manager
camera_streams_urls = ["rtmp://62.113.210.250/medienasa-live/rbw_high", "rtmp://62.113.210.250/medienasa-live/rbw_high"]
stream_manager = StreamManager(camera_streams_urls)

class CameraStream:
    def __init__(self, id, url):
        self.id = id
        self.vcap = cv2.VideoCapture(url)

# Function thaat takes in frame and proccess frames
def process_frame(camera, frame):
    
    #TODO - Run Yolo model here
    
    # Right now displaying frame for testing purposes
    if camera == 1:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    #cv2.imshow(f'Camera{camera}', frame) 
    #cv2.waitKey(1) 
    return frame


def start_proccesor():
    global lock

    executor = ThreadPoolExecutor(max_workers=3) 

    # Read until video is completed
    while True:
        
        # Reading frames from each camera
        frames = stream_manager.get_latest_frames()

        results = stream_manager.proccess_frames(executor, frames, process_frame)

        stream_manager.set_current_output_frame(frames[1])
        #time.sleep(1)




@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html")

@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(stream_manager.generate_stream_from_output_frame(),
        mimetype = "multipart/x-mixed-replace; boundary=frame")

if __name__ == '__main__':

    # Argument Parsing
    ap = argparse.ArgumentParser()
    ap.add_argument("-i", "--ip", type=str, required=False, default='localhost',
        help="ip address of the device")
    ap.add_argument("-o", "--port", type=int, required=False, default=8000, 
        help="Port number of the server (1024 to 65535)")

    args = vars(ap.parse_args())


    # Start Proccessor in different thread
    t = threading.Thread(target=start_proccesor)
    t.daemon = True
    t.start()
    
     # Start the flask app
    app.run(host=args["ip"], port=args["port"], debug=True,
        threaded=True, use_reloader=False)



