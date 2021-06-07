import flask_admin as admin

# Models for CRUD views.
from models import db
from models.project import Project
from models.survey import Survey
from models.device import Device
from models.photo import Photo
from views.general import LogoutMenuLink, LoginMenuLink, UserModelView
from views.help import HelpView
from views.map import MapView
from views.project import ProjectView
from views.survey import SurveyView
from views.device import DeviceView

admin = admin.Admin(name="Libre360", template_mode="bootstrap4", url="/dashboard", base_template="base.html")

# Login/logout menu links.
admin.add_link(LogoutMenuLink(name="Logout", category="", url="/logout"))
admin.add_link(LoginMenuLink(name="Login", category="", url="/login"))

# Publicly visible pages.
admin.add_view(HelpView(name="Help", url="help"))
admin.add_view(MapView(name="Map", url="map"))


admin.add_view(ProjectView(Project, db, name="Projects", url="projects", category="Setup"))

admin.add_view(SurveyView(Survey, db, name="Surveys", url="surveys", category="Setup"))
admin.add_view(DeviceView(Device, db, name="Status", url="device"))