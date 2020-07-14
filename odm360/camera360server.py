from http.server import BaseHTTPRequestHandler
import json
import cgi
import logging
import numpy as np
import time
import datetime

# adapted from https://gist.github.com/nitaku/10d0662536f37a087e1b
def make_Camera360Server(parent):
    class Camera360Server(BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.parent = parent
            super(Camera360Server, self).__init__(*args, **kwargs)

        def log_message(self, format, *args):
            return

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
            self.parent.cam_state[self.address_string()] = msg['state']
            log_msg = f'Cam {self.address_string()} - GET {msg["req"]}'
            self.parent.logger.debug(log_msg)
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
            self.parent.logger.debug(log_msg)

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
            self.parent.logger.info(f'Giving root {self.parent.root} to Cam {self.address_string()}')
            return {'root': self.parent.root}

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
            # TODO replace by push button, now stopping after 30 secs
            if self.parent.start_time is not None:
                if time.time() > self.parent.start_time + 10:
                    print(time.time(), self.parent.start_time)
                    self.parent.stop = True
            cur_address = self.address_string()
            state = self.parent.cam_state[cur_address]
            if state == 'idle':
                # initialize the camera
                self.parent.logger.info('Sending camera initialization ')
                return {'task': 'init',
                        'kwargs': {}
                        }
            elif state == 'ready':
                if not(self.parent.stop):
                    return self.activate_camera()

            elif state == 'capture':
                if self.parent.stop:
                    return {'task': 'stop',
                            'kwargs': {}
                            }
                # camera is already capturing, so just wait for further instructions (stop)
            return {'task': 'wait',
                    'kwargs': {}
                    }

        def post_log(self, msg):
            """
            Log message from current camera on logger
            :return:
            dict {'success': False or True}
            """
            try:
                cur_address = self.address_string()
                log_msg = f'Cam {self.address_string()} - {msg["msg"]}'
                log_method = getattr(self.parent.logger, msg['level'])
                log_method(log_msg)
                return {'success': True}
            except:
                return {'success': False}

        def activate_camera(self):
            cur_address = self.address_string()
            # check how many cams have the state 'ready', only start when the full rig is ready
            n_cams_ready = np.sum([self.parent.cam_state[s] == 'ready' for s in self.parent.cam_state])
            if n_cams_ready == self.parent.n_cams:
                self.parent.logger.info(f'All cameras ready. Start capturing on {cur_address}')
                # no start time has been set yet, ready to start the time
                self.parent.logger.debug('All cameras are ready, setting start time')
                self.parent.start_time = 5 * round((time.time() + 10) / 5)
                self.parent.start_datetime = datetime.datetime.fromtimestamp(self.parent.start_time)
                self.parent.logger.debug(f'start time is set to {self.parent.start_datetime}')
                self.parent.logger.info(f'Sending capture command to {cur_address}')
                return {'task': 'capture_continuous',
                        'kwargs': {'start_time': self.parent.start_time}
                        }
            else:
                self.parent.logger.debug(f'Only {n_cams_ready} out of {self.parent.n_cams} ready for capture, waiting...')
                return {'task': 'wait',
                        'kwargs': {}
                        }
            # TODO check wait
            # TODO check capture_continuous
    return Camera360Server