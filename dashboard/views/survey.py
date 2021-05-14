from models.survey import Survey
from views.general import UserModelView


class SurveyView(UserModelView):
    can_edit = False
    # FIXME: prepare specific views for the survey
    #column_list = (
        #Survey.project,
        #Survey.time_start,
    #)

    #column_labels = {
        #"project.name": "Name of project the survey belongs to",
        #"time_start": "Number of cameras [-]",
    #}
