from app import app, conn
from flask import request, render_template, jsonify, Response, make_response
from odm360 import dbase
from odm360.utils import cleanopts, create_geo_txt
import zipstream
import json
import numpy as np

logger = app.logger


@app.route("/file_page")  # , methods=["GET", "POST"])
def file_page():
    with conn.cursor() as cur_files:
        projects = dbase.query_projects(cur_files)
        project_ids = [p[0] for p in projects]
        project_names = [p[1] for p in projects]
        projects = zip(project_ids, project_names)
        return render_template("file_page.html", projects=projects)


@app.route("/_files", methods=["GET", "POST"])
def _files():
    try:
        args = cleanopts(request.args)
        with conn.cursor() as cur_files:
            # first query the relevant project
            project = dbase.query_projects(
                cur_files, project_id=args["project_id"], as_dict=True, flatten=True
            )
            # check what the survey_run id is
            if args["survey_run"] == "all":
                survey_run = None
            else:
                survey_run = args["survey_run"].upper()
            fns = dbase.query_photo_names(
                cur_files, project_id=project["project_id"], survey_run=survey_run
            )
        return jsonify(fns)
    except BaseException as e:
        logger.error(f"{_files} failed with error {e}")


@app.route("/_surveys", methods=["GET", "POST"])
def _surveys():
    args = cleanopts(request.args)
    with conn.cursor() as cur_surveys:
        # first query the relevant project
        project = dbase.query_projects(
            cur_surveys, project_id=args["project_id"], as_dict=True, flatten=True
        )
        surveys = dbase.query_surveys(
            cur_surveys, project_id=project["project_id"], as_dict=True
        )
    return jsonify(surveys)


@app.route("/odm360.zip", methods=["GET"], endpoint="_download")
def _download():
    """
    # download works with a streeaming zip archive: all files listed are queued first, and then streamed to a end-user
    # zip file
    """

    def generator(cur, fns):
        """
        generator for zip archive
        :param cur: cursor for retrieval of individual files
        :return: chunk (i.e. one photo) for zip stream
        """
        z = zipstream.ZipFile(
            mode="w", compression=zipstream.ZIP_DEFLATED, allowZip64=True
        )
        # first make a geo.txt file
        geo = create_geo_txt(fns)
        z.writestr("geo.txt", geo.encode())
        for fn in fns:
            z.write_iter(
                fn["photo_filename"],
                dbase._generator(cur, fn["srvname"], fn["photo_uuid"]),
            )
        for chunk in z:
            yield chunk

    # retrieve arguments (stringified json)
    args = cleanopts(request.args)
    fns = json.loads(args["photos"])
    # build zipfile name
    if len(np.unique([fn["survey_run"] for fn in fns])) > 1:
        # apparently a full project is downloaded
        zip_fn = "{:03d}.zip".format(fns[0]["project_id"])
    else:
        zip_fn = "{:03d}_{:s}.zip".format(
            fns[0]["project_id"], fns[0]["survey_run"].upper()
        )
    # change filename so that ODM can handle them
    for n in range(len(fns)):
        fns[n]["photo_filename"] = fns[n]["photo_filename"].replace("/", "_")
    # open a dedicated connection for the download
    cur_download = conn.cursor()
    response = Response(generator(cur_download, fns), mimetype="application/zip")
    response.headers["Content-Disposition"] = "attachment; filename={}".format(zip_fn)
    return response


@app.route("/_delete", methods=["GET"])
def _delete():
    """
    delete selection
    """
    # retrieve arguments (stringified json)
    logger.info("Deleting file selection")
    args = cleanopts(request.args)
    fns = json.loads(args["photos"])
    # find unique projects
    project_ids = set([int(fn["project_id"]) for fn in fns])
    # find unique survey runs
    survey_runs = set([fn["survey_run"].upper() for fn in fns])
    # find unique servers
    srvnames = set([fn["srvname"] for fn in fns])

    # open a dedicated connection for the download
    cur_delete = conn.cursor()
    for survey_run in survey_runs:
        # check if there are still photos, if not delete the survey_run
        fns = dbase.query_photo_names(cur_delete, survey_run=survey_run)
        # deletion sometimes doesn't fully work with remote tables, so we repeat this until no files are found
        while len(fns) > 0:
            for srvname in srvnames:
                dbase.delete_photos(
                    cur_delete, srvname, survey_run
                )  # conversion to upper case needed after json-text conversion
                fns = dbase.query_photo_names(cur_delete, survey_run=survey_run)
        # TODO: delete selection return positive response.
        fns = dbase.query_photo_names(cur_delete, survey_run=survey_run)
        if len(fns) == 0:
            # apparently all photos are successfully deleted, so remove the survey run from the table
            dbase.delete_survey(cur_delete, survey_run=survey_run)
    # finally check over the entire project if there are files left. If not, delete the project!
    for project_id in project_ids:
        fns = dbase.query_photo_names(cur_delete, project_id=project_id)
        if len(fns) == 0:
            dbase.delete_project(cur_delete, project_id=project_id)

    logger.info("Delete is done")
    return make_response(jsonify("Files successfully deleted", 200))
