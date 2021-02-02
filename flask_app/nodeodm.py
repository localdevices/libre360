from app import app
from flask import render_template
import os


@app.route("/nodeodm")
def nodeodm_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template(
        "nodeodm.html",
        logo="./static/images/logo.png"
        if os.path.isfile("./static/images/logo.png")
        else "",
    )
