import flask_admin as admin


class MapView(admin.BaseView):
    @admin.expose("/")
    def index(self):
        return self.render("map.html")
