# Server is setup here
from flask import Flask, session, render_template, request, jsonify
from flask_bootstrap import Bootstrap
from flask_session import Session
import time, os

from odm360.utils import parse_config
from odm360.log import start_logger
from odm360.camera360rig import CameraRig
from odm360.utils import get_lan_ip

# API for picam is defined below
def do_GET():
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
    global rig
    try:
        msg = request.get_json()
        print(msg)
        # Create or update state of current camera
        session['rig'].cam_state[request.remote_addr] = msg['state']
        log_msg = f'Cam {request.remote_addr} - GET {msg["req"]}'
        logger.debug(log_msg)
        # check if task exists and sent instructions back
        method = f'get_{msg["req"].lower()}'
        # if hasattr(self, method):
        if 'kwargs' in msg:
            kwargs = msg['kwargs']
        else:
            kwargs = {}
        task = getattr(session['rig'], method)
        # execute with key-word arguments provided
        r = task(**kwargs)
        return r
    except:
        return {'task': 'wait',
                'kwargs': {}
                }

# POST echoes the message adding a JSON field
def do_POST():
    """
    POST API should provide a json with the following fields:
    req: str - name of method for posting to call from server (e.g. log)
    kwargs: dict - any kwargs that need to be parsed to method (can be left out if None)
    the POST API then decides what action should be taken based on the POST request.
    POST API will also return a result back
    """
    msg = request.get_json()
    print(msg)
    # show request in log
    log_msg = f'Cam {request.remote_addr} - POST {msg["req"]}'

    session['rig'].logger.debug(log_msg)

    # check if task exists and sent instructions back
    method = f'post_{msg["req"].lower()}'
    if hasattr(session['rig'], method):
        if 'kwargs' in msg:
            kwargs = msg['kwargs']
        else:
            kwargs = {}
        task = getattr(session['rig'], method)
        # execute with key-word arguments provided
        r = task(**kwargs)
        return r

def cleanopts(optsin):
    """Takes a multidict from a flask form, returns cleaned dict of options"""
    opts = {}
    d = optsin
    for key in d:
        opts[key] = optsin[key].lower().replace(' ', '_')
    return opts

app = Flask(__name__)
app.secret_key = 'odm360'
bootstrap = Bootstrap(app)

logger = start_logger("True", "False")


@app.route("/")
def gps_page():
    # start with a parent server immediately. Make a new one when a new project is initiated
    # TODO: only do this if there is no rig initialized yet.
    if os.path.isfile('current_config'):
        with open('current_config', 'r') as f:
            config_fn = os.path.join('config', f.read())
    else:
        config_fn = 'config/settings.conf.default'
    logger.info(f'Parsing project config from {os.path.abspath(config_fn)}')
    config = parse_config(config_fn)

    # test if we are ready to start devices or not
    start_parent = True
    if config.get('main', 'n_cams') == '':
        start_parent = False
        logger.info('n_cams is missing in config, starting without a running parent server')
    if config.get('main', 'dt') == '':
        start_parent = False
        logger.info('dt is missing in config, starting without a running parent server')
    if config.get('main', 'project') == '':
        start_parent = False
        logger.info('project is missing in config, starting without a running parent server')
    if config.get('main', 'root') == '':
        start_parent = False
        logger.info('root is missing in config, starting without a running parent server')
    session['config'] = config
    session['ip'] = get_lan_ip()

    if start_parent:
        logger.info('Starting parent server')
        kwargs = {
            'ip': session['ip'],
            'project': config.get('main', 'project'),
            'root': config.get('main', 'root'),
            'n_cams': int(config.get('main', 'n_cams')),
            'dt': int(config.get('main', 'dt')),
            'logger': logger,
            'auto_start': False
        }
        # start a rig server object with the current settings
        # find own ip address
        # setup server
        session['rig'] = CameraRig(**kwargs)
        print('Server started')
    else:
        session['rig'] = None
    """
        The status web page with the gnss satellites levels and a map
    """
    return render_template("status.html")

# def home():
#     return render_template("index.html.j2")

@app.route('/project', methods=['GET', 'POST'])
def project_page():
    """
        The settings page where you can manage the various services, the parameters, update, power...
    """
    # main_settings = rtkbaseconfig.get_main_settings()
    # ntrip_settings = rtkbaseconfig.get_ntrip_settings()
    # file_settings = rtkbaseconfig.get_file_settings()
    # rtcm_svr_settings = rtkbaseconfig.get_rtcm_svr_settings()
    if request.method == 'POST':
        config = session['config']
        form = cleanopts(request.form)
        # set the config options as provided
        config.set('main', 'project', form['project'])
        config.set('main', 'n_cams', form['n_cams'])
        config.set('main', 'dt', form['dt'])
        config.set('main', 'root', os.path.join('photos', form['project']))
        config.set('main', 'verbose', "True" if form['loglevel']=='debug' else "False")
        config.set('main', 'quiet', "False")
        config_fn = f'{form["project"]}.ini'
        with open(os.path.abspath(os.path.join('config', config_fn)), 'w') as f:
            config.write(f)
        with open('current_config', 'w') as f:
            f.write(config_fn)
        # store current project to cur_settings file
        # make new rig object
        kwargs = {
            'ip': session['ip'],
            'project': config.get('main', 'project'),
            'root': config.get('main', 'root'),
            'n_cams': int(config.get('main', 'n_cams')),
            'dt': int(config.get('main', 'dt')),
            'logger': logger,
            'auto_start': False
        }
        session['config'] = config
        session['rig'] = CameraRig(**kwargs)
        print('stop here')


        return render_template("status.html") #, main_settings = main_settings,
                                                # ntrip_settings = ntrip_settings,
                                                # file_settings = file_settings,
                                                # rtcm_svr_settings = rtcm_svr_settings)

    else:
        return render_template("project.html") #, main_settings = main_settings,
                                                # ntrip_settings = ntrip_settings,
                                                # file_settings = file_settings,
                                                # rtcm_svr_settings = rtcm_svr_settings)

@app.route('/logs')
def logs_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template("logs.html")

@app.route('/settings')
def settings_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template("settings.html")

@app.route('/cams')
def cam_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template("cam_status.html", n_cams=range(6))

@app.route('/file_page')
def file_page():
    return render_template("file_page.html")

@app.route('/picam', methods=['GET', 'POST'])
def picam():
    if request.method == 'POST':

        r = do_POST()
    else:
        # print(request.get_json())
        r = do_GET()  # response is passed back to client
    return jsonify(r)

def run(app):
    app.run(debug=False, port=5000, host="0.0.0.0")

if __name__ == "__main__":
    run(app)