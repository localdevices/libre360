from app import app, conn
from flask import request, jsonify, make_response
from odm360.camera360rig import do_request


@app.route("/picam", methods=["GET", "POST"])
def picam():
    with conn.cursor() as cur_request:
        if request.method == "POST":

            r, status_code = do_request(cur_request, method="POST")
            return make_response(jsonify(r), status_code)

        elif request.method == "GET":
            r, status_code = do_request(
                cur_request, method="GET"
            )  # response is passed back to client
            # print(r, status_code)
            return make_response(jsonify(r), status_code)
