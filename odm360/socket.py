import socketio
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

@sio.on("msg_disconnect", namespace='/test')
def disconnect_handler(msg):
    if sio.sid in msg["connected"] and len(msg["connected"]) == 1:
        return "stop"
    print(f"Client {msg['disconnected']} was disconnected")

@sio.on("_video", namespace="/test")
def _video_handler(msg):
    # start the webcam video

    sio.parent.capture_stream()

@sio.on("_stop", namespace="/test")
def _stop_handler(msg):
    sio.parent.stop_stream()

# TODO: clean up CameraRig after camera_rig is fully integrated in Flask

