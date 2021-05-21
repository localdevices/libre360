from flask import Flask, redirect, jsonify, url_for
from flask_admin import helpers as admin_helpers
from flask_security import Security, login_required, SQLAlchemySessionUserDatastore
from werkzeug import serving
import re
from models import db
from models.user import User, Role
from controllers import device_api
from controllers import data_api
from controllers import dashboard_api
from views import admin

def log_request(self, *args, **kwargs):
    if not self.path in disabled_endpoints:
        parent_log_request(self, *args, **kwargs)

# Create flask app
app = Flask(__name__, template_folder="templates")
app.register_blueprint(device_api)
app.register_blueprint(data_api)
app.register_blueprint(dashboard_api)

app.debug = True
app.config["SECRET_KEY"] = "super-secret"
app.config["SECURITY_REGISTERABLE"] = True
app.config["SECURITY_SEND_REGISTER_EMAIL"] = False
app.config["SECURITY_PASSWORD_SALT"] = "salt"

# Setup Flask-Security
user_datastore = SQLAlchemySessionUserDatastore(db, User, Role)
security = Security(app, user_datastore)

#Disable logs for requests to specific endpoints
disabled_endpoints = ['/api/get_status']

parent_log_request = serving.WSGIRequestHandler.log_request
serving.WSGIRequestHandler.log_request = log_request
# Alternative routes


@app.route("/")
def index():
    return redirect("/dashboard", code=302)


# Create admin interface
admin.init_app(app)

# Provide necessary vars to flask-admin views.
@security.context_processor
def security_context_processor():
    return dict(
        admin_base_template=admin.base_template,
        admin_view=admin.index_view,
        h=admin_helpers,
        get_url=url_for,
    )


# Resolve database session issues for the combination of Postgres/Sqlalchemy scoped session/Flask-admin.
@app.teardown_appcontext
def shutdown_session(exception=None):
    # load all expired attributes for the given instance
    db.expire_all()


if __name__ == "__main__":

    # Start app
    app.run()
