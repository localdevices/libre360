from flask import Blueprint, jsonify, request, flash, url_for, redirect
from jsonschema import validate, ValidationError
from models import db
from models.device import Device, DeviceStatus

device_api = Blueprint("device_api", __name__)

# functionality to select and return tasks
def get_task(cur, state):
    """
    Choose a task for the child to perform, and return this
    Currently implemented are:
        init: - initialize camera (done when status of camera is 'idle')
        wait: - tell camera to simply wait and send a request for a task later (typically done when not all cameras are online yet
        capture_until: - capture until a stop (not implemented yet) is given, using kwargs for time and time intervals
                         this is only provided when all cameras in the expected camera rig size are initialized
    :return:
    dict representation of task, including the following fields:
    task: str - name of task method to be performed on child side
    kwargs: dict - set of key word arguments and their values to provide to that task
    """
    rig = dbase.query_project_active(cur, as_dict=True)
    cur_device = dbase.query_devices(
        cur, device_uuid=state["device_uuid"], as_dict=True, flatten=True
    )
    # get states of parent and child in human readable format
    device_status = utils.get_key_state(cur_device["status"])
    if len(rig) > 0:
        rig_status = utils.get_key_state(rig["status"])
        if device_status != rig_status:
            # something needs to be done to get the states the same
            task_name = f"task_{device_status}_to_{rig_status}"
            if not (hasattr(camrig, task_name)):
                return f"task {task_name} not available"
            task = getattr(camrig, task_name)
            # execute task
            return task(cur, state)
            # camera is already capturing, so just wait for further instructions (stop)
    return {"task": "wait", "kwargs": {}}




# FIXME: make a schema format to check task request messages of child against, before processing
task_schema = {
    "type": "object",
    "required": ["device_type", "request_time", "status"],
    "properties": {
        "device_type": {"type": "string"},
        "request_time": {"type": "string"},
        "status": {"type": "string"},
    }
}

# FIXME: make a schema format to check log messages of child against, before processing
log_schema = {
}

@device_api.route("/api/task_request/<hostname>", methods=["POST"])
def task_request(hostname):
    """
    API endpoint for task request from child

    :param id: hostname of child
    :return:
    """
    content = request.get_json(silent=True)
    print(f"Content = {content}")
    validate(instance=content, schema=task_schema)
    content["hostname"] = hostname  # add the host to the content
    # content["status"] = DeviceStatus[content["status"]]
    # FIXME: implement task handling, which eventually should lead to return of task
    device = Device.query.filter(Device.hostname == hostname).first()
    if device is None:
        # device hasn't been online yet, add to database
        print(content)
        db.add(Device(**content))
    else:
        # update status
        device.status = content["status"]
    db.commit()
    # request a task

    # ....
    return "Success", 200
    # return jsonify(task.to_dict())

@device_api.route("/api/child_log/<id>", methods=["POST"])
def child_log(id):
    """
    API endpoint to post a log message of child to the parent device

    :param id: hostname of child
    """
    content = request.get_json(silent=True)
    print(f"Content = {content}")
    validate(instance=content, schema=log_schema)
    # parse content
    # FIXME: implement log message handling, eventually leading to a success/error msg for child
    # ...
    # return jsonify(bathymetry.to_dict())


@device_api.errorhandler(ValidationError)
@device_api.errorhandler(ValueError)
def handle(e):
    """
    Custom error handling for child API endpoints.

    :param e:
    :return:
    """
    return jsonify({"error": "Invalid input for child", "message": str(e)}), 400
