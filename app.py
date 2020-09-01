# Server is setup here
from flask import Flask, render_template, request
from flask_bootstrap import Bootstrap

app = Flask(__name__)
bootstrap = Bootstrap(app)

@app.route("/")
def status_page():
    """
        The status web page with the gnss satellites levels and a map
    """
    # base_position = rtkbaseconfig.get("main", "position").replace("'", "").split()
    # base_coordinates = {"lat" : base_position[0], "lon" : base_position[1]}
    base_coordinates = {"lat" : 52, "lon" : 4}
    return render_template("status.html", base_coordinates=base_coordinates, tms_key={"maptiler_key" : None})
    # return render_template("status.html", base_coordinates=base_coordinates, tms_key={"maptiler_key" : rtkbaseconfig.get("general", "maptiler_key")})

# def home():
#     return render_template("index.html.j2")

@app.route('/settings')
def settings_page():
    """
        The settings page where you can manage the various services, the parameters, update, power...
    """
    # main_settings = rtkbaseconfig.get_main_settings()
    # ntrip_settings = rtkbaseconfig.get_ntrip_settings()
    # file_settings = rtkbaseconfig.get_file_settings()
    # rtcm_svr_settings = rtkbaseconfig.get_rtcm_svr_settings()

    return render_template("settings.html") #, main_settings = main_settings,
                                            # ntrip_settings = ntrip_settings,
                                            # file_settings = file_settings,
                                            # rtcm_svr_settings = rtcm_svr_settings)

@app.route('/logs')
def logs_page():
    """
        The data web pages where you can download/delete the raw gnss data
    """
    return render_template("logs.html")

def run():
    app.run(debug=True, port=5001, host="0.0.0.0")

if __name__ == "__main__":
    run()