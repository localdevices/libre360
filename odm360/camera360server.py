from http.server import BaseHTTPRequestHandler
import json
import cgi
import logging
import numpy as np
import time
import datetime

# adapted from https://gist.github.com/nitaku/10d0662536f37a087e1b
class Camera360Server(BaseHTTPRequestHandler):
    # add a number of properties to class
    cam_state = {}  # status of cameras, always passed by cameras with GET requests
    cam_logs = {}  # last log of cameras, always passed by cameras with POST requests
    n_cams = None
    root = None
    start_time = None
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
        """
        POST API should provide a json with the following fields:
        req: str - name of method for posting to call from server (e.g. log)
        kwargs: dict - any kwargs that need to be parsed to method (can be left out if None)
        the POST API then decides what action should be taken based on the POST request.
        POST API will also return a result back
        """
        ctype, pdict = cgi.parse_header(self.headers.get('content-type'))
        # refuse to receive non-json content
        if ctype != 'application/json':
            self.send_response(400)
            self.end_headers()
            return

        # read the message and convert it into a python dictionary
        length = int(self.headers.get('content-length'))
        msg = json.loads(self.rfile.read(length))

        # show request in log
        log_msg = f'Cam {self.address_string()} - POST {msg["req"]}'
        self.logger.info(log_msg)

        # check if task exists and sent instructions back
        method = f'post_{msg["req"].lower()}'
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

        # send the message back
        self._set_headers()
        self.wfile.write(json.dumps(r).encode())

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
        cur_address = self.address_string()
        state = self.cam_state[cur_address]
        # FIXME implement init (when camera is idle and asking for a task)
        if state == 'idle':
            # initialize the camera
            return {'task': 'init',
                    'kwargs': {}
                    }
        elif state == 'ready':
            self.activate_camera()

        #
        # , if they all are ready, then set a time and start
        elif state == 'capture':
            # camera is already capturing, so just wait for further instructions (stop)
            return {'task': 'wait',
                    'kwargs': {}
                    }

    def post_log(self, log):
        """
        Log message from current camera on logger
        :return:
        dict {'success': False or True}
        """
        try:
            cur_address = self.address_string()
            log_msg = f'Cam {self.address_string()} - {log}'
            self.logger.info(log_msg)
            return {'success': True}
        except:
            return {'success': False}

    def activate_camera(self):
        # check how many cams have the state 'ready'
        n_cams_ready = np.sum([self.cam_state[s] == 'ready' for s in self.cam_state])
        if n_cams_ready == self.n_cams:
            return self.activate_camera()
            if self.start_time is None:
                # no start time has been set yet, ready to start the time
                self.logger.info('All cameras are ready, setting start time')
                self.start_time = 5 * round((time.time() + 10) / 5)
                self.start_datetime = datetime.datetime.fromtimestamp(self.start_time)
                self.logger.info(f'start time is set to {self.start_datetime}')
                self.logger.info(f'Sending capture command to {cur_address}')
            return {'task': 'capture_continuous',
                    'kwargs': {}
                    }
        else:
            return {'task': 'wait',
                    'kwargs': {}
                    }
        # TODO check wait
        # TODO check capture_continuous
