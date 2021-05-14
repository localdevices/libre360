import flask_admin as admin


class HelpView(admin.BaseView):
    @admin.expose("/")
    def index(self):
        return self.render("help/index.html")
