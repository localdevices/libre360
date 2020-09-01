# Server is setup here
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap
from odm360.workflows import parent_server
from odm360.utils import parse_config
from odm360.log import start_logger

# start with a parent server immediately. Make a new one when a new project is initiated
default_config_fn = 'config/settings.conf.default'
config = parse_config(default_config_fn)
logger = start_logger(config.get('main', 'verbose'), config.get('main', 'quiet'))
logger.info(f'Parsing project config from ...') # TODO read last config option, if not available start fresh

# TODO introduce checks to see if the information is complete enough to already start up a workflow
kwargs = {
    'project': config.get('main', 'project'),
    'n_cams': int(config.get('main', 'n_cams')),
    'dt': int(config.get('main', 'dt')),
    'root': config.get('main', 'root'),
    'logger': logger,
    'debug': config.get('main', 'verbose'),
    'auto_start': True
}

# TODO prepare a daemon object that runs parent_server until it is killed

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route("/")
def gps_page():
    """
        The status web page with the gnss satellites levels and a map
    """
    return render_template("status.html")

# def home():
#     return render_template("index.html.j2")

@app.route('/settings')
def settings_page():
    """
        The settings page where you can manage the various services, the parameters, update, power...
    """
    # main_settings = rtkbaseconfig.get_main_settings()
    # ntrip_settings = rtkbaseconfig.get_ntrip_settings()
    # file_settings = rtkbaseconfig.get_file_settings()
    # rtcm_svr_settings = rtkbaseconfig.get_rtcm_svr_settings()

    return render_template("settings.html") #, main_settings = main_settings,
                                            # ntrip_settings = ntrip_settings,
                                            # file_settings = file_settings,
                                            # rtcm_svr_settings = rtcm_svr_settings)

@app.route('/logs')
def logs_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template("logs.html")

@app.route('/cams')
def cam_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template("cam_status.html")

def run():
    app.run(debug=True, port=5001, host="0.0.0.0")

if __name__ == "__main__":
    run()