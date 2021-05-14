import flask_admin as admin
from flask_admin.menu import MenuLink
from flask_security import current_user
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for


class LoginMenuLink(MenuLink):
    def is_accessible(self):
        return not current_user.is_authenticated


class LogoutMenuLink(MenuLink):
    def is_accessible(self):
        return current_user.is_authenticated


class UserModelView(ModelView):
    can_view_details = True

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for("security.login"))


# Extend this view class for views which should only be available for logged in users.
class UserView(admin.BaseView):
    def can_view_details(self):
        return True

    def is_accessible(self):
        return current_user.is_active and current_user.is_authenticated

    def _handle_view(self, name):
        if not self.is_accessible():
            return redirect(url_for("security.login"))
