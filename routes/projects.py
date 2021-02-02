from app import app
from flask import request, redirect, render_template
from odm360 import dbase
from odm360.utils import cleanopts
import psycopg2

logger = app.logger
db = "dbname=odm360 user=odm360 host=localhost password=zanzibar"
conn = psycopg2.connect(db)


@app.route("/project", methods=["GET", "POST"])
def project_page():
    """
        The settings page where you can manage the various services, the parameters, update, power...
    """
    with conn.cursor() as cur_project:
        if request.method == "POST":
            # config = current_app.config['config']
            form = cleanopts(request.form)
            # set the config options as provided
            dbase.insert_project(
                cur_project,
                form["project_name"],
                n_cams=int(form["n_cams"]),
                dt=int(form["dt"]),
            )
            dbase.truncate_table(cur_project, "project_active")
            # set project to current by retrieving its id and inserting that in current project table
            project_id = dbase.query_projects(
                cur_project, project_name=form["project_name"]
            )[0][0]
            dbase.insert_project_active(cur_project, project_id=project_id)
            logger.info(
                f'Created a new project name: "{form["project_name"]}" cams: {form["n_cams"]} interval: {int(form["dt"])} secs.'
            )
            return redirect("/")
        else:
            return render_template("project.html")
