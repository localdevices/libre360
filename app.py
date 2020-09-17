# Server is setup here
from flask import Flask, session, render_template, request, jsonify, current_app
from flask_bootstrap import Bootstrap
import time, os
import psycopg2

from odm360.utils import parse_config, make_config
from odm360.log import start_logger
import odm360.camera360rig as camrig
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
    try:
        # TODO: pass full project details from dbase to child
        msg = request.get_json()
        print(msg)
        # Create or update state of current camera
        current_app.config['rig'].cam_state[request.remote_addr] = msg['state']
        log_msg = f'Cam {request.remote_addr} - GET {msg["req"]}'
        logger.debug(log_msg)
        # check if task exists and sent instructions back
        method = f'get_{msg["req"].lower()}'
        # if hasattr(self, method):
        if 'kwargs' in msg:
            kwargs = msg['kwargs']
        else:
            kwargs = {}
        task = getattr(current_app.config['rig'], method)
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

    logger.debug(log_msg)

    # check if task exists and sent instructions back
    method = f'post_{msg["req"].lower()}'
    if hasattr(current_app.config['rig'], method):
        if 'kwargs' in msg:
            kwargs = msg['kwargs']
        else:
            kwargs = {}
        task = getattr(current_app.config['rig'], method)
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

# TODO: remove when database connection is function
def initialize_config(config_fn):
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
    current_app.config['config'] = dict(config.items('main'))
    current_app.config['ip'] = get_lan_ip()
    current_app.config['start_parent'] = start_parent

db = 'dbname=odm360 user=odm360 host=localhost password=zanzibar'
conn = psycopg2.connect(db)
cur = conn.cursor()

app = Flask(__name__)
bootstrap = Bootstrap(app)

logger = start_logger("True", "False")

@app.route("/")
def gps_page():
    # TODO: only do this if there is no rig initialized yet.
    # FIXME: replace by checking for projects in database
    if not('config' in current_app.config):
        if os.path.isfile('current_config'):
            with open('current_config', 'r') as f:
                config_fn = os.path.join('config', f.read())
        else:
            config_fn = 'config/settings.conf.default'
        logger.info(f'Parsing project config from {os.path.abspath(config_fn)}')
        initialize_config(config_fn)
    if current_app.config['start_parent']:
        logger.info('Starting parent server')
        camrig.start_rig()

    """
        The status web page with the gnss satellites levels and a map
    """
    return render_template("status.html")

@app.route('/project', methods=['GET', 'POST'])
def project_page():
    """
        The settings page where you can manage the various services, the parameters, update, power...
    """
    if request.method == 'POST':
        # config = current_app.config['config']
        # FIXME: put inputs into the database and remove config stuff below
        form = cleanopts(request.form)
        config = {}
        # set the config options as provided
        config['project'] = form['project']
        config['n_cams'] = form['n_cams']
        config['dt'] = form['dt']
        config['root'] = os.path.join('photos', form['project'])
        config['verbose'] = "True" if form['loglevel']=='debug' else "False"
        config['quiet'] = "False"
        config_fn = f'{form["project"]}.ini'
        conf_obj = make_config(config)
        with open(os.path.abspath(os.path.join('config', config_fn)), 'w') as f:
            conf_obj.write(f)
        with open('current_config', 'w') as f:      
            f.write(config_fn)
        initialize_config(os.path.join('config', config_fn))
        # start the rig, after this, the rig is in current_app.config['rig'], if start_parent is true
        if current_app.config['start_parent']:
            camrig.start_rig()

        return render_template("status.html")   #, main_settings = main_settings,
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

if __name__ == "__main__":
    app.run(host="0.0.0.0")
