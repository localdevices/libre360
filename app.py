# Server is setup here
from flask import Flask, render_template, redirect, request, jsonify, make_response, Response
from flask_bootstrap import Bootstrap
import psycopg2

from odm360.log import start_logger, stream_logger
from odm360.camera360rig import do_request
from odm360 import dbase
from odm360.states import states
from odm360.utils import cleanopts

db = 'dbname=odm360 user=odm360 host=localhost password=zanzibar'
conn = psycopg2.connect(db)
cur = conn.cursor()

#make sure devices is empty
dbase.truncate_table(cur, 'devices')

logger = start_logger("True", "False")

# if there is an active project, put status on zero (waiting for cams) at the beginning no matter what
cur_project = dbase.query_project_active(cur)
if len(cur_project) == 1:
    dbase.update_project_active(cur, states['ready'])

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route("/", methods=['GET', 'POST'])
def gps_page():
    if request.method == "POST":
        raw_form = request.form
        form = cleanopts(raw_form)
        if 'project' in form:
            logger.info(f"Changing to project {form['project']}")
            # first drop the current active project table and create a new one
            dbase.truncate_table(cur, 'project_active')
            # insert new active project
            dbase.insert_project_active(cur, int(form['project']))
            cur_project = dbase.query_projects(cur, project_id=int(form['project']), as_dict=True, flatten=True)
            logger.info(f"Successfully changed to project - name: {cur_project['project_name']} cams: {int(cur_project['n_cams'])} interval: {int(cur_project['dt'])} secs.'")
        elif 'service' in form:
            if form["service"] == "on":
                logger.info("Starting service")
                dbase.update_project_active(cur, states['capture'])
        elif len(form) == 0:
            print(f'RAW FORM: {raw_form}')
            print(f'FORM: {form}')
            # TODO: bug in code. When switch is turned off, the form returns empty dictionary.
            logger.info("Stopping service")
            dbase.update_project_active(cur, states['ready'])  # status 1 means auto_start cameras once they are all online

    # FIXME: replace by checking for projects in database
    # first check what projects already exist and list those in the status page as selectors
    projects = dbase.query_projects(cur)
    project_ids = [p[0] for p in projects]
    project_names = [p[1] for p in projects]
    projects = zip(project_ids, project_names)
    cur_project = dbase.query_project_active(cur)
    devices_ready = dbase.query_devices(cur, status=states['ready'])
    devices_total = dbase.query_devices(cur)

    if len(cur_project) == 0:
        cur_project_id = None
        service_active = 0
        dbase.update_project_active(cur, status=states['idle'])
    else:
        cur_project_id = cur_project[0][0]
        service_active = cur_project[0][1]
        if service_active != states['capture']:
            # apparently there is a project, but not activated to capture yet. So set on 'ready' instead
            dbase.update_project_active(cur, status=states['ready'])
    return render_template("status.html",
                           projects=projects,
                           cur_project_id=cur_project_id,
                           service_active=service_active,
                           devices_total=len(devices_total),
                           devices_ready=len(devices_ready)
                           )  #

@app.route('/project', methods=['GET', 'POST'])
def project_page():
    """
        The settings page where you can manage the various services, the parameters, update, power...
    """
    if request.method == 'POST':
        # config = current_app.config['config']
        # FIXME: put inputs into the database and remove config stuff below
        form = cleanopts(request.form)
        # set the config options as provided

        dbase.insert_project(cur, form['project_name'], n_cams=int(form['n_cams']), dt=int(form['dt']))
        # remove the current project selection and make a fresh table
        dbase.create_table_project_active(cur, drop=True)
        # set project to current by retrieving its id and inserting that in current project table
        project_id = dbase.query_projects(cur, project_name=form['project_name'])[0][0]
        dbase.insert_project_active(cur, project_id=project_id)
        logger.info(f'Created a new project name: "{form["project_name"]}" cams: {form["n_cams"]} interval: {int(form["dt"])} secs.')
        return redirect("/")
    else:
        return render_template("project.html")

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
    # from example https://stackoverflow.com/questions/24735810/python-flask-get-json-data-to-display
    return render_template("cam_status.html")


@app.route('/file_page')
def file_page():
    return render_template("file_page.html")


@app.route("/log_stream", methods=["GET"])
def stream():
    """returns logging information"""
    # largely taken from https://towardsdatascience.com/how-to-add-on-screen-logging-to-your-flask-application-and-deploy-it-on-aws-elastic-beanstalk-aa55907730f
    return Response(stream_logger(), mimetype="text/plain", content_type="text/event-stream")


@app.route('/_cameras')
def cameras():
    # FIXME get the actual database status
    cur_project = dbase.query_project_active(cur)
    project = dbase.query_projects(cur, project_id=cur_project[0][0], as_dict=True, flatten=True)
    devices = dbase.make_dict_devices(cur)
    n_online = len(devices)
    # add offline devices
    n_offline = int(project['n_cams']) - n_online
    for n in range(n_offline):
        devices.append({'device_no': f'camera{n + n_online}',
                        'device_uuid': 'uknown',
                        'device_name': 'unknown',
                        'status': 'offline',
                        'last_photo': None,
                        }
                       )

    return jsonify(devices) #, mimetype='application/json') #mimetype="text/plain", content_type="text/event-stream")



@app.route('/picam', methods = ['GET', 'POST'])
def picam():
    if request.method == 'POST':

        r, status_code = do_request(cur, method='POST')
        return make_response(jsonify(r), status_code)

    elif request.method == 'GET':
        r, status_code = do_request(cur, method='GET')  # response is passed back to client
        return make_response(jsonify(r), status_code)


def run(app):
    app.run(debug=False, port=5000, host="0.0.0.0")

if __name__ == "__main__":
    run(app)
