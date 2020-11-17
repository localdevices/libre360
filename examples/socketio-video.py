import datetime
from threading import Thread
import base64
import time
import socketio
import glob
# import cv2


sio = socketio.Client(logger=True)

@sio.event
def connect():
    print('[INFO] Successfully connected to server')


@sio.event
def connect_error():
    print('[INFO] Failed to connect to server.')


@sio.event
def disconnect():
    print('[INFO] Disconnected from server.')


fns = glob.glob('/home/hcwinsemius/temp/phone/*.jpg')
frames = [open(fn, 'rb').read() for fn in fns]
# frames = ["Hellos", "This", "Is", "A", "Test"]
def main():
    sio.connect('http://0.0.0.0:5000',
                # transports=['websocket'],
                namespaces=['/test'],
                )

    while True:
        select = int(time.time()) % len(frames)
        print(select)
        data = frames[select]
        sio.emit('stream_request', {'image': encode_image(data)}, namespace='/test')
        # sio.emit('my broadcast event', {'data': data}, namespace='/test')
        time.sleep(1)

def encode_image(image):
    # serialize data
    image = base64.b64encode(image).decode('utf-8')
    image = f"data:image/jpeg;base64,{image}"
    return image

if __name__ == "__main__":
    main()