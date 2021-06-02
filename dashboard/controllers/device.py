from flask import Blueprint, jsonify, request, current_app
from jsonschema import validate, ValidationError
from models import db
from models.device import Device, DeviceType
from models.photo import Photo
from controllers import tasks

device_api = Blueprint("device_api", __name__)

task_schema = {
    "type": "object",
    "required": ["device_type", "request_time", "status"],
    "properties": {
        "device_type": {"type": "string"},
        "request_time": {"type": "string"},
        "status": {"type": "string"},
    }
}

log_schema = {
    "type": "object",
    "required": [],
    "properties": {
        "project_id": {"type": "integer"},
        "survey_id": {"type": "integer"},
        "file": {"type": "string"},
        "timestamp": {"type": "string"},
    }
}

@device_api.route("/api/task_request/<hostname>", methods=["POST"])
def task_request(hostname):
    """
    API endpoint for task request from child

    :param id: hostname of child
    :return:
    """
    content = request.get_json(silent=True)
    validate(instance=content, schema=task_schema)
    content["hostname"] = hostname  # add the host to the content
    # replace string of DeviceStatus for type

    child = Device.query.filter(Device.hostname == hostname).first()
    if child is None:
        # device hasn't been online yet, add to database
        child = Device(**content)
        db.add(child)
    else:
        # update status
        child.status = content["status"]
    db.commit()
    # request a task
    parent = Device.query.filter(Device.device_type == DeviceType.PARENT).first()  # retrieve parent
    # construct task name from status differences
    if child.status != parent.status:
        task_name = f"task_{child.status.name}_to_{parent.status.name}".lower()
        if not (hasattr(tasks, task_name)):
            return f"task {task_name} not available", 400
        task = getattr(tasks, task_name)
        # execute task
        return task()
    # if the status of child is the same as parent, then just wait
    return {"task": "wait", "kwargs": {}}, 200

@device_api.route("/api/child_log/<hostname>", methods=["POST"])
def child_log(hostname):
    """
    API endpoint to post a log message of child to the parent device

    :param id: hostname of child
    """
    current_app.logger.info(f"Receiving new photo details from {hostname}")
    content = request.get_json(silent=True)
    validate(instance=content, schema=log_schema)
    # deserialize components, and make data model complete
    content["hostname"] = hostname
    photo = Photo(**content)
    db.add(photo)
    db.commit()
    return "Success", 200

@device_api.errorhandler(ValidationError)
@device_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for child API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for child", "message": str(e)}), 400
