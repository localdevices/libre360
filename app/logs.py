from flask import render_template, Response
from odm360.log import stream_logger
import os
from app import app

@app.route("/logs")
def logs_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template(
        "logs.html",
        logo="./static/images/logo.png"
        if os.path.isfile("./static/images/logo.png")
        else "",
    )


@app.route("/log_stream", methods=["GET"])
def stream():
    """returns logging information"""
    # largely taken from https://towardsdatascience.com/how-to-add-on-screen-logging-to-your-flask-application-and-deploy-it-on-aws-elastic-beanstalk-aa55907730f
    return Response(
        stream_logger(), mimetype="text/plain", content_type="text/event-stream"
    )
