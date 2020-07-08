from http.server import BaseHTTPRequestHandler, HTTPServer
import socketserver
import json
import cgi
import logging

# adapted from https://gist.github.com/nitaku/10d0662536f37a087e1b
class Camera360Server(BaseHTTPRequestHandler):

    cam_state = {}  # status of cameras, always passed by cameras with GET requests
    cam_logs = {}  # last log of cameras, always passed by cameras with POST requests
    n_cams = None
    root = None
    logger = logging
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

    def do_HEAD(self):
        self._set_headers()

    # GET sends back a Hello world message
    def do_GET(self):
        """
        GET API should provide a json with the following fields:
        state: str - can be:
            "idle" - before anything is done, or after camera is stopped (to be implemented with push button)
            "ready" - camera is initialized
            "capture" - camera is capturing
        req: str - name of method to call from server
        kwargs: dict - any kwargs that need to be parsed to method (can be left out if None)
        log: str - log message to be printed from client on server's log (see self.logger)

        the GET API then decides what action should be taken given the state.
        Client is responsible for updating its status to the current
        """

        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return
        length = int(self.headers.get('content-length'))
        msg = json.loads(self.rfile.read(length).decode('utf-8'))
        # Create or update state of current camera
        self.cam_state[self.address_string()] = msg['state']
        log_msg = f'Cam {self.address_string()} - GET {msg["req"]}'
        self.logger.info(log_msg)
        # check if task exists and sent instructions back
        method = f'get_{msg["req"].lower()}'
        if hasattr(self, method):
            if 'kwargs' in msg:
                kwargs = msg['kwargs']
            else:
                kwargs = {}
            task = getattr(self, method)
            # execute with key-word arguments provided
            r = task(**kwargs)
        else:
            self.send_response(404)
            self.end_headers()
            return
            # return r

        self._set_headers()
        self.wfile.write(json.dumps(r).encode())

    # POST echoes the message adding a JSON field
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))

        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        message = json.loads(self.rfile.read(length))

        # add a property to the object, just to mess with data
        self.logger.info('POST received')
        message['received'] = 'ok'

        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(message).encode())

    def get_root(self):
        """
        :return:
        dict representation of the root folder
        """
        return {'root': self.root}

    def get_task(self):
        """
        Choose a task for the child to perform, and return this
        Currently implemented are:
            init: - initialize camera (done when status of camera is 'idle')
            wait: - tell camera to simply wait and send a request for a task later (typically done when not all cameras are online yet
            capture_until: - capture until a stop (not implemented yet) is given, using kwargs for time and time intervals
                             this is only provided when all cameras in the expected camera rig size are initialized
        :return:
        dict representation of task, including the following fields:
        task: str - name of task method to be performed on child side
        kwargs: dict - set of key word arguments and their values to provide to that task
        """
        # FIXME implement init (when camera is idle and asking for a task)
        # FIXME implement wait (when camera is initialized, but not enough cameras are online)
        # FIXME implement capture_until (only fire this when all cameras are online and initialized)
