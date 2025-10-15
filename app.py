
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
from MPC_1 import motor_app, register_motor_callbacks
from Main_5 import main_app, register_main_callbacks
from Renewal_6 import renew_app, register_renew_callbacks
from Workshop_4 import workshop_app, register_workshop_callbacks
from AgtClass_9 import meetingSlides_app,register_uwslides_callbacks
from Financial_Results_9 import upr_app,register_upr_callbacks


# Build app
app = dash.Dash(__name__, suppress_callback_exceptions=True,  meta_tags=[{"name": "viewport", "content": "width=device-width"}])

app.layout = html.Div([
    dcc.Location(id="url", refresh=False),

    html.Div([                       # ⇦ wrapper
        html.Div([
            html.H2("Navigation"),
            dcc.Link("Main Dashboard", href="/"),
            dcc.Link("Motor- MPC", href="/motor/MPC"),
            dcc.Link("Motor- Renewal", href="/motor/renewal"),
            dcc.Link("Workshop", href="/workshop"),
            dcc.Link("UW", href="/uw"),
            dcc.Link("Finance", href="/finance"),

        ], className="sidebar"),

        html.Div(id="page-content", className="page-content"),
    ], className="main-wrapper"),
])

register_motor_callbacks(app)
register_main_callbacks(app)
register_renew_callbacks(app)
register_workshop_callbacks(app)
register_uwslides_callbacks(app)
register_upr_callbacks(app)

@app.callback(
        Output("page-content","children"),
        Input("url","pathname")
)
def render_page(pathname):
    if pathname=="/motor/MPC":
        return motor_app
    elif pathname=="/motor/renewal":
        return renew_app
    elif pathname=="/workshop":
        return workshop_app
    elif pathname=="/uw":
        return meetingSlides_app
    elif pathname=="/finance":
        return upr_app
    else:
        return main_app

    


if __name__ == '__main__':
    app.run(debug=True, port=8050)
