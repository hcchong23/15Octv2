import dash
from dash import dcc, html, dash_table
import pandas as pd
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import plotly.express as px

import numpy as np
from MPC_monthly_3 import refresh_motorMPC_monthly
from DPD_DCD_2 import refresh_DPD_DCD

# Latest MPC file
df_motor = pd.read_excel('A_MOTOR_MPC_DETAIL_Dashboard.xlsx',sheet_name='Sheet1', keep_default_na=False)
df_motor = df_motor[df_motor['UY'] >= 2021]
df_motor = df_motor[df_motor['Fuel_Type'] != "EV"]
df_motor['Commission'] = pd.to_numeric(df_motor['Commission'], errors='coerce')


# Collection of past MPC files by month
df_summary = pd.read_excel('Monthly_loss_snapshot.xlsx',sheet_name='Sheet1')

year_list2 = sorted([year for year in df_motor['UY'].unique() if year >= 2021])

year_list2 = [str(year) for year in year_list2]  # Convert to string for checklist
scheme_list2 = [str(x) for x in df_motor['Scheme'].unique() if pd.notnull(x)]
model_list2 = sorted([model for model in df_motor['Model_Main'].fillna('Unknown').astype(str).unique()])
riskfactor_list2 = ['Insured_Age_f', 'Vehicle_Age_f', 'Driving_Exp_f', 'Engine_CC.f', 'NCD',  'Model_Main', 'New Business']

category_orders = {
    "Insured_Age_f": ["Below 27", "27-30", "31-35", "36-40", "41-45", "46-50", "51-55", "56-60", "61-65", "66-70", "Above 70"],
    "Vehicle_Age_f": ["0-3", "4-6", "7-10", "11-15", ">=16", "NA"],
    "Driving_Exp_f": ["0-3", "4-10", "11-15", "16-20", ">=21", "NA"],
    "Engine_CC_f": ["<1300", "1300-1399", "1400-1499", "1500-1599", "1600-1799", "1800-1999", "2000-2499", "2500-4999", ">=5000"],
    "NCD":["0","10","20","30","40","50"]
}
for col, order in category_orders.items():
    df_motor[col] = pd.Categorical(df_motor[col], categories=order, ordered=True)

riskfactor_label = {
    'Insured_Age_f': 'Insured Age',
    'Vehicle_Age_f': 'Vehicle Age',
    'Driving_Exp_f': 'Driving Experience',
    'Engine_CC_f': 'Engine CC',
    'NCD': 'NCD',
    'Model_Main': 'Main Model',
    'Agency':'Agency',
    'New_Business':'New Business'
}

agent_list = [str(agent) for agent in df_motor['Agency'].unique()]  



#app1 = dash.Dash(__name__,  meta_tags=[{"name": "viewport", "content": "width=device-width"}])


