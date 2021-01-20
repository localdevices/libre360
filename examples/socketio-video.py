import datetime
from threading import Thread
import base64
import time
import socketio
import glob

sio = socketio.Client(logger=True)


class WebCamVideoStream:
    def __init__(self, sio, src="*.jpg"):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.sio = sio
        self.sio.parent = self
        fns = glob.glob(src)
        frames = [open(fn, "rb").read() for fn in fns]
        self.stream = frames
        # initialize frame
        self.frame = self.stream[0]
        # initialize the variable used to inidicate if the thread
        # should be stopped
        self.stopped = False

    def start(self):
        self.stopped = False
        # start the thread to read frames from the video stream
        print("Starting live video!!!!")
        Thread(target=self.update, args=()).start()
        # return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        select = 0
        while True:
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise read the next frame from the stream
            # select = int(time.time()) % len(self.stream)
            if select == len(self.stream) - 1:
                select = 0
            else:
                select += 1
            print(select)
            self.frame = self.stream[select]
            self.sio.emit(
                "stream_request", {"image": encode_image(self.frame)}, namespace="/test"
            )
            time.sleep(1.0 / 25)

    def read(self):
        # return the frame most recently read
        return self.frame, self.stopped

    def stop(self, args={}):
        # indicate that the thread should be stopped
        self.stopped = True


def encode_image(image):
    # serialize data
    image = base64.b64encode(image).decode("utf-8")
    # image = f"data:image/jpeg;base64,{image}"
    return image


@sio.event
def connect():
    print("[INFO] Successfully connected to server")


@sio.event
def connect_error():
    print("[INFO] Failed to connect to server.")


@sio.event
def disconnect():
    print("[INFO] Disconnected from server.")


@sio.on("msg_disconnect", namespace="/test")
def disconnect_handler(msg):
    if sio.sid in msg["connected"] and len(msg["connected"]) == 1:
        return "stop"
    print(f"Client {msg['disconnected']} was disconnected")


@sio.on("_video", namespace="/test")
def _video_handler(msg):
    # start the WebCamVideoStream class
    sio.parent.start()


@sio.on("_stop", namespace="/test")
def _stop_handler(msg):
    sio.parent.stop()


# frames = ["Hellos", "This", "Is", "A", "Test"]
def main():
    cam = WebCamVideoStream(sio)
    cam.sio.connect(
        "http://0.0.0.0:5000",
        # transports=['websocket'],
        namespaces=["/test"],
    )

    stream = cam.start()
    #
    # while True:
    #     # select = int(time.time()) % len(frames)
    #     # print(select)
    #     # data = frames[select]
    #     sio.emit('stream_request', {'image': encode_image(stream.frame)}, namespace='/test')
    #     sio.on("msg_stop", stream.stop, namespace="/test")
    #     # sio.emit('my broadcast event', {'data': data}, namespace='/test')
    #     time.sleep(1./5)
    #
    #     if stream.stopped:
    #         break


if __name__ == "__main__":
    main()
