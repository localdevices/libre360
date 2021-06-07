from models.project import Project
from views.general import UserModelView


class ProjectView(UserModelView):
    can_edit = False
    column_list = (
        Project.id,
        Project.name,
        Project.n_cams,
        Project.dt,
        Project.status,
    )

    column_labels = {
        "name": "Name",
        "n_cams": "Number of cameras [-]",
        "dt": "Time interval [s]",
    }

    column_descriptions = {
        "name": "Your name for the project",
        "n_cams": "Amount of cameras available",
        "dt": "Time interval between photos in whole seconds",
    }
    form_columns = (
        Project.name,
        Project.n_cams,
        Project.dt,
    )
    # if you want to edit project list, create, update, or detail view, specify adapted templates below.
    list_template = "project/list.html"
    #create_template = "project/create.html"
    #edit_template = "project/edit.html"
    #details_template = "project/details.html"
