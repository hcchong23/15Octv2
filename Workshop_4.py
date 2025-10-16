import pandas as pd
import plotly.express as px
import dash
from dash import dcc, html
from dash.dependencies import Input, Output

df1 = pd.read_excel("workshop/Workshop_meriman.xlsm", sheet_name="Raw")

workshop_app=html.Div([
    html.H1("Total Repairs by Workshop in Calendar Year 2024 (Source: Meriman)", className="main-title"),
    html.Div([
        dcc.RadioItems(
            id='Cost-of-Repair_button',
            options=[
                {'label': 'Total Cost', 'value': 'Total_Cost'},
                {'label': 'Average Cost', 'value': 'Avg_Cost'},
                {'label': 'Claim Count', 'value': 'Claim_Count'},
            ],
            value='Avg_Cost',  # ← must match one of the option values exactly
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        )
    ]),
    dcc.Graph(id="Workshop_chart1"),
 ])
def register_workshop_callbacks(app):
    @app.callback(
            Output("Workshop_chart1", "figure"),
            Input("Cost-of-Repair_button", "value"),
        )
    def workshop_chart1(selected_cost):
        if selected_cost=="Avg_Cost":
            summary = (
                df1
                .groupby('Company', observed=False)["Total Recommend'n"]     
                .mean()                                                      
                .reset_index()                                             
                .sort_values('Total Recommend\'n', ascending=True)           
            )
        elif selected_cost=="Total_Cost" :
            summary = (
                df1
                .groupby('Company', observed=False)["Total Recommend'n"]      
                .sum()                                                       
                .reset_index()                                             
                .sort_values('Total Recommend\'n', ascending=True)           
            )
        else: 
            summary = (
                df1
                .groupby('Company', observed=False)["Claim No"]      
                .count()                                                       
                .reset_index(name="Total Recommend'n")                                             
                .sort_values('Total Recommend\'n', ascending=True)           
            )

        summary = summary[summary["Total Recommend'n"] > 0]

        bars = summary.shape[0]
        fig_height = max(400, bars * 20)  # 30px per bar, min 400px

        fig = px.bar(
            summary,
            x="Total Recommend'n",
            y="Company",
            orientation="h",
            text="Total Recommend'n",
        )
        fig.update_layout(
            height=fig_height,
            title="Total Approved @ May 2025",
            margin=dict(t=50, b=20, l=0, r=20),
            xaxis_title="Amount $",
            yaxis_title="Workshop",
            yaxis={"categoryorder": "total ascending"},
            template="plotly_white"
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
        return fig

if __name__ == '__main__':
    app = dash.Dash(__name__, meta_tags=[{"name": "viewport", "content": "width=device-width"}])
    app.layout = workshop_app
    register_workshop_callbacks(app)  
    app.run(debug=True)