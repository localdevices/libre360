# Example to test video streaming from a generator to front end
import time
import asyncio
import socketio
import io
from threading import Condition

loop = asyncio.get_event_loop()
sio = socketio.AsyncClient(logger=True, engineio_logger=True)
start_timer = None


async def send_ping():
    global start_timer
    start_timer = time.time()
    await sio.emit("ping_from_client")


@sio.on("connect")
async def on_connect():
    print("connected to server")
    await send_ping()


@sio.on("pong_from_server")
async def on_pong(data):
    global start_timer
    latency = time.time() - start_timer
    print("latency is {0:.2f} ms".format(latency * 1000))
    await sio.sleep(1)
    await send_ping()


async def start_server():
    await sio.connect("http://localhost:5000/test")
    await sio.wait()


if __name__ == "__main__":
    loop.run_until_complete(start_server())
#
# class Camera(object):
#     def __init__(self):
#         import glob
#         fns = glob.glob('/home/hcwinsemius/temp/c9f1c734-ac7a-4241-8988-2d1fb30cc0e7/6/2020-11-10t13:00:30/*.jpg')
#         self.frames = [open(fn, 'rb').read() for fn in fns]
#         self.frames = ['Hello', 'You', 'Great', 'Dude!']
#
#     def get_frame(self):
#         return self.frames[int(time.time()) % len(self.frames)]
#
#
# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
#
#


# ## WITH PiCamera
# import picamera
class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b"\xff\xd8"):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)


#
# # TODO: replace stuff below so that a jpg blob is send over to Flask-SocketIO
# import socketserver
# from http import server
#
# class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
#     allow_reuse_address = True
#     daemon_threads = True
#
# with picamera.PiCamera(resolution='640x480', framerate=24) as camera:
#     output = StreamingOutput()
#     camera.start_recording(output, format='mjpeg')
#     try:
#         address = ('', 8000)
#         server = StreamingServer(address, StreamingHandler)
#         server.serve_forever()
#     finally:
#         camera.stop_recording()