motor_app = html.Div([
    html.H1(
        "Portfolio Performance - Motor MPC",className="main-title"
    ),

    
   html.Div([
        html.Div([
            html.Button("Refresh MPC data", id="run-button-1", n_clicks=0, style={'width': '300px'}),
            html.Button("Refresh DPD and DCD data", id="run-button-2", n_clicks=0, style={'width': '300px'})
        ], style={'display': 'flex', 'gap': '100px', 'margin-bottom': '10px'}),
        
        html.Div(id="refresh-output-1"),
        html.Div(id="refresh-output-2")
    ]),

    html.Div([
        html.Button("Download CSV", id="btn-download-2",style={'width': '100%','margin-bottom': '10px'}),
        dcc.Download(id="download-dataframe2-csv")
    ]),

    dcc.Interval(id='interval-component', interval=1*1000, n_intervals=0, max_intervals=2),

    html.Div([
        dcc.Graph(
            id="Graph1-LossRatio_UWY"
        )
    ], className="graph"),

    html.Div([
        dcc.Checklist(
            id="Scheme_button",
            options=[{'label': y, 'value': y} for y in scheme_list2],
            value=scheme_list2[:3],
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        )
    ], className="checklist"),

    html.Div([
            dcc.Graph(
                id="Graph2-LossRatio_UWY_Scheme"
            )
    ], className="graph"),


    html.H2(
        "Profitability by Segment",className="secondary-title"
    ),
    html.Div([
        dcc.Checklist(
        id="Year_button",
        options=[{'label': y, 'value': y} for y in  year_list2],
        value=[year_list2[0]],
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    )
    ], className="checklist"),

    html.Div([
        dcc.Dropdown(
            id='Riskfactor_button',
            options=[{'label': label, 'value': value} for value, label in riskfactor_label.items()],
            multi=False,
            value=list(riskfactor_label.keys())[0]  # Default selection
        )
    ], className="dropdown"),


    html.Div([
        dcc.Graph(
            id="Graph3-FreqSevChart"
        )
    ], className="graph"),

    html.Div([
        dcc.Graph(
            id="Graph4-LossRatio"
        )
    ], className="graph"),

    html.Div([
        html.Div("Trantype = 'N' and 'R'", style={"marginLeft": "10px"}),
        dcc.Graph(id="Graph5-AvgPrem")
    ], className="graph"),

    html.H2(
        "Performance by Vehicle Make",className="secondary-title"
    ),
    html.Div([
        dcc.Checklist(
            id="Year_button5",
            options=[{'label': y, 'value': y} for y in year_list2],
            value=[year_list2[0]],
            labelStyle={'display': 'inline-block', 'margin-right': '10px'}
        ),

        dcc.RadioItems(
            id='Premium-info_button5',
            options=[
                {'label': 'Loss Ratio', 'value': 'LossRatio'},
                {'label': 'Total Premium', 'value': 'TotalPrem'},
                {'label': 'Average Premium', 'value': 'AvgPrem'},
                {'label': 'Policy Count', 'value': 'Exposure'},
            ],
            value='LossRatio',  # default
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        ),

        dcc.Dropdown(
            id="Model_button5",
            options=[{'label': y, 'value': y} for y in model_list2],
            value=["TOYOTA","HONDA"],  # 🔁 Use list only if multi=True
            multi=True,              # 👈 Allow multiple models
            style={"width": "300px", "marginTop": "10px"}
        )
    ], className="checklist"),
    
    html.Div([
        dcc.Graph(id="Graph6-VehMake")
    ], className="graph"),

    html.H2(
        "Portfolio Concentration",className="secondary-title"
    ),
    
    html.Div([
        dcc.Checklist(
        id="Checklist_button2",
        options=[{'label': label, 'value': value} for value, label in  riskfactor_label.items()],
        value=[  list(riskfactor_label.keys())[0]],
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    )
    ], className="checklist"),

    html.Div([
        dcc.Checklist(
        id="Year_button7",
        options=[{'label': y, 'value': y} for y in  year_list2],
        value=[year_list2[0]],
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    )
    ], className="checklist"),

    html.Div(
        "Top 3 Segments: ",className="third-title"
    ),

   html.Div([
        html.Div(id='top3-list', className='half-div'),
        html.Div(id='bottom3-list', className='half-div'),
    ], className='side-by-side-title'),
   
    html.Div(id='table_listing'),

    html.H2(
        "Monthly Loss Ratio Movement",className="secondary-title"
    ),

    html.Div([
        html.Div([
            dcc.Checklist(
                id="Year_button3",
                options=[{'label': y, 'value': y} for y in year_list2],
                value=[year_list2[0]],
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            )
        ], className="checklist"),

        html.Div([
            dcc.Checklist(
                id="Scheme_button2",
                options=[{'label': y, 'value': y} for y in scheme_list2],
                value=[scheme_list2[0]],
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            )
        ], className="checklist"),
    ], style={"marginBottom": "20px"}),


    html.Div([
        dcc.Graph(
            id="monthly-loss-chart6")
    ], className="graph"),

    html.H2(
        "Monthly Frequency Movement",className="secondary-title"
    ),

    html.Div([
        html.Div([
            dcc.Checklist(
                id="Year_button8",
                options=[{'label': y, 'value': y} for y in year_list2],
                value=[year_list2[0]],
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            )
        ], className="checklist"),

        html.Div([
            dcc.Checklist(
                id="Scheme_button3",
                options=[{'label': y, 'value': y} for y in scheme_list2],
                value=[scheme_list2[0]],
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            )
        ], className="checklist"),

        html.Div([
            dcc.RadioItems(
                id="RiskFactor_button2",
                options=[{'label': y, 'value': y} for y in riskfactor_list2],
                value=riskfactor_list2[0],
                labelStyle={'display': 'inline-block', 'margin-right': '10px'}
            )
        ]),

    ], style={"marginBottom": "20px"}),

    # html.Div([
    #     dcc.Graph(
    #         id="freq-chart10")
    # ], className="graph"),
    html.Div([
        dcc.Tabs(id="tabs-freqsev", value='tab-1-freq-chart10', children=[
            dcc.Tab(label='Frequency', value='tab-1-freq-chart10'),
            dcc.Tab(label="Severity", value="tab-1-sev-chart10"),

        ]),
        html.Div(id='tabs-content-graph', children=[
           dcc.Graph(id="freq-chart10", figure={}),
            dcc.Graph(id="sev-chart10", figure={})
        ]),
    ]),


    html.H2(
        "Agents",className="secondary-title"
    ),

    html.Div([
        dcc.Dropdown(
            id='Agency_list',
            options=[{'label': agent, 'value': agent} for agent in agent_list],
            multi=True,
            placeholder="Select agencies"
        )
    ], className="dropdown"),

    html.Div([
        dcc.Checklist(
        id="Year_button4",
        options=[{'label': y, 'value': y} for y in year_list2],
        value=[year_list2[0]],
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    )
    ], className="checklist"),

    html.Div([
        dcc.Dropdown(
            id='Riskfactor_button2',
            options=[{'label': label, 'value': value} for value, label in riskfactor_label.items()],
            multi=False,
            value=list(riskfactor_label.keys())[0]  # Default selection
        )
    ], className="dropdown"),


    html.Div([
        dcc.Graph(
            id="agency-production-chart")
    ], className="graph"),
   
    html.Div([
        dcc.Checklist(
        id="Year_button6",
        options=[{'label': y, 'value': y} for y in year_list2],
        value=[year_list2[0]],
        labelStyle={'display': 'inline-block', 'margin-right': '10px'}
    )
    ], className="checklist"),

    html.Div(
        "Total Commission Paid: ",className="third-title"
    ),

    html.Div([
        dcc.Graph(
            id="agency-commission-chart")
    ], className="graph"),
    
    html.Div(
        "Commission per policy / Commission rate: ",className="third-title"
    ),
    html.Div(
        dcc.RadioItems(
            id='Commission-info_button',
            options=[
                {'label': 'Average Commission', 'value': 'AvgComm'},
                {'label': 'Commission Rate', 'value': 'CommRate'},
            ],
            value='AvgComm',  # default
            labelStyle={'display': 'inline-block', 'margin-right': '15px'}
        )
    ),

    html.Div([
        dcc.Graph(
            id="agency-commission-chart2")
    ], className="graph"),


], id='mainContainer', className= "main-container" )

