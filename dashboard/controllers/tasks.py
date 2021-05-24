import time
import datetime
import pytz

from models import db
from models.project import Project, ProjectStatus
from models.device import Device, DeviceStatus, DeviceType
from models.survey import Survey

# tasks are named along the idea that a child should take the status of parent, naming convention as follows:
# task_{child.status}_to_{parent.status}

def task_idle_to_ready():
    return {"task": "init", "kwargs": {}}, 200

def task_capture_to_ready():
    return {"task": "stop", "kwargs": {}}, 200

def task_stream_to_ready():
    return {"task": "stop_stream", "kwargs": {}}, 200

def task_ready_to_capture():
    # retrieve which project is active (if None then tell the child to stay ready
    project = Project.query.filter(Project.status == ProjectStatus.ACTIVE).first()  # retrieve parent
    if project is None:
        return {"task": "wait", "kwargs": {}}, 200
    else:
        # dt = int(project["dt"])
        # cur_address = request.remote_addr
        # check how many cams have the state 'ready', only start when the full rig is ready
        devices_ready = Device.query.filter(Device.device_type == DeviceType.CHILD).filter(Device.status ==
                                            DeviceStatus.READY).all()
        if len(devices_ready) == project.n_cams:
            # ready to go, collect info and send the device the go-ahead
            start_time_epoch = project.dt * round(
                (time.time() + 10) / project.dt
            )  # this number is send to the child to start capturing
            start_datetime = datetime.datetime.fromtimestamp(start_time_epoch)
            dt_local = start_datetime.astimezone()
            start_datetime_utc = dt_local.astimezone(pytz.utc)
            survey = {
                "project_id": project.id,
                "timestamp": start_datetime_utc,
                }
            # set start time for capturing, and set state to capture
            new_survey = Survey(**survey)
            db.add(new_survey)
            db.commit()
            return {
                "task": "capture_continuous",
                "kwargs": new_survey.to_dict()
            }, 200
        else:
            # this should not happen as the front end part already checks if enough cams are online.
            parent = Device.query.filter(Device.device_type == DeviceType.PARENT).first()
            parent.status = DeviceStatus.READY
            db.commit()
            return f"Only {len(devices_ready)} out of {project.n_cams} ready for capture, " \
                                                                                  "switching state back", 405

def task_ready_to_stream():
    # retrieve which project is active (if None then tell the child to stay ready
    project = Project.query.filter(Project.status == ProjectStatus.ACTIVE).first()  # retrieve parent
    if project is not None:
        # check how many cams have the state 'ready', only start when the full rig is ready
        devices_ready = Device.query.filter(Device.device_type == DeviceType.CHILD).filter(Device.status ==
                                            DeviceStatus.READY).all()
        if len(devices_ready) == project.n_cams:
            # set state to stream
            return {
                "task": "capture_stream",
                "kwargs": {},
            }
        else:
            # this should not happen as the front end part already checks if enough cams are online.
            return f"Only {len(devices_ready)} out of {project.n_cams} ready for capture, " \
                                                                                      "switching state back", 405
            # roll back to state "ready"
            parent = Device.query.filter(Device.device_type == DeviceType.PARENT).first()
            parent.status = DeviceStatus.READY
            db.commit()
    return {"task": "wait", "kwargs": {}}, 200

