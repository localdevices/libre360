from models.device import Device
from views.general import UserModelView


class DeviceView(UserModelView):
    can_edit = False
    can_delete = False
    can_create = False
    column_list = (
        Device.id,
        Device.device_type,
        Device.hostname,
        Device.status,
    )

    column_labels = {
        "device_type": "Device type",
        "hostname": "Host name",
        "status": "Status",
    }

    column_descriptions = {
        "device_type": "Device can be a parent or child",
        "hostname": "Name of device as known on the network",
        "status": "Describes what the device is currently doing",
    }
    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    # list_template = "project/list.html"
    #create_template = "project/create.html"
    #edit_template = "project/edit.html"
    #details_template = "project/details.html"