def register_motor_callbacks(app):

    @app.callback(
        Output("refresh-output-1", "children"),
        Input("run-button-1", "n_clicks"),
        prevent_initial_call=True
    )
    def run_script(n_clicks):
        # Run the external script using subprocess
        if n_clicks and n_clicks > 0:
            try:
                refresh_motorMPC_monthly()
                # Optionally, you could inspect df_result here before returning.
                return "✅ Task completed: monthly_loss_ratio.xlsx has been created."
            except Exception as e:
                return f"❌ Failed to update: {str(e)}"
        return ""
    
    @app.callback(
        Output("refresh-output-2", "children"),
        Input("run-button-2", "n_clicks"),
        prevent_initial_call=True
    )
    def run_script2(n_clicks):
        # Run the external script using subprocess
        if n_clicks and n_clicks > 0:
            try:
                refresh_DPD_DCD()
                # Optionally, you could inspect df_result here before returning.
                return "✅ Task completed: Dashboard_data.xlsx has been created."
            except Exception as e:
                return f"❌ Failed to update: {str(e)}"
        return ""
    
    
    @app.callback(
        Output("download-dataframe2-csv", "data"),
        Input("btn-download-2", "n_clicks"),
        prevent_initial_call=True
    )
    def generate_csv(n_clicks):
        return dcc.send_data_frame(df_motor.to_csv, "dashboard_data2.csv", index=False)

    @app.callback(
        Output('Graph1-LossRatio_UWY', 'figure'),
        Input('interval-component', 'n_intervals')
    )
    def lossratio_chart1(n):
        df_motor_summary=df_motor.copy()
        df_motor_summary = (
            df_motor_summary
            .groupby('UY',observed=False)
            .agg({
                'Premium_b4_GST' : 'sum',
                'Total_Incurred_Claim':'sum'
            })
            .reset_index()
        )

        df_motor_summary['Loss Ratio'] = df_motor_summary['Total_Incurred_Claim'] / df_motor_summary['Premium_b4_GST']
        df_motor_summary = df_motor_summary.sort_values(by='UY', ascending=True)
        df_motor_summary['UY'] = df_motor_summary['UY'].astype(str)
        

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df_motor_summary['UY'],
            y=df_motor_summary['Premium_b4_GST'],
            name="Gross Premium",
            text=df_motor_summary['Premium_b4_GST'],
            texttemplate='$' + '%{text:,.2s}',
            marker_color='yellow',
            textposition="inside",
            textfont=dict(color="black"),  
            hovertemplate="UW Year: %{x}<br>Gross Premium: $%{y:,.0f}"
        ))

        fig.add_trace(go.Scatter(
            x=df_motor_summary['UY'],
            y=df_motor_summary['Loss Ratio'],
            name="Loss Ratio",
            mode='lines+markers+text',
            text=df_motor_summary["Loss Ratio"].map(lambda x: f"{x:.0%}"),  
            textfont=dict(color="red"),
            textposition="top center", 
            line=dict(color='red', width=2),
            yaxis="y2",
            hovertemplate="UW Year: %{x}<br>Loss Ratio: %{y:.1%}"
        ))

        fig.update_layout(
            title=dict(text="Gross Premium and Loss Ratio by UW Year",font=dict(size=13) ),
            xaxis=dict(
                title="UW Year",
                showgrid=False
            ),
            yaxis=dict(
                title=dict(
                    text="Gross Premium",  # Set the title text
                    font=dict(color="blue")  # Set the font color
                ),
                tickfont=dict(color="blue"),
                showgrid=False
            ),
            yaxis2=dict(
                title=dict(
                    text="Loss Ratio",
                    font=dict(color="red")
                ),
                overlaying="y",
                side="right",
                tickformat=".0%",  # Display as percentage
                tickfont=dict(color="red"),
                showgrid=False,
                zeroline = False,
            ),
            legend=dict(x=0.8, y=1.2, bgcolor="rgba(0,0,0,0)"),
        )
        return fig



    @app.callback(
        Output('Graph2-LossRatio_UWY_Scheme', 'figure'),
        Input('Scheme_button', 'value'),
    )
    def lossratio_chart2(selected_scheme):
        df_motor_filtered=df_motor.copy()
        if selected_scheme:
            df_motor_filtered= df_motor_filtered[df_motor_filtered['Scheme'].isin(selected_scheme)]
        else:
            df_motor_filtered = df_motor_filtered.copy() # or handle empty selection as needed

        # Aggregate data
        df_motor_summary = (
            df_motor_filtered
            .groupby( ['UY','Scheme'] , observed=False)
            .agg({
                'Premium_b4_GST': 'sum', 
                'Total_Incurred_Claim': 'sum'
            })
            .reset_index()
        )

        # Compute Loss Ratio
        df_motor_summary['Loss Ratio'] = df_motor_summary['Total_Incurred_Claim'] / df_motor_summary['Premium_b4_GST']
        # Sort by UY
        df_motor_summary = df_motor_summary.sort_values(by='UY')
        df_motor_summary['UY'] = df_motor_summary['UY'].astype(str)
        scheme_colors = {
            'MPC': "#ffff00",     # bright yellow
            'MFP': "#FFDD00",     # medium yellow
            'MCT': "#FFAA00",     # light orange
            'Others': "#FF7F50"      # medium orange
        }

        scheme_colors2 = {
            'MPC': "#00FF7F",  # Light Mint Green
            'MFP': "#66c2a5",  # Soft Teal Green
            'MCT': "#2ca25f",  # Medium Green
            'Others': "#006d2c"   # Deep Forest Green
        }
        fig = go.Figure()
        for scheme in df_motor_summary['Scheme'].unique():
            df_sub = df_motor_summary[df_motor_summary['Scheme'] == scheme]
            bar_color = scheme_colors.get(scheme) 
            line_color = scheme_colors2.get(scheme)  

            fig.add_trace(go.Bar(
                x=df_sub['UY'],
                y=df_sub['Premium_b4_GST'],
                name=f"{scheme} - Gross Premium",
                text=df_sub['Premium_b4_GST'],
                texttemplate='$%{text:,.2s}',
                textposition="inside",
                marker=dict(color=bar_color ),
                textfont=dict(color="black"),
                hovertemplate="UW Year: %{x}<br>Gross Premium: $%{y:,.0f}"

            ))

            fig.add_trace(go.Scatter(
                x=df_sub['UY'],
                y=df_sub['Loss Ratio'],
                name=f"{scheme} - Loss Ratio",
                mode='lines+markers+text',
                text=df_sub["Loss Ratio"].map(lambda x: f"{x:.0%}"),
                textposition="top center",
                textfont=dict(color="red"),
                line=dict(color= line_color , width=2),
                yaxis="y2",
                hovertemplate="UW Year: %{x}<br>Loss Ratio: %{y:.1%}"
            ))

        fig.update_layout(
            title=dict(text="Gross Premium and Loss Ratio by UW Year and Scheme", font=dict(size=13)),
            xaxis=dict(title="UW Year", showgrid=False),
            yaxis=dict(
                title=dict(text="Gross Premium", font=dict(color="blue")),
                tickfont=dict(color="blue"),
                showgrid=False
            ),
            yaxis2=dict(
                title=dict(text="Loss Ratio", font=dict(color="red")),
                overlaying="y",
                side="right",
                tickformat=".0%",
                tickfont=dict(color="red"),
                showgrid=False,
                zeroline=False
            ),
            legend=dict(x=0.8, y=1.2, bgcolor="rgba(0,0,0,0)")
        )
        return fig

    @app.callback(
        Output('Graph3-FreqSevChart', 'figure'),
        Input('Riskfactor_button', 'value'),
        Input('Year_button', 'value')
    )
    def freqsev_chart3(selected_riskfactor, selected_year):
        df_motor_filtered=df_motor.copy()
        df_motor_filtered['UY'] =   df_motor_filtered['UY'].astype(str)
        df_motor_filtered =   df_motor_filtered[ df_motor_filtered['UY'].isin(selected_year)]

        # Group and aggregate
        df_motor_filtered = (
            df_motor_filtered
            .groupby(selected_riskfactor,observed=False)
            .agg(
                Total_RiskExp=('RiskExp', 'sum'),
                Total_Incurred_Claim=('Total_Incurred_Claim', 'sum'),
                Total_Claim_Count=('No_Claims', 'sum') 
            )
            .reset_index()
        )

        # Calculate frequency and severity
        df_motor_filtered['Frequency'] = df_motor_filtered['Total_Claim_Count'] / df_motor_filtered['Total_RiskExp']
        df_motor_filtered['Severity'] = df_motor_filtered['Total_Incurred_Claim'] / df_motor_filtered['Total_Claim_Count']


        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_motor_filtered[selected_riskfactor],
            y=df_motor_filtered['Severity'],
            name="Severity",
            marker_color='#FFA07A',
            text=df_motor_filtered['Severity'].fillna(0).round(0).astype(int).astype(str),  # integer values
            textposition='outside',
            yaxis="y",  # Left axis
            hovertemplate=f"{selected_riskfactor}: %{{x}}<br>Severity: %{{y:.0f}}"
        ))

        # Line chart for Frequency
        fig.add_trace(go.Scatter(
            x=df_motor_filtered[selected_riskfactor],
            y=df_motor_filtered['Frequency'],
            name="Frequency",
            mode='lines+markers+text',
            marker=dict(color='green'),
            text=[f"{y:.1%}" for y in df_motor_filtered['Frequency']],  # format as percent
            textposition='top center', 
            line=dict(color='green', width=2),
            yaxis="y2",  # Right axis
            hovertemplate=f"{selected_riskfactor}: %{{x}}<br>Frequency: %{{y:.1%}}"
        ))

        # Layout remains unchanged
        fig.update_layout(
            title=f"Frequency and Severity by {selected_riskfactor}",
            xaxis=dict(title=selected_riskfactor),
  
            yaxis=dict(
                title=dict(text="Severity", font=dict(color="#FFA07A")),
                tickfont=dict(color="#FFA07A"),
                tickformat=".0f",
                side="right",
                showgrid=False
            ),

            yaxis2=dict(
                title=dict(text="Frequency", font=dict(color="green")),
                tickfont=dict(color="green"),
                tickformat=".0%",
                overlaying="y",
                showgrid=False
            ),
            legend=dict(
                orientation="h",
                x=0.5,
                y=-0.3,
                xanchor="center",
                yanchor="top"
            )
        )
        return fig

    @app.callback(
    Output('Graph4-LossRatio', 'figure'),
    Input('Riskfactor_button', 'value'),
    Input('Year_button', 'value')
    )
    def lossratio_chart4(selected_riskfactor, selected_year):
        df_motor_filtered=df_motor.copy()
        df_motor_filtered['UY'] = df_motor_filtered['UY'].astype(str)
        df_motor_filtered = df_motor_filtered[df_motor_filtered['UY'].isin(selected_year)].copy()

        # Group by UY and selected risk factor
        df_motor_filtered = (
            df_motor_filtered
            .groupby([selected_riskfactor], observed=False)
            .agg({
                'Premium_b4_GST': 'sum', 
                'Total_Incurred_Claim': 'sum'
            })
            .reset_index()
        )

        # Compute Loss Ratio
        df_motor_filtered['Loss Ratio'] = df_motor_filtered['Total_Incurred_Claim'] / df_motor_filtered['Premium_b4_GST']

        # Plot
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_motor_filtered[selected_riskfactor],
            y=df_motor_filtered['Premium_b4_GST'],
            name="Gross Premium",
            text=df_motor_filtered['Premium_b4_GST'],
            texttemplate='$' + '%{text:,.2s}',
            marker_color='yellow',
            textposition="inside",
            textfont=dict(color="black"),  
            hovertemplate="UW Year: %{x}<br>Gross Premium: $%{y:,.0f}"
        ))

        fig.add_trace(go.Scatter(
            x=df_motor_filtered[selected_riskfactor],
            y=df_motor_filtered['Loss Ratio'],
            name="Loss Ratio",
            mode='lines+markers+text',
            text=df_motor_filtered["Loss Ratio"].map(lambda x: f"{x:.0%}"),  
            textfont=dict(color="red"),
            textposition="top center", 
            line=dict(color='red', width=2),
            yaxis="y2",
            hovertemplate="UW Year: %{x}<br>Loss Ratio: %{y:.1%}"
        ))

        fig.update_layout(
            title=dict(text=f"Gross Premium and Loss Ratio by {selected_riskfactor}", font=dict(size=13)),
            xaxis=dict(title=f"{selected_riskfactor}", showgrid=False),
            yaxis=dict(
                title=dict(text="Gross Premium", font=dict(color="blue")),
                tickfont=dict(color="blue"),
                showgrid=False
            ),
            yaxis2=dict(
                title=dict(text="Loss Ratio", font=dict(color="red")),
                overlaying="y",
                side="right",
                tickformat=".0%",
                tickfont=dict(color="red"),
                showgrid=False,
                zeroline=False
            ),
            legend=dict(x=0.8, y=1.2, bgcolor="rgba(0,0,0,0)")
        )

        return fig
    
    @app.callback(
    Output('Graph5-AvgPrem', 'figure'),
    Input('Riskfactor_button', 'value'),
    Input('Year_button', 'value')
    )
    def avgprem_chart5(selected_riskfactor, selected_year):
        df_motor_filtered=df_motor.copy()
        df_motor_filtered['UY'] = df_motor_filtered['UY'].astype(str)
        df_motor_filtered = df_motor_filtered[df_motor_filtered['UY'].isin(selected_year)]
        df_motor_filtered = df_motor_filtered[df_motor_filtered['trantype'].isin(['N', 'R'])]

        # Group by UY and selected risk factor
        df_motor_filtered = (
            df_motor_filtered
            .groupby(selected_riskfactor, observed=False)
            .agg(
                Total_Gross_Premium=('Premium_b4_GST', 'sum'),
                Total_Incurred_Claim=('Total_Incurred_Claim', 'sum'),
                Count=('polno', 'count') 
            )
            .reset_index()
        )

        # Compute Loss Ratio
        df_motor_filtered['AveragePrem'] = df_motor_filtered['Total_Gross_Premium'] / df_motor_filtered['Count']

        # Plot
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_motor_filtered[selected_riskfactor],
            y=df_motor_filtered['AveragePrem'],
            name="Average Premium",
            text=df_motor_filtered['AveragePrem'],
            texttemplate='$%{text:,.2f}',  # More appropriate formatting for currency
            textposition="inside",
            textfont=dict(color="black"),
            hovertemplate="UW Year: %{x}<br>Gross Premium: $%{y:,.0f}<extra></extra>"
        ))

        fig.update_layout(
            title=dict(text=f"Average Premium by {selected_riskfactor}", font=dict(size=13)),
            xaxis=dict(title=f"{selected_riskfactor}", showgrid=False),
            yaxis=dict(
                title=dict(text="Average Premium", font=dict(color="blue")),
                tickfont=dict(color="blue"),
                showgrid=False
            ),
            legend=dict(x=0.8, y=1.2, bgcolor="rgba(0,0,0,0)")  
        )

        return fig
    
    @app.callback(
    Output('Graph6-VehMake', 'figure'),
    Input('Year_button5', 'value'),
    Input('Model_button5', 'value'),
    Input('Premium-info_button5','value')
    )
    def vehmake_chart6(selected_year,selected_model,selected_info):
        df_motor_filtered=df_motor.copy()
        df_motor_filtered['UY'] = df_motor_filtered['UY'].astype(str)
        df_motor_filtered = df_motor_filtered[df_motor_filtered['UY'].isin(selected_year)]
        df_motor_filtered = df_motor_filtered[df_motor_filtered['Model_Main'].isin(selected_model)]

        # Group by UY and selected risk factor
        df_motor_filtered = (
            df_motor_filtered
            .groupby('Model_Make', observed=False)
            .agg(
                Total_Gross_Premium=('Premium_b4_GST', 'sum'),
                Total_Incurred_Claim=('Total_Incurred_Claim', 'sum'),
                Exposure=('polno', 'count') 
            )
            .reset_index()
        )

        # Compute Loss Ratio
        df_motor_filtered['LossRatio'] = df_motor_filtered['Total_Incurred_Claim'] / df_motor_filtered['Total_Gross_Premium']      
        df_motor_filtered['AvgPrem'] = df_motor_filtered['Total_Gross_Premium'] / df_motor_filtered['Exposure']       
        df_motor_filtered['TotalPrem'] = df_motor_filtered['Total_Gross_Premium']  

 
        df_motor_filtered= df_motor_filtered.sort_values("LossRatio", ascending=True)
        df_motor_filtered2 = df_motor_filtered[df_motor_filtered['LossRatio'] > 0]

        row_height = 5

        # Calculate chart height: don't let each row take more than 10px
        chart_height = len(df_motor_filtered) * row_height
        chart_height2 = len(df_motor_filtered2) * row_height

        if selected_info == 'LossRatio':
            fig1 = px.bar(
                df_motor_filtered2,
                x="LossRatio",  # Now on x-axis
                y="Model_Make",  # Now on y-axis (categories on the vertical)
                text=df_motor_filtered2["LossRatio"].apply(lambda x: f"{x:.0%}"),
                labels={"LossRatio": "Loss Ratio", "Model_Make": "Vehicle Make"},
                title="Loss Ratio by Vehicle Make",
                orientation='h',  # Required for horizontal bars
                height=chart_height2 
            )

            fig1.update_traces(
                textposition='outside',
                marker_color='steelblue'
            )

            fig1.update_layout(
                xaxis_tickformat=".0%",
                xaxis_range=[0, df_motor_filtered2["LossRatio"].max() * 1.1],  # Add margin
                bargap=0.1,      # 👈 Smaller gap = thicker bars,
                margin=dict(l=250),
                height=len(df_motor_filtered2) * 30,  # 30px per bar
            )

            return fig1

        elif selected_info == 'TotalPrem':
            fig2 = px.bar(
                df_motor_filtered,
                x="TotalPrem",  # Now on x-axis
                y="Model_Make",  # Now on y-axis (categories on the vertical)
                text=df_motor_filtered["TotalPrem"].apply(lambda x: f"{x:,.2f}"),
                labels={"TotalPrem": "Total Premium", "Model_Make": "Vehicle Make"},
                title="Total Premium by Vehicle Make",
                orientation='h',  # Required for horizontal bars
                height=len(df_motor_filtered) * 30,  # 30px per bar
            )

            return fig2
        
        elif selected_info == 'AvgPrem':
            fig3 = px.bar(
                df_motor_filtered,
                x="AvgPrem",  # Now on x-axis
                y="Model_Make",  # Now on y-axis (categories on the vertical)
                text=df_motor_filtered["AvgPrem"].apply(lambda x: f"{x:,.2f}"),
                labels={"AvgPrem": "Average Premium", "Model_Make": "Vehicle Make"},
                title="Average Premium by Vehicle Make",
                orientation='h',  # Required for horizontal bars
                height=len(df_motor_filtered) * 30,  # 30px per bar
            )

            return fig3
        

        elif selected_info == 'Exposure':
            fig4 = px.bar(
                df_motor_filtered,
                x="Exposure",  # Now on x-axis
                y="Model_Make",  # Now on y-axis (categories on the vertical)
                text=df_motor_filtered["Exposure"].apply(lambda x: f"{x:,.0f}"),
                labels={"Exposure": "Exposure", "Model_Make": "Vehicle Make"},
                title="Exposure by Vehicle Make",
                orientation='h',  # Required for horizontal bars
                height=len(df_motor_filtered) * 30,  # 30px per bar
            )

            return fig4

    @app.callback(
        Output('top3-list', 'children'),
        Output('bottom3-list', 'children'),
        Output('table_listing', 'children'),
        Input('Checklist_button2', 'value'),
        Input('Year_button7', 'value')
    )
    def loss_segment_table6(selected_riskfactor, selected_year):
        if not selected_riskfactor:
            return (
                html.P("⚠️ Please choose at least 1 risk factor to display the results.", style={"color": "red"}),
                html.Div(style={'display': 'none'}),
                html.Div(style={'display': 'none'})  
            )
        df_motor_filtered=df_motor.copy()
        df_motor_filtered['UY'] = df_motor_filtered['UY'].astype(str)
        df_motor_filtered = df_motor_filtered[df_motor_filtered['UY'].isin(selected_year)]

        # Group by selected risk factor
        df_grouped = (
            df_motor_filtered
            .groupby(selected_riskfactor, observed=False)
            .agg(
                Total_Gross_Premium=('Premium_b4_GST', 'sum'),
                Total_Incurred_Claim=('Total_Incurred_Claim', 'sum'),
                Count=('polno', 'count')
            )
            .reset_index()
        )

        # Calculate loss ratio and % of GWP 
        df_grouped['% Loss_Ratio'] = round(
            df_grouped['Total_Incurred_Claim'] / df_grouped['Total_Gross_Premium'] * 100, 2
        )        
        total_gwp = df_grouped['Total_Gross_Premium'].sum()

        df_grouped['% GWP'] = round(
            df_grouped['Total_Gross_Premium'] / total_gwp * 100, 2
        )
        df_grouped_filtered = df_grouped.nlargest(10, '% GWP')

        # Get top 3 segments by loss ratio
        top3 = df_grouped_filtered.sort_values(by='% Loss_Ratio', ascending=False).head(3)
        top3 = top3.reset_index(drop=True)
        top3_gwp = top3['Total_Gross_Premium'].sum()
        top3_gwp_pct = (top3_gwp / total_gwp) * 100

        # Average loss ratio of top 3
        avg_loss_ratio_top3 = top3['% Loss_Ratio'].mean()

        # Get bottom 3 segments by loss ratio
        bottom3 = df_grouped_filtered.sort_values(by='% Loss_Ratio', ascending=False).tail(3)
        bottom3 = bottom3.reset_index(drop=True)
        bottom3_gwp = bottom3['Total_Gross_Premium'].sum()
        bottom3_gwp_pct = (bottom3_gwp / total_gwp) * 100

        # Average loss ratio of bottom 3
        avg_loss_ratio_bottom3 = bottom3['% Loss_Ratio'].mean()

        # Format number 
        df_grouped['Total_Gross_Premium'] = df_grouped['Total_Gross_Premium'].apply(lambda x: f"{x:,.2f}")
        df_grouped['Total_Incurred_Claim'] = df_grouped['Total_Incurred_Claim'].apply(lambda x: f"{x:,.2f}")
        
        segment_paragraphs_top3 = [
            html.P(
                f"{i+1}. " + ", ".join(f"{riskfactor_label.get(risk, risk)}={row[risk]}" for risk in selected_riskfactor)
            )
            for i, row in top3.iterrows()
        ]

        segment_paragraphs_bottom3 = [
            html.P(
                f"{i+1}. " + ", ".join(f"{riskfactor_label.get(risk, risk)}={row[risk]}" for risk in selected_riskfactor)
            )
            for i, row in bottom3.iterrows()
        ]

        summary_top3 = html.Div([
            html.P(f"a). Top 3 high-loss segments contributing {top3_gwp_pct:.2f}% of total GWP. They are:"),
            *segment_paragraphs_top3,
            html.P(f"Average loss ratio: {avg_loss_ratio_top3:.2f}%.")
        ])

        summary_bottom3 = html.Div([
            html.P(f"b). Top 3 best-performing segments contributing {bottom3_gwp_pct:.2f}% of total GWP. They are:"),
            *segment_paragraphs_bottom3,
            html.P(f"Average loss ratio: {avg_loss_ratio_bottom3:.2f}%.")
        ])

        table = dash_table.DataTable(
            columns=[{"name": i, "id": i} for i in df_grouped.columns],
            data=df_grouped.to_dict('records'),
            filter_action='native',     
            sort_action='native', 
            sort_mode='multi',    
            style_cell={'textAlign': 'left'},
            style_header={'fontWeight': 'bold', 'backgroundColor': 'rgb(230, 230, 230)'},
            style_table={  
                'overflowX': 'auto',  # ✅ horizontal scroll
                'maxHeight': '400px',  # ✅ vertical scroll
                'overflowY': 'auto',},
            page_size=10
        )
        return summary_top3, summary_bottom3,  table
        
    @app.callback(
        Output('monthly-loss-chart6', 'figure'),
        Input('Scheme_button2', 'value'),
        Input('Year_button3', 'value')
    )

    def monthly_loss_chart7(selected_scheme, selected_year):
        df_summary_filtered=df_summary.copy()
        df_summary_filtered['UY'] = df_summary_filtered['UY'].astype(str)
        df_summary_filtered = df_summary_filtered[df_summary_filtered['Scheme'].isin(selected_scheme)]
        df_summary_filtered = df_summary_filtered[df_summary_filtered['UY'].isin(selected_year)]

        df_summary_filtered = df_summary_filtered.groupby(["UY","file_date"],observed=False).agg({
            "Total_Incurred_Claim_sum": "sum",
            "Premium_b4_GST_sum": "sum"
        }).reset_index()

        df_summary_filtered["Loss_Ratio"] =  df_summary_filtered["Total_Incurred_Claim_sum"] /  df_summary_filtered["Premium_b4_GST_sum"]

        try:
             df_summary_filtered["file_date_dt"] = pd.to_datetime( df_summary_filtered["file_date"], format="%m-%Y")
             df_summary_filtered = df_summary_filtered.sort_values("file_date_dt")
        except:
            pass  # Ignore if datetime or sorting not needed
        fig = px.line( df_summary_filtered, x="file_date", y="Loss_Ratio",
            title="Monthly Loss Ratio",
            markers=True,
            color="UY",
            labels={"file_date": "Month", "Loss_Ratio": "Loss Ratio"},
            text="Loss_Ratio")
        fig.update_layout(
            yaxis=dict(
                tickformat=".1%",  
                dtick=0.1,          # step size (0.1 = 10%)
            ),
            xaxis_title=None
        )
        fig.update_traces(
            texttemplate="%{text:.2%}",   # format as percentage
            textposition="top center"     # show above points
        )
        return fig
    
        
    @app.callback(
    Output('agency-production-chart', 'figure'),
    Input('Agency_list', 'value'),
    Input('Year_button4', 'value'),
    Input('Riskfactor_button2', 'value'),
    )
    def agency_performance8(selected_agent, selected_year, selected_factor):
        df_motor_filtered=df_motor.copy()
        # Convert UY to string for filtering
        df_motor_filtered['UY'] = df_motor_filtered['UY'].astype(str)
        # Filter by selected agents and years
        if selected_agent:
            df_motor_filtered = df_motor_filtered[df_motor_filtered['Agency'].isin(selected_agent)]
        if selected_year:
            df_motor_filtered = df_motor_filtered[df_motor_filtered['UY'].isin([str(y) for y in selected_year])]
        # Group by the selected risk factor (e.g., 'Make', 'Model', or 'RiskFactor')
        df_motor_summary = (
            df_motor_filtered
            .groupby(selected_factor, observed=False, as_index=False)
            .agg(
                GWP=('Premium_b4_GST', 'sum'),
                Claims=('Total_Incurred_Claim', 'sum'),
                Policies=('polno', 'count')
            )
        )
        df_motor_summary['Loss Ratio']=df_motor_summary['Claims']/df_motor_summary['GWP']

        # Build bar chart for GWP
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_motor_summary[selected_factor],
            y=df_motor_summary['GWP'],
            name="Gross Written Premium",
            text=df_motor_summary['GWP'],
            texttemplate='$%{text:,.0f}',
            marker_color='yellow',
            textposition="inside",
            textfont=dict(color="black"),
            hovertemplate=f"{selected_factor}: %{{x}}<br>Gross Premium: $%{{y:,.0f}}<extra></extra>"
        ))


        fig.add_trace(go.Scatter(
            x=df_motor_summary[selected_factor],
            y=df_motor_summary['Loss Ratio'],
            name="Loss Ratio",
            mode='lines+markers+text',
            text=df_motor_summary["Loss Ratio"].map(lambda x: f"{x:.0%}"),  
            textfont=dict(color="red"),
            textposition="top center", 
            line=dict(color='red', width=2),
            yaxis="y2",
            hovertemplate="UW Year: %{x}<br>Loss Ratio: %{y:.1%}"
        ))

        fig.update_layout(
            title=dict(text=f"Gross Premium and Loss Ratio by {selected_factor}", font=dict(size=13)),
            xaxis=dict(title=f"{selected_factor}", showgrid=False),
            yaxis=dict(
                title=dict(text="Gross Premium", font=dict(color="blue")),
                tickfont=dict(color="blue"),
                showgrid=False
            ),
            yaxis2=dict(
                title=dict(text="Loss Ratio", font=dict(color="red")),
                overlaying="y",
                side="right",
                tickformat=".0%",
                tickfont=dict(color="red"),
                showgrid=False,
                zeroline=False
            ),
            legend=dict(x=0.8, y=1.2, bgcolor="rgba(0,0,0,0)")
        )
   

        return fig
    
    @app.callback(
        Output('agency-commission-chart', 'figure'),
        Input('Year_button6', 'value')
    )
    def agency_commission9(selected_year):
        df_motor_filtered=df_motor.copy()
        # Convert UY to string for filtering
        df_motor_filtered['UY'] = df_motor_filtered['UY'].astype(str)
        df_motor_filtered = df_motor_filtered[df_motor_filtered['UY'].isin([str(y) for y in selected_year])]
        # Group by the agent
        df_motor_summary = (
            df_motor_filtered
            .groupby(['Agency'], observed=False, as_index=False)
            .agg(
                GWP=('Premium_b4_GST', 'sum'),
                Claims=('Total_Incurred_Claim', 'sum'),
                Count=('polno', 'count'),
                Commission=('Commission','sum')
            )
        )
        df_motor_summary['Commission']=df_motor_summary['Commission'].abs()

        df_motor_summary['Loss Ratio']=df_motor_summary['Claims']/df_motor_summary['GWP']
        df_motor_summary['Commission Per Policy']=df_motor_summary['Commission']/df_motor_summary['Count']

        # Build bar chart for Commission
        fig = go.Figure()

        fig.add_trace(go.Bar(
            x=df_motor_summary['Agency'],
            y=df_motor_summary['Commission'],
            name="Total Commission",
            text=df_motor_summary['Commission'],
            texttemplate='$%{text:,.0f}',
            marker_color='#1E90FF',
            textposition="inside",
            textfont=dict(color="black"),
            hovertemplate="%{x}<br>Commission: $%{y:,.0f}<extra></extra>"
        ))


        fig.add_trace(go.Scatter(
            x=df_motor_summary['Agency'],
            y=df_motor_summary['Loss Ratio'],
            name="Loss Ratio",
            mode='lines+markers+text',
            text=df_motor_summary["Loss Ratio"].map(lambda x: f"{x:.0%}"),  
            textfont=dict(color="red"),
            textposition="top center", 
            line=dict(color='red', width=2),
            yaxis="y2",
            hovertemplate="UW Year: %{x}<br>Loss Ratio: %{y:.1%}"
        ))

        fig.update_layout(
            title=dict(text="Commission and Loss Ratio by Agency", font=dict(size=13)),
            xaxis=dict(title="Agency", showgrid=False),
            yaxis=dict(
                title=dict(text="Commission", font=dict(color="black")),
                tickfont=dict(color="black"),
                showgrid=False
            ),
            yaxis2=dict(
                title=dict(text="Loss Ratio", font=dict(color="red")),
                overlaying="y",
                side="right",
                tickformat=".0%",
                tickfont=dict(color="red"),
                showgrid=False,
                zeroline=False
            ),
            legend=dict(x=0.8, y=1.2, bgcolor="rgba(0,0,0,0)")
        )
   
        return fig
    

    @app.callback(
        Output('agency-commission-chart2', 'figure'),
        Input('Year_button6', 'value'),
        Input('Commission-info_button','value')
    )

    def avgcomm_chart9(selected_year,selected_commission):
        df_motor_filtered=df_motor.copy()
        df_motor_filtered['UY'] = df_motor_filtered['UY'].astype(str)
        df_motor_filtered = df_motor_filtered[df_motor_filtered['UY'].isin(selected_year)]
        df_motor_filtered = df_motor_filtered[df_motor_filtered['trantype'].isin(['N', 'R'])]

        # Group by UY and selected risk factor
        df_motor_filtered = (
            df_motor_filtered
            .groupby('Agency', observed=False)
            .agg(
                Total_Premium=('Premium_b4_GST', 'sum'),
                Total_Commission=('Commission', 'sum'),
                Total_Incurred_Claim=('Total_Incurred_Claim', 'sum'),
                Count=('polno', 'count') 
            )
            .reset_index()
        )

        # Compute Average Commission
        df_motor_filtered['AvgComm'] = df_motor_filtered['Total_Commission'].abs() / df_motor_filtered['Count']
        df_motor_filtered['CommRate'] = df_motor_filtered['Total_Commission'].abs() / df_motor_filtered['Total_Premium']


        # Plot
        fig = go.Figure()

        if selected_commission == 'AvgComm':
            fig1=fig.add_trace(go.Bar(
                x=df_motor_filtered['Agency'],
                y=df_motor_filtered['AvgComm'],
                name="Average Commission",
                text=df_motor_filtered['AvgComm'],
                texttemplate='$%{text:,.0f}',  # More appropriate formatting for currency
                textposition="inside",
                textfont=dict(color="black"),
                hovertemplate="Agency: %{x}<br>Average Commission: $%{y:,.0f}<extra></extra>"
            ))

            fig1.update_layout(
                title=dict(text="Average Commission by Agency", font=dict(size=13)),
                xaxis=dict(title="Agency", showgrid=False),
                yaxis=dict(
                    title=dict(text="Average Commission", font=dict(color="blue")),
                    tickfont=dict(color="blue"),
                    showgrid=False
                ),
                legend=dict(x=0.8, y=1.2, bgcolor="rgba(0,0,0,0)")  
            )

            return fig1
        
        elif selected_commission == 'CommRate':
             
            fig2=fig.add_trace(go.Scatter(
                x=df_motor_filtered['Agency'],
                y=df_motor_filtered['CommRate'],
                name="Commission Rate",
                text=[f"{val:.2%}" for val in df_motor_filtered['CommRate']],
                mode="lines+markers+text",
                textposition="top center",
                textfont=dict(color="black"),
                hovertemplate="Agency: %{x}<br>Commission Rate: %{y:,.1%}<extra></extra>"
            ))

            fig2.update_layout(
                title=dict(text="Commission Rate by Agency", font=dict(size=13)),
                xaxis=dict(title="Agency", showgrid=False),
                yaxis=dict(
                    title=dict(text="Commission Rate", font=dict(color="blue")),
                    tickfont=dict(color="blue"),
                    showgrid=False
                ),
                legend=dict(x=0.8, y=1.2, bgcolor="rgba(0,0,0,0)")  
            )
            return fig2
    
    
    @app.callback(
        [Output('freq-chart10', 'figure'),
        Output('sev-chart10', 'figure')],
        [Input('Scheme_button3', 'value'),
        Input('Year_button8', 'value'),
        Input('RiskFactor_button2', 'value')]
    )

    def freqsev_chart10(selected_scheme,selected_year, selected_factor):
        df_summary_filtered=df_summary.copy()
        df_summary_filtered['UY'] = df_summary_filtered['UY'].astype(str)
        df_summary_filtered = df_summary_filtered[df_summary_filtered['Scheme'].isin(selected_scheme)]
        df_summary_filtered = df_summary_filtered[df_summary_filtered['UY'].isin(selected_year)]
        df_summary_filtered = df_summary_filtered.groupby(["file_date", selected_factor], observed=False).agg({
            "Total_Incurred_Claim_sum": "sum",
            "No_Claims_sum": "sum",
            "PolNo_count":"sum"
        }).reset_index()

        df_summary_filtered["Severity"] =  df_summary_filtered["Total_Incurred_Claim_sum"] /  df_summary_filtered["No_Claims_sum"]
        df_summary_filtered["Frequency"] =  df_summary_filtered["No_Claims_sum"] /  df_summary_filtered["PolNo_count"]

        try:
             df_summary_filtered["file_date_dt"] = pd.to_datetime( df_summary_filtered["file_date"], format="%m-%Y")
             df_summary_filtered = df_summary_filtered.sort_values("file_date_dt")
        except:
            pass  # Ignore if datetime or sorting not needed

        fig_sev = px.line(
            df_summary_filtered,
            x="file_date",
            y="Severity",
            title="Monthly Severity",
            markers=True,
            color=selected_factor,
            labels={"file_date": "Month", "Severity": "Severity"},
            text="Severity",  # still fine for hover/labels
            category_orders=category_orders
        )

        fig_sev.update_layout(
            yaxis=dict(
                tickformat=",0",  # thousands separator, no decimals
            ),
            xaxis_title=None
        )

        fig_sev.update_traces(
            texttemplate="%{y:,.0f}",   # use y, format with commas, no decimals
            textposition="top center",
            hovertemplate=(
                "Month: %{x}<br>"           # show x-axis value (file_date)
                + "Severity: %{y:,.0f}<br>" # formatted y value with commas, no decimals
                + "<extra></extra>"         # remove trace name from hover box
            )
        )


        fig_freq = px.line(
            df_summary_filtered,
            x="file_date",
            y="Frequency",
            title="Monthly Frequency",
            markers=True,
            color=selected_factor,
            labels={"file_date": "Month", "Frequency": "Frequency"},
            text="Frequency",  # still fine for hover/labels
            category_orders=category_orders
        )

        fig_freq.update_layout(
            yaxis=dict(
                tickformat=".0%",  # thousands separator, no decimals
            ),
            xaxis_title=None
        )

        fig_freq.update_traces(
            texttemplate="%{y:,.0%}",   # use y, format with commas, no decimals
            textposition="top center",
            hovertemplate=(
                "Month: %{x}<br>"           # show x-axis value (file_date)
                + "Frequency: %{y:,.1%}<br>" # formatted y value with commas, no decimals
                + "<extra></extra>"         # remove trace name from hover box
            )
        )
        return fig_freq, fig_sev 
    
    @app.callback(
        Output('tabs-content-graph', 'children'),
        [
            Input('tabs-freqsev', 'value'),
            Input('Scheme_button3', 'value'),
            Input('Year_button8', 'value'),
            Input('RiskFactor_button2', 'value')
        ]
    )
    def render_content(tab, selected_scheme, selected_year, selected_factor):
        # Call your helper with the 3 inputs
        fig_freq, fig_sev = freqsev_chart10(selected_scheme, selected_year, selected_factor)

        if tab == 'tab-1-freq-chart10':
            return dcc.Graph(figure=fig_freq)
        elif tab == 'tab-1-sev-chart10':
            return dcc.Graph(figure=fig_sev)
         
def get_layout():
    return motor_app

if __name__ == '__main__':
    app = dash.Dash(__name__,suppress_callback_exceptions=True,meta_tags=[{"name": "viewport", "content": "width=device-width"}])
    app.layout = get_layout()
    register_motor_callbacks(app)  
    app.run(debug=True, port=8050)
